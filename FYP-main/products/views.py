from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count  # <--- Added Count here
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from customers.models import NegotiatedOrder
from .models import Product, Category
from .forms import ProductForm, NegotiationOfferForm
from .models import ProductNegotiation, ProductNegotiationOffer
from services.llama_service import negotiate_price
from products.models import ProductNegotiation, ProductNegotiationOffer
from django.utils import timezone

# Public View: List all products
def product_list_view(request):
    products = Product.objects.filter(is_available=True)
    
    # FIX: Annotate category with the count of AVAILABLE products only
    categories = Category.objects.annotate(
        items_count=Count('products', filter=Q(products__is_available=True))
    ).all()

    # Search
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )

    # Category Filter
    selected_categories = request.GET.getlist('category')
    if selected_categories:
        products = products.filter(category__slug__in=selected_categories)

    # Price Range Filter
    price_range = request.GET.get('price_range')
    if price_range:
        if '-' in price_range:
            if 'plus' in price_range:
                min_price = int(price_range.split('-')[0])
                products = products.filter(price__gte=min_price)
            else:
                min_price, max_price = map(int, price_range.split('-'))
                products = products.filter(price__gte=min_price, price__lte=max_price)

    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by == 'price':
        products = products.order_by('price')
    elif sort_by == '-price':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    products_data = []
    for p in page_obj:
        image_url = p.main_image.url if getattr(p, 'main_image', None) and bool(p.main_image) else ''
        price_val = float(p.get_discount_price())
        rating_val = float(p.rating or 0)

        products_data.append(
            {
                'id': p.id,
                'name': p.name,
                'price': price_val,
                'rating': rating_val,
                'image': image_url,
            }
        )

    context = {
        'products': page_obj,
        'categories': categories,
        'selected_categories': selected_categories,
        'total_count': products.count(),
        'products_data': products_data,
    }
    return render(request, 'products/list.html', context)

# ... (keep the rest of your views the same)


def product_detail_view(request, slug):
    """
    Display detailed view of a single product with recommendations
    """
    from services.recommendation_service import get_recommendations_for_user, get_recommendations_for_guest

    product = get_object_or_404(
        Product.objects.select_related('category', 'seller'),
        slug=slug,
        is_available=True
    )
    
    # Related products from same category (existing logic — keep this)
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:4]

    # Personalized recommendations
    if request.user.is_authenticated:
        recommended_products = get_recommendations_for_user(request.user, limit=4)
        recommendation_label = 'Recommended For You'
    else:
        recommended_products = get_recommendations_for_guest(limit=4)
        recommendation_label = 'You May Also Like'

    # Exclude the current product from recommendations
    recommended_products = [p for p in recommended_products if p.id != product.id]
    
    # Reviews
    reviews = product.reviews.all().select_related('user')[:10]
    
    context = {
        'product': product,
        'related_products': related_products,
        'recommended_products': recommended_products,
        'recommendation_label': recommendation_label,
        'reviews': reviews,
    }
    
    return render(request, 'products/detail.html', context)


