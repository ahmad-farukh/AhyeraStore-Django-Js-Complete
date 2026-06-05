from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from urllib.parse import urlencode
from django.contrib.auth.models import User
from django.utils.http import url_has_allowed_host_and_scheme
from products.models import Product, Category
from .models import SellerProfile, Order
from products.forms import ProductForm


@login_required
def dashboard_view(request):
    """
    Seller dashboard with overview statistics
    """
    try:
        seller_profile = request.user.seller_profile
    except SellerProfile.DoesNotExist:
        messages.warning(request, 'Please complete your seller profile first.')
        return redirect('sellers:profile')
    
    # Get seller's products
    products_list = Product.objects.filter(seller=request.user).select_related('category')

    # Filtering
    category_slug = request.GET.get('category')
    stock_status = request.GET.get('stock')
    
    if category_slug:
        products_list = products_list.filter(category__slug=category_slug)
    
    if stock_status == 'out_of_stock':
        products_list = products_list.filter(stock=0)
    elif stock_status == 'low_stock':
        products_list = products_list.filter(stock__gt=0, stock__lte=10)
    elif stock_status == 'active':
        products_list = products_list.filter(is_available=True)
    elif stock_status == 'inactive':
        products_list = products_list.filter(is_available=False)

    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by == 'price_asc':
        products_list = products_list.order_by('price')
    elif sort_by == 'price_desc':
        products_list = products_list.order_by('-price')
    elif sort_by == 'stock_asc':
        products_list = products_list.order_by('stock')
    elif sort_by == 'stock_desc':
        products_list = products_list.order_by('-stock')
    elif sort_by == 'date_asc':
        products_list = products_list.order_by('created_at')
    else: # date_desc or default
        products_list = products_list.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products_list, 12) # Show 12 products per page
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    # Get seller's orders (seller isolation via OrderItem -> Product.seller)
    orders = (
        Order.objects.filter(items__product__seller=request.user)
        .distinct()
        .order_by('-created_at')[:10]
    )
    
    # Calculate product statistics (using base query for accurate stats)
    all_products = Product.objects.filter(seller=request.user)
    total_products = all_products.count()
    active_products = all_products.filter(is_available=True).count()
    low_stock = all_products.filter(stock__gt=0, stock__lte=10).count()  # 1-10 items
    out_of_stock = all_products.filter(stock=0).count()
    
    # Calculate order statistics
    total_orders = Order.objects.filter(items__product__seller=request.user).distinct().count()
    pending_orders = Order.objects.filter(items__product__seller=request.user, status='pending').distinct().count()
    total_revenue = seller_profile.total_revenue
    
    # Get all categories for filter dropdown
    categories = Category.objects.filter(products__seller=request.user).distinct()

    context = {
        'seller_profile': seller_profile,
        'products': products,
        'orders': orders,
        'total_products': total_products,
        'active_products': active_products,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'categories': categories,
        'current_category': category_slug,
        'current_stock': stock_status,
        'current_sort': sort_by,
    }
    
    return render(request, 'sellers/dashboard.html', context)


@login_required
def orders_view(request):
    """
    View all seller orders
    """
    orders = (
        Order.objects.filter(items__product__seller=request.user)
        .select_related('customer')
        .prefetch_related('items', 'items__product')
        .distinct()
        .order_by('-created_at')
    )
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)

    orders_data = []
    for order in orders:
        seller_items = [
            item for item in order.items.all()
            if item.product and item.product.seller_id == request.user.id
        ]

        seller_total = sum(float(item.subtotal) for item in seller_items)

        orders_data.append({
            'id': order.id,
            'order_number': order.order_number,
            'status': order.status,
            'total': seller_total,
            'created_at': order.created_at.strftime('%Y-%m-%d'),
            'customer': {
                'id': order.customer_id,
                'name': order.shipping_full_name or order.customer.get_full_name() or order.customer.username,
                'phone': order.shipping_phone or '',
                'email': order.customer.email or '',
                'address': ', '.join(
                    part for part in [
                        order.shipping_address_line_1,
                        order.shipping_address_line_2,
                        order.shipping_city,
                        order.shipping_state,
                        order.shipping_postal_code,
                        order.shipping_country,
                    ]
                    if part
                ),
            },
            'items': [
                {
                    'title': item.product_name,
                    'qty': item.quantity,
                    'subtotal': float(item.subtotal),
                }
                for item in seller_items
            ],
        })
    
    context = {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'orders_data': orders_data,
    }
    
    return render(request, 'sellers/orders.html', context)


@login_required
@require_POST
def order_status_update_view(request, order_id):
    """Update a seller order's status with strict seller isolation."""
    new_status = request.POST.get('status', '').strip()
    allowed_statuses = {key for key, _label in Order.STATUS_CHOICES}
    if new_status not in allowed_statuses:
        return JsonResponse({'success': False, 'error': 'Invalid status.'}, status=400)

    order = (
        Order.objects.filter(id=order_id, items__product__seller=request.user)
        .distinct()
        .first()
    )
    if not order:
        return JsonResponse({'success': False, 'error': 'Order not found.'}, status=404)

    order.status = new_status
    order.save(update_fields=['status', 'updated_at'])
    return JsonResponse({'success': True, 'status': order.status})


@login_required
def order_conversation_redirect(request, order_id):
    order = (
        Order.objects.filter(
            pk=order_id,
        )
        .filter(Q(seller=request.user) | Q(items__product__seller=request.user))
        .select_related('customer')
        .distinct()
        .first()
    )
    if not order:
        messages.error(request, 'Order not found.')
        return redirect('sellers:orders')

    query = urlencode({'user_id': order.customer_id, 'order_id': order.pk})
    return redirect(f"{reverse('sellers:messages')}?{query}")


@login_required
def profile_view(request):
    """
    View and manage seller profile - handles both display and creation/editing
    """
    try:
        seller_profile = request.user.seller_profile
        is_new = False
    except SellerProfile.DoesNotExist:
        seller_profile = None
        is_new = True
    
    # Check if user wants to edit their profile
    show_form = is_new or request.GET.get('edit') == 'true' or request.method == 'POST'
    
    if request.method == 'POST':
        from .forms import SellerProfileForm
        
        if seller_profile:
            # Update existing profile
            form = SellerProfileForm(request.POST, request.FILES, instance=seller_profile)
        else:
            # Create new profile
            form = SellerProfileForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                
                if is_new:
                    messages.success(request, 'Seller profile created successfully! Welcome to Ahyera Store.')
                else:
                    messages.success(request, 'Profile updated successfully!')
                
                return redirect('sellers:profile')
            except Exception as e:
                messages.error(request, f'Error saving profile: {str(e)}')
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        from .forms import SellerProfileForm
        
        if show_form:
            # Show form for creating or editing
            if seller_profile:
                form = SellerProfileForm(instance=seller_profile)
            else:
                # Pre-fill with user's email if available
                initial_data = {'email': request.user.email} if request.user.email else {}
                form = SellerProfileForm(initial=initial_data)
        else:
            form = None
    
    context = {
        'seller_profile': seller_profile,
        'form': form,
        'is_new': is_new,
    }
    
    return render(request, 'sellers/profile.html', context)


@login_required
def add_product_view(request):
    """
    Add a new product to the seller's inventory
    """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                product = form.save(commit=False)
                product.seller = request.user
                product.save()
                messages.success(request, f'Product "{product.name}" added successfully!')
                return redirect('sellers:dashboard')
            except Exception as e:
                messages.error(request, f'Error saving product: {str(e)}')
        else:
            # Log form errors for debugging
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Add Product'
    }
    return render(request, 'sellers/add_product.html', context)


@login_required
def edit_product_view(request, pk):
    """
    Edit an existing product
    """
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Product "{product.name}" updated successfully!')
                return redirect('sellers:dashboard')
            except Exception as e:
                messages.error(request, f'Error updating product: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'title': f'Edit {product.name}'
    }
    return render(request, 'sellers/add_product.html', context)