@login_required
def negotiate_view(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('category', 'seller'),
        slug=slug,
        is_available=True,
    )

    if request.user == product.seller:
        messages.error(request, 'You cannot negotiate on your own product.')
        return redirect('products:detail', slug=product.slug)

    negotiation, _created = ProductNegotiation.objects.get_or_create(
        product=product,
        buyer=request.user,
        defaults={'status': ProductNegotiation.STATUS_OPEN},
    )

    offers_qs = negotiation.offers.all()
    attempts = offers_qs.count()

    try:
        min_price = (product.price * (Decimal('1') - Decimal(str(settings.MAX_NEGOTIATION_DISCOUNT))))
    except Exception:
        min_price = product.price

    min_price = min_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    listed_price = Decimal(str(product.price)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    form = NegotiationOfferForm()

    if request.method == 'POST':
        form = NegotiationOfferForm(request.POST)
        if form.is_valid():
            if negotiation.status != ProductNegotiation.STATUS_OPEN:
                return redirect('products:negotiate', slug=product.slug)

            attempts = negotiation.offers.count()
            if attempts >= int(getattr(settings, 'MAX_NEGOTIATION_ATTEMPTS', 3)):
                return redirect('products:negotiate', slug=product.slug)

            offer = form.cleaned_data['offer']
            offer = Decimal(str(offer)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            decision = None
            counter_price = None
            raw_ai_output = ''

            hard_reject_threshold = (min_price * Decimal('0.7')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            if offer >= listed_price:
                decision = ProductNegotiationOffer.DECISION_ACCEPT
            elif offer < hard_reject_threshold:
                decision = ProductNegotiationOffer.DECISION_REJECT
            elif offer < min_price:
                decision = ProductNegotiationOffer.DECISION_COUNTER
                counter_price = min_price
            else:
                result = negotiate_price(
                    product_price=listed_price,
                    min_price=min_price,
                    offer=offer,
                )
                decision = result.get('decision')
                counter_price = result.get('counter_price')
                raw_ai_output = result.get('raw_output') or ''

            if decision == ProductNegotiationOffer.DECISION_ACCEPT:
                if offer < min_price:
                    decision = ProductNegotiationOffer.DECISION_COUNTER
                    counter_price = min_price
            elif decision == ProductNegotiationOffer.DECISION_COUNTER:
                try:
                    counter_price = Decimal(str(counter_price)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                except (InvalidOperation, TypeError):
                    counter_price = ((offer + listed_price) / 2).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                if counter_price < min_price:
                    counter_price = min_price
                if counter_price > listed_price:
                    counter_price = listed_price
            elif decision != ProductNegotiationOffer.DECISION_REJECT:
                decision = ProductNegotiationOffer.DECISION_COUNTER
                counter_price = ((offer + listed_price) / 2).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                if counter_price < min_price:
                    counter_price = min_price
                if counter_price > listed_price:
                    counter_price = listed_price

            ProductNegotiationOffer.objects.create(
                negotiation=negotiation,
                offer_price=offer,
                decision=decision,
                counter_price=counter_price,
                raw_ai_output=raw_ai_output,
            )

            if decision == ProductNegotiationOffer.DECISION_ACCEPT:
                negotiation.status = ProductNegotiation.STATUS_ACCEPTED
                negotiation.save(update_fields=['status', 'updated_at'])

                pending = NegotiatedOrder.objects.filter(
                    buyer=request.user,
                    product=product,
                    status=NegotiatedOrder.STATUS_PENDING,
                ).order_by('-created_at').first()

                if pending and pending.expires_at and pending.expires_at <= timezone.now():
                    pending.status = NegotiatedOrder.STATUS_CANCELLED
                    pending.save(update_fields=['status'])
                    pending = None

                if pending and pending.negotiated_price != offer:
                    pending.status = NegotiatedOrder.STATUS_CANCELLED
                    pending.save(update_fields=['status'])
                    pending = None

                if not pending:
                    pending = NegotiatedOrder.objects.create(
                        buyer=request.user,
                        product=product,
                        negotiated_price=offer,
                        status=NegotiatedOrder.STATUS_PENDING,
                    )

                return redirect('checkout_with_negotiation', order_id=pending.id)

            elif decision == ProductNegotiationOffer.DECISION_REJECT:
                # Only permanently close the negotiation if all attempts are exhausted
                attempts_after = negotiation.offers.count()
                max_attempts = int(getattr(settings, 'MAX_NEGOTIATION_ATTEMPTS', 3))

                if attempts_after >= max_attempts:
                    negotiation.status = ProductNegotiation.STATUS_REJECTED
                    negotiation.save(update_fields=['status', 'updated_at'])
                else:
                    negotiation.save(update_fields=['updated_at'])
            else:
                negotiation.save(update_fields=['updated_at'])

            return redirect('products:negotiate', slug=product.slug)

        return redirect('products:negotiate', slug=product.slug)

    offers = offers_qs
    latest_offer = offers.last()

    negotiated_order = None
    if negotiation.status == ProductNegotiation.STATUS_ACCEPTED:
        negotiated_order = NegotiatedOrder.objects.filter(
            buyer=request.user,
            product=product,
            status=NegotiatedOrder.STATUS_PENDING,
        ).order_by('-created_at').first()

    form_disabled = False
    if negotiation.status != ProductNegotiation.STATUS_OPEN:
        form_disabled = True
    if attempts >= int(getattr(settings, 'MAX_NEGOTIATION_ATTEMPTS', 3)):
        form_disabled = True

    context = {
        'product': product,
        'negotiation': negotiation,
        'min_price': min_price,
        'listed_price': listed_price,
        'attempts': attempts,
        'max_attempts': int(getattr(settings, 'MAX_NEGOTIATION_ATTEMPTS', 3)),
        'offers': offers,
        'latest_offer': latest_offer,
        'negotiated_order': negotiated_order,
        'form': form,
        'form_disabled': form_disabled,
    }
    return render(request, 'products/negotiate.html', context)


@login_required
def product_create_view(request):
    """
    Create a new product (seller only)
    """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                product = form.save(commit=False)
                product.seller = request.user
                product.save()
                messages.success(request, f'Product "{product.name}" created successfully!')
                return redirect('sellers:dashboard')
            except Exception as e:
                messages.error(request, f'Error creating product: {e}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Create Product',
        'action': 'Create'
    }
    return render(request, 'products/form.html', context)


@login_required
def product_update_view(request, pk):
    """
    Update an existing product (seller only - own products)
    """
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        
        if form.is_valid():
            try:
                updated_product = form.save()
                messages.success(request, f'Product "{updated_product.name}" updated successfully!')
                return redirect('sellers:dashboard')
            except Exception as e:
                messages.error(request, f'Error updating product: {e}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'title': f'Edit {product.name}',
        'action': 'Update'
    }
    return render(request, 'products/form.html', context)


@login_required
def product_delete_view(request, pk):
    """
    Delete a product (seller only - own products)
    """
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    
    if request.method == 'POST':
        product_name = product.name
        try:
            product.delete()
            messages.success(request, f'Product "{product_name}" deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting product: {e}')
        
        return redirect('sellers:dashboard')
    
    context = {
        'product': product,
    }
    return render(request, 'products/delete_confirm.html', context)


@login_required
def product_toggle_availability_view(request, pk):
    """
    Toggle product availability (seller only - own products)
    """
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    
    try:
        product.is_available = not product.is_available
        product.save()
        status = "available" if product.is_available else "unavailable"
        messages.success(request, f'Product "{product.name}" is now {status}!')
    except Exception as e:
        messages.error(request, f'Error updating product: {e}')

    return redirect('sellers:dashboard')