@login_required
def bulk_delete_products_view(request):
    """
    Bulk delete products
    """
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')
        if product_ids:
            # Filter by IDs and ensure they belong to the current user
            products_to_delete = Product.objects.filter(id__in=product_ids, seller=request.user)
            deleted_count = products_to_delete.count()
            products_to_delete.delete()
            
            if deleted_count > 0:
                messages.success(request, f'Successfully deleted {deleted_count} product(s).')
            else:
                messages.warning(request, 'No valid products found to delete.')
        else:
            messages.warning(request, 'No products selected for deletion.')
            
    return redirect('sellers:dashboard')


@login_required
def messages_view(request):
    """
    View seller messages
    """
    from .models import Message

    return_url = request.GET.get('return_url')
    back_url = None
    if return_url and url_has_allowed_host_and_scheme(
        url=return_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        back_url = return_url

    if not back_url and request.GET.get('user_id'):
        back_url = reverse('sellers:messages')

    if not back_url:
        ref = request.META.get('HTTP_REFERER')
        if ref and url_has_allowed_host_and_scheme(
            url=ref,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            messages_base = request.build_absolute_uri(reverse('sellers:messages'))
            if ref.startswith(messages_base):
                back_url = reverse('sellers:messages')
            else:
                back_url = ref

    if not back_url:
        back_url = reverse('sellers:dashboard')

    order_id = request.GET.get('order_id')
    selected_order_id = None
    if order_id:
        try:
            selected_order_id = int(order_id)
        except (TypeError, ValueError):
            selected_order_id = None
    
    allowed_partner_ids = set(
        Order.objects.filter(seller=request.user).values_list('customer_id', flat=True)
    )

    message_partner_ids = set(
        Message.objects.filter(Q(sender=request.user) | Q(recipient=request.user))
        .values_list('sender_id', 'recipient_id')
        .distinct()
    )
    partner_ids = set()
    for sender_id, recipient_id in message_partner_ids:
        if sender_id and sender_id != request.user.id:
            partner_ids.add(sender_id)
        if recipient_id and recipient_id != request.user.id:
            partner_ids.add(recipient_id)

    if partner_ids:
        customer_partner_ids = set(
            User.objects.filter(id__in=partner_ids, seller_profile__isnull=True)
            .values_list('id', flat=True)
        )
        allowed_partner_ids.update(customer_partner_ids)
    
    # Handle sending new message
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        message_text = request.POST.get('message')
        
        if recipient_id and message_text:
            try:
                if int(recipient_id) not in allowed_partner_ids:
                    messages.error(request, 'You are not allowed to message this user.')
                    return redirect('sellers:messages')

                recipient = User.objects.get(id=recipient_id)
                if hasattr(recipient, 'seller_profile'):
                    messages.error(request, 'You can only message customers.')
                    return redirect('sellers:messages')

                linked_order = None
                if selected_order_id:
                    linked_order = (
                        Order.objects.filter(
                            pk=selected_order_id,
                            seller=request.user,
                            customer=recipient,
                        )
                        .first()
                    )
                if not linked_order:
                    linked_order = (
                        Order.objects.filter(seller=request.user, customer=recipient)
                        .order_by('-created_at')
                        .first()
                    )

                Message.objects.create(
                    sender=request.user,
                    recipient=recipient,
                    message=message_text,
                    subject=f"Message from {request.user.username}",
                    order=linked_order,
                )
                messages.success(request, 'Message sent successfully!')
                query = {'user_id': recipient_id}
                if selected_order_id:
                    query['order_id'] = selected_order_id
                if back_url:
                    query['return_url'] = back_url
                return redirect(f"{request.path}?{urlencode(query)}")
            except Exception as e:
                messages.error(request, f'Error sending message: {str(e)}')
    
    # Get all messages involving the user
    all_messages = Message.objects.filter(
        Q(sender=request.user, recipient_id__in=allowed_partner_ids)
        | Q(recipient=request.user, sender_id__in=allowed_partner_ids)
    ).select_related('sender', 'recipient')
    
    # Group by conversation partner
    conversations = {}
    for msg in all_messages:
        partner = msg.recipient if msg.sender == request.user else msg.sender
        if partner.id not in conversations:
            conversations[partner.id] = {
                'partner': partner,
                'last_message': msg,
                'unread_count': 0
            }
        else:
            # Update last message if this one is newer (though query is ordered by date, better to be safe)
            if msg.created_at > conversations[partner.id]['last_message'].created_at:
                conversations[partner.id]['last_message'] = msg
        
        if msg.recipient == request.user and not msg.is_read:
            conversations[partner.id]['unread_count'] += 1
            
    # Convert to list and sort by last message date
    conversations_list = sorted(
        conversations.values(), 
        key=lambda x: x['last_message'].created_at, 
        reverse=True
    )
    
    # Get selected conversation
    selected_user_id = request.GET.get('user_id')
    selected_conversation = None
    chat_messages = []
    
    if selected_user_id:
        try:
            selected_user_id = int(selected_user_id)
            if selected_user_id not in allowed_partner_ids:
                messages.error(request, 'You are not allowed to view this conversation.')
                return redirect('sellers:messages')

            chat_messages = all_messages.filter(
                Q(sender__id=selected_user_id) | Q(recipient__id=selected_user_id)
            )
            if selected_order_id:
                order_ok = Order.objects.filter(
                    pk=selected_order_id,
                    seller=request.user,
                    customer_id=selected_user_id,
                ).exists()
                if not order_ok:
                    messages.error(request, 'You are not allowed to view this order conversation.')
                    return redirect('sellers:messages')

                chat_messages = chat_messages.filter(order_id=selected_order_id)

            chat_messages = chat_messages.order_by('created_at')
            
            # Mark as read
            chat_messages.filter(recipient=request.user, is_read=False).update(is_read=True)
            
            selected_conversation = User.objects.get(id=selected_user_id)
        except (ValueError, User.DoesNotExist):
            pass
            
    # Total unread count
    total_unread = all_messages.filter(recipient=request.user, is_read=False).count()
    
    context = {
        'conversations': conversations_list,
        'selected_conversation': selected_conversation,
        'chat_messages': chat_messages,
        'total_unread': total_unread,
        'back_url': back_url,
    }
    
    return render(request, 'sellers/messages.html', context)


@login_required
def delivery_view(request):
    """
    Manage delivery settings
    """
    try:
        seller_profile = request.user.seller_profile
    except SellerProfile.DoesNotExist:
        messages.warning(request, 'Please complete your seller profile first.')
        return redirect('sellers:profile')
    
    # Handle settings update
    if request.method == 'POST':
        city = request.POST.get('city')
        radius = request.POST.get('radius')
        
        if city and radius:
            try:
                seller_profile.city = city
                seller_profile.delivery_radius = int(radius)
                seller_profile.save()
                messages.success(request, 'Delivery settings updated successfully!')
            except ValueError:
                messages.error(request, 'Invalid radius value.')
            except Exception as e:
                messages.error(request, f'Error saving settings: {str(e)}')
        
        return redirect('sellers:delivery')
    
    # Get delivery statistics
    from django.db.models import Count, Q
    
    orders = Order.objects.filter(seller=request.user)
    
    delivery_stats = {
        'total_deliveries': orders.filter(status='delivered').count(),
        'in_transit': orders.filter(status='shipped').count(),
        'pending_shipment': orders.filter(status__in=['confirmed', 'processing']).count(),
        'delivery_rate': 0,
    }
    
    total_completed = orders.filter(status__in=['delivered', 'cancelled', 'refunded']).count()
    if total_completed > 0:
        delivery_stats['delivery_rate'] = (delivery_stats['total_deliveries'] / total_completed) * 100

    cities = {
        'Lahore': {'lat': 31.5204, 'lng': 74.3587},
        'Karachi': {'lat': 24.8607, 'lng': 67.0011},
        'Islamabad': {'lat': 33.6844, 'lng': 73.0479},
        'Faisalabad': {'lat': 31.4504, 'lng': 73.1350},
        'Multan': {'lat': 30.1575, 'lng': 71.5249},
        'Sahiwal': {'lat': 30.6680, 'lng': 73.1113},
        'Sialkot': {'lat': 32.4945, 'lng': 74.5229},
        'Gujranwala': {'lat': 32.1877, 'lng': 74.1945},
        'Rawalpindi': {'lat': 33.5651, 'lng': 73.0169},
        'Peshawar': {'lat': 34.0151, 'lng': 71.5249},
    }
    
    context = {
        'seller_profile': seller_profile,
        'delivery_stats': delivery_stats,
        'recent_orders': orders.filter(status='shipped')[:10],
        'delivery_cities': cities,
    }
    
    return render(request, 'sellers/delivery.html', context)


@login_required
def sales_graph_view(request):
    """
    View sales analytics and graphs
    """
    from django.db.models import Sum, Count, Avg
    from django.db.models.functions import TruncDate, TruncMonth
    from datetime import datetime, timedelta
    from customers.models import OrderItem
    
    # Get date range from request or default to last 30 days
    days = int(request.GET.get('days', 30))
    start_date = datetime.now() - timedelta(days=days)
    
    seller_items = OrderItem.objects.filter(
        product__seller=request.user,
        order__created_at__gte=start_date
    )

    daily_sales = (
        seller_items.annotate(date=TruncDate('order__created_at'))
        .values('date')
        .annotate(total_sales=Sum('subtotal'))
        .order_by('date')
    )

    monthly_sales = (
        seller_items.annotate(month=TruncMonth('order__created_at'))
        .values('month')
        .annotate(total_sales=Sum('subtotal'))
        .order_by('month')
    )

    total_revenue = seller_items.aggregate(total=Sum('subtotal'))['total'] or 0
    total_orders = seller_items.values('order_id').distinct().count()
    average_order_value = (total_revenue / total_orders) if total_orders else 0
    units_sold = seller_items.aggregate(total=Sum('quantity'))['total'] or 0

    stats = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'average_order_value': average_order_value,
        'units_sold': units_sold,
    }

    top_products = seller_items.values('product__name').annotate(
        quantity_sold=Sum('quantity'),
        revenue=Sum('subtotal')
    ).order_by('-quantity_sold')[:5]

    low_stock_products = Product.objects.filter(
        seller=request.user,
        stock__gt=0,
        stock__lte=10,
    ).order_by('stock')[:5]
    
    context = {
        'daily_sales': list(daily_sales),
        'monthly_sales': list(monthly_sales),
        'stats': stats,
        'top_products': list(top_products),
        'low_stock_products': low_stock_products,
        'days': days,
    }
    
    return render(request, 'sellers/sales_graph.html', context)


@login_required
def payment_view(request):
    """
    Manage payment and payouts
    """
    from django.db.models import Sum, Q
    
    try:
        seller_profile = request.user.seller_profile
    except SellerProfile.DoesNotExist:
        messages.warning(request, 'Please complete your seller profile first.')
        return redirect('sellers:profile')
    
    # Get payment statistics
    orders = Order.objects.filter(seller=request.user)
    
    payment_stats = {
        'total_earnings': seller_profile.total_revenue,
        'pending_payments': orders.filter(payment_status='pending').aggregate(total=Sum('total'))['total'] or 0,
        'paid_orders': orders.filter(payment_status='paid').aggregate(total=Sum('total'))['total'] or 0,
        'failed_payments': orders.filter(payment_status='failed').count(),
        'pending_count': orders.filter(payment_status='pending').count(),
    }
    
    # Recent transactions (paid orders)
    recent_transactions = orders.filter(payment_status='paid').order_by('-created_at')[:10]
    
    context = {
        'seller_profile': seller_profile,
        'payment_stats': payment_stats,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'sellers/payment.html', context)


@login_required
def product_preview_view(request, pk):
    """
    Seller-side preview of their own product.
    Does NOT require is_available=True so draft/inactive products are also visible.
    Only accessible by the seller who owns the product.
    """
    from products.models import Product
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    context = {
        'product': product,
    }
    return render(request, 'sellers/product_preview.html', context)


