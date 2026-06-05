from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q  
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from urllib.parse import urlencode
import logging
import json
from .models import CustomerProfile, ShippingAddress, Cart, CartItem, Wishlist, Order, OrderItem, NegotiatedOrder
from products.models import ProductNegotiation, ProductNegotiationOffer
from products.models import Product, Category
from django.contrib.auth.models import User
from django.db import transaction
from sellers.models import Message

logger = logging.getLogger(__name__)

def home(request):
    """
    Customer homepage with all products and personalized recommendations
    """
    from services.recommendation_service import get_recommendations_for_user, get_recommendations_for_guest

    # Main product list
    products = Product.objects.filter(is_available=True).order_by('-created_at')
    
    # Personalized recommendations
    if request.user.is_authenticated:
        recommended_products = get_recommendations_for_user(request.user, limit=6)
        recommendation_label = 'Recommended For You'
    else:
        recommended_products = get_recommendations_for_guest(limit=6)
        recommendation_label = 'Trending Products'

    # Keep existing ai_products for backward compatibility (used by carousel)
    ai_products = Product.objects.filter(is_available=True, ai_recommended=True).order_by('-created_at')[:6]
    
    # Categories for sidebar with product count (Using Q object)
    categories = Category.objects.filter(is_active=True).annotate(
        items_count=Count('products', filter=Q(products__is_available=True))
    )

    unread_messages_count = 0
    if request.user.is_authenticated:
        unread_messages_count = Message.objects.filter(
            recipient=request.user,
            is_read=False,
        ).count()
    
    context = {
        'products': products,
        'ai_products': ai_products,
        'recommended_products': recommended_products,
        'recommendation_label': recommendation_label,
        'categories': categories,
        'unread_messages_count': unread_messages_count,
    }
    return render(request, 'customers/home.html', context)

@login_required
def dashboard(request):
    """
    Customer dashboard view
    """
    # Ensure customer profile exists
    CustomerProfile.objects.get_or_create(user=request.user)
    
    # Get recent orders
    recent_orders = Order.objects.filter(customer=request.user).order_by('-created_at')[:5]
    
    # Get stats
    total_spent = Order.objects.filter(customer=request.user).aggregate(Sum('total'))['total__sum'] or 0
    orders_count = Order.objects.filter(customer=request.user).count()
    
    context = {
        'recent_orders': recent_orders,
        'total_spent': total_spent,
        'orders_count': orders_count,
    }
    return render(request, 'customers/dashboard.html', context)

@login_required
def profile_view(request):
    """
    View customer profile
    """
    profile, created = CustomerProfile.objects.get_or_create(user=request.user)
    
    # Calculate stats
    total_spent = Order.objects.filter(customer=request.user).aggregate(Sum('total'))['total__sum'] or 0
    orders_count = Order.objects.filter(customer=request.user).count()
    
    # Determine favorite category (Simplified placeholder)
    favorite_category = "General"
    favorite_category_count = 0
    
    context = {
        'profile': profile,
        'total_spent': total_spent,
        'orders_count': orders_count,
        'favorite_category': favorite_category,
        'favorite_category_count': favorite_category_count,
    }
    return render(request, 'customers/profile.html', context)

@login_required
def profile_update(request):
    """
    Update customer profile with Image Upload support
    """
    if request.method == 'POST':
        user = request.user
        profile, created = CustomerProfile.objects.get_or_create(user=user)
        
        # 1. Update User Model Fields (Name)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.save()
        
        # 2. Update Profile Fields (Phone)
        profile.phone = request.POST.get('phone', profile.phone)
        
        # 3. Handle Profile Image Upload
        if 'profile_image' in request.FILES:
            profile.profile_image = request.FILES['profile_image']
            
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('customers:profile')
    
    # If not POST, just redirect to profile view
    return redirect('customers:profile')

@login_required
def address_list(request):
    """
    List customer addresses
    """
    addresses = ShippingAddress.objects.filter(customer=request.user)
    return render(request, 'customers/addresses.html', {'addresses': addresses})

@login_required
def address_add(request):
    """
    Add new address
    """
    if request.method == 'POST':
        is_default = request.POST.get('is_default') == 'on'
        
        # If setting as default, unset others first
        if is_default:
            ShippingAddress.objects.filter(customer=request.user).update(is_default=False)

        ShippingAddress.objects.create(
            customer=request.user,
            full_name=request.POST.get('full_name'),
            phone=request.POST.get('phone'),
            address_line_1=request.POST.get('address_line_1'),
            city=request.POST.get('city'),
            is_default=is_default,
            state=request.POST.get('state', ''),
            postal_code=request.POST.get('postal_code', ''),
            country=request.POST.get('country', 'Pakistan')
        )
        messages.success(request, 'Address added successfully!')
        return redirect('customers:addresses')
    
    return redirect('customers:addresses')

@login_required
def address_delete(request, pk):
    """
    Delete address
    """
    address = get_object_or_404(ShippingAddress, pk=pk, customer=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully!')
    return redirect('customers:addresses')

@login_required
def order_list(request):
    """
    List customer orders
    """
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'customers/orders.html', {'orders': orders})

@login_required
def order_detail(request, pk):
    """
    View order details
    """
    order = get_object_or_404(Order, pk=pk, customer=request.user)
    return render(request, 'customers/orders.html', {'orders': [order], 'detail_view': True})

@login_required
def order_conversation_redirect(request, pk):
    order = get_object_or_404(Order, pk=pk, customer=request.user)
    if not order.seller_id:
        messages.error(request, 'This order does not have an associated seller.')
        return redirect('customers:orders')

    query = urlencode({'user_id': order.seller_id, 'order_id': order.pk})
    return redirect(f"{reverse('customers:messages')}?{query}")

@login_required
def order_chat_view(request, pk):
    order = get_object_or_404(Order, pk=pk, customer=request.user)
    if not order.seller_id:
        messages.error(request, 'This order does not have an associated seller.')
        return redirect('customers:orders')

    query = urlencode({'user_id': order.seller_id, 'order_id': order.pk})
    return redirect(f"{reverse('customers:messages')}?{query}")

@login_required
def wishlist_view(request):
    """
    View wishlist
    """
    wishlist_items = Wishlist.objects.filter(customer=request.user)
    return render(request, 'customers/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def wishlist_add(request, product_id):
    """
    Add product to wishlist
    """
    product = get_object_or_404(Product, pk=product_id)
    Wishlist.objects.get_or_create(customer=request.user, product=product)
    messages.success(request, f'{product.name} added to wishlist!')
    return redirect(request.META.get('HTTP_REFERER') or 'customers:wishlist')

@login_required
def wishlist_remove(request, product_id):
    """
    Remove product from wishlist
    """
    product = get_object_or_404(Product, pk=product_id)
    Wishlist.objects.filter(customer=request.user, product=product).delete()
    messages.success(request, f'{product.name} removed from wishlist!')
    return redirect('customers:wishlist')

@login_required
def cart_view(request):
    """
    View shopping cart
    """
    cart, created = Cart.objects.get_or_create(customer=request.user)
    return render(request, 'customers/cart.html', {'cart': cart})

@login_required
def cart_add(request, product_id):
    """
    Add product to cart
    """
    product = get_object_or_404(Product, pk=product_id)
    cart, created = Cart.objects.get_or_create(customer=request.user)
    
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect(request.META.get('HTTP_REFERER', 'customers:cart'))

@login_required
@require_POST
def cart_update(request, item_id):
    """
    Update cart item quantity via AJAX
    """
    try:
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__customer=request.user)
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found in cart'})

        data = json.loads(request.body)
        change = int(data.get('change', 0))
        
        new_quantity = cart_item.quantity + change
        
        if new_quantity <= 0:
            # Remove item if quantity reaches 0
            cart_item.delete()
            cart = Cart.objects.get(customer=request.user)
            return JsonResponse({
                'success': True,
                'removed': True,
                'cart_total': float(cart.get_total()),
                'cart_count': cart.get_total_items()
            })
        
        # Validate against stock
        if new_quantity > cart_item.product.stock:
            return JsonResponse({
                'success': False,
                'message': f'Only {cart_item.product.stock} items available in stock'
            })
        
        cart_item.quantity = new_quantity
        cart_item.save()
        
        cart = cart_item.cart
        return JsonResponse({
            'success': True,
            'removed': False,
            'quantity': cart_item.quantity,
            'item_total': float(cart_item.get_total_price()),
            'cart_total': float(cart.get_total()),
            'cart_count': cart.get_total_items(),
            'max_stock': cart_item.product.stock
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_POST
def cart_remove(request, item_id):
    """
    Remove item from cart via AJAX
    """
    try:
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__customer=request.user)
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found in cart'})

        cart_item.delete()
        
        cart = Cart.objects.get(customer=request.user)
        return JsonResponse({
            'success': True,
            'cart_total': float(cart.get_total()),
            'cart_count': cart.get_total_items()
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_POST
def cart_clear(request):
    """
    Clear all items from cart via AJAX
    """
    try:
        cart = Cart.objects.get(customer=request.user)
        cart.items.all().delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Cart cleared successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def checkout_view(request):
    cart, created = Cart.objects.get_or_create(customer=request.user)
    # Optimize query
    cart_items = cart.items.select_related('product', 'product__seller').all()
    addresses = ShippingAddress.objects.filter(customer=request.user)
    
    if request.method == 'POST':
        # 1. Get Payment Method
        payment_method = request.POST.get('payment_method', 'cod')
        
        # 2. Determine Shipping Address
        saved_address_id = request.POST.get('saved_address') # Changed from 'address_id' to match template
        shipping_address = None

        # Case A: User selected an existing address
        if saved_address_id:
            shipping_address = get_object_or_404(ShippingAddress, id=saved_address_id, customer=request.user)
        
        # Case B: User entered a NEW address
        else:
            # Extract new address data from form
            full_name = request.POST.get('full_name')
            phone = request.POST.get('phone')
            address_line_1 = request.POST.get('address_line_1')
            city = request.POST.get('city')
            state = request.POST.get('state')
            postal_code = request.POST.get('postal_code')
            country = request.POST.get('country', 'Pakistan')
            save_info = request.POST.get('save_address') == 'on' # Checkbox to save

            # Basic Validation
            if not all([full_name, phone, address_line_1, city]):
                messages.error(request, 'Please fill in all required address fields.')
                return redirect('customers:checkout')

            # Create the address object (we don't save it to DB yet unless requested)
            # However, for the Order foreign key, we usually need a saved object.
            # Strategy: Create a ShippingAddress record.
            
            shipping_address = ShippingAddress(
                customer=request.user,
                full_name=full_name,
                phone=phone,
                address_line_1=address_line_1,
                address_line_2=request.POST.get('address_line_2', ''),
                city=city,
                state=state,
                postal_code=postal_code,
                country=country,
                is_default=False
            )
            
            # If user checked "Save this address", save it permanently.
            # Otherwise, we still save it to link to the Order, but you might want to mark it hidden or 
            # just use it as a one-time record. For simplicity here, we save it.
            if save_info:
                shipping_address.save()
            else:
                # If we don't want to save it to the user's profile, we can still save it 
                # but maybe we need logic to hide it from their list? 
                # For now, let's save it so the ForeignKey works.
                shipping_address.save()

        if not cart_items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('customers:home')

        try:
            with transaction.atomic():
                # Group items by seller
                items_by_seller = {}
                for item in cart_items:
                    seller = item.product.seller
                    if seller not in items_by_seller:
                        items_by_seller[seller] = []
                    items_by_seller[seller].append(item)
                
                # Create one order per seller
                for seller, items in items_by_seller.items():
                    # Calculate totals
                    order_subtotal = sum(item.get_total_price() for item in items)
                    order_tax = 0 
                    order_total = order_subtotal + order_tax
                    
                    order = Order.objects.create(
                        customer=request.user,
                        seller=seller,
                        status='pending',
                        payment_method=payment_method,
                        shipping_address=shipping_address, # Links to the address object
                        # Snapshot the address details in case the address object changes/deletes later
                        shipping_full_name=shipping_address.full_name,
                        shipping_phone=shipping_address.phone,
                        shipping_address_line_1=shipping_address.address_line_1,
                        shipping_city=shipping_address.city,
                        shipping_state=shipping_address.state,
                        shipping_postal_code=shipping_address.postal_code,
                        shipping_country=shipping_address.country,
                        subtotal=order_subtotal,
                        total=order_total
                    )
                    
                    # Create Order Items
                    # Create Order Items and reduce stock
                    for item in items:
                        OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        product_name=item.product.name,
                        product_sku=item.product.sku,
                        product_image=item.product.main_image,
                        price=item.product.get_discount_price(),
                        quantity=item.quantity
                        )
                    # Reduce stock
                    item.product.stock = max(0, item.product.stock - item.quantity)
                    item.product.save(update_fields=['stock'])
                
                # Clear Cart
                cart.items.all().delete()
                
                messages.success(request, 'Order placed successfully!')
                return redirect('customers:orders')
                
        except Exception as e:
            messages.error(request, f'Error processing order: {str(e)}')
            return redirect('customers:checkout')
        
    return render(request, 'customers/checkout.html', {'cart': cart, 'addresses': addresses})

@login_required
def checkout_with_negotiation(request, order_id):
    negotiated_order = get_object_or_404(NegotiatedOrder.objects.select_related('product', 'product__seller'), pk=order_id)

    if negotiated_order.buyer != request.user:
        messages.error(request, 'You do not have access to this negotiated checkout.')
        return redirect('customers:home')

    if negotiated_order.status != NegotiatedOrder.STATUS_PENDING:
        messages.error(request, 'This negotiated order is no longer available.')
        return redirect('products:negotiate', slug=negotiated_order.product.slug)

    if negotiated_order.expires_at and negotiated_order.expires_at <= timezone.now():
        negotiated_order.status = NegotiatedOrder.STATUS_CANCELLED
        negotiated_order.save(update_fields=['status'])
        messages.error(request, 'This negotiated price has expired. Please negotiate again.')
        return redirect('products:negotiate', slug=negotiated_order.product.slug)

    product = negotiated_order.product
    addresses = ShippingAddress.objects.filter(customer=request.user)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'cod')

        saved_address_id = request.POST.get('saved_address')
        shipping_address = None

        if saved_address_id:
            shipping_address = get_object_or_404(ShippingAddress, id=saved_address_id, customer=request.user)
        else:
            full_name = request.POST.get('full_name')
            phone = request.POST.get('phone')
            address_line_1 = request.POST.get('address_line_1')
            city = request.POST.get('city')
            state = request.POST.get('state')
            postal_code = request.POST.get('postal_code')
            country = request.POST.get('country', 'Pakistan')
            save_info = request.POST.get('save_address') == 'on'

            if not all([full_name, phone, address_line_1, city]):
                messages.error(request, 'Please fill in all required address fields.')
                return redirect('checkout_with_negotiation', order_id=negotiated_order.id)

            shipping_address = ShippingAddress(
                customer=request.user,
                full_name=full_name,
                phone=phone,
                address_line_1=address_line_1,
                address_line_2=request.POST.get('address_line_2', ''),
                city=city,
                state=state,
                postal_code=postal_code,
                country=country,
                is_default=False,
            )

            if save_info:
                shipping_address.save()
            else:
                shipping_address.save()

        try:
            with transaction.atomic():
                refreshed = NegotiatedOrder.objects.select_for_update().get(pk=negotiated_order.pk)
                if refreshed.status != NegotiatedOrder.STATUS_PENDING:
                    messages.error(request, 'This negotiated order is no longer available.')
                    return redirect('products:negotiate', slug=product.slug)

                if refreshed.expires_at and refreshed.expires_at <= timezone.now():
                    refreshed.status = NegotiatedOrder.STATUS_CANCELLED
                    refreshed.save(update_fields=['status'])
                    messages.error(request, 'This negotiated price has expired. Please negotiate again.')
                    return redirect('products:negotiate', slug=product.slug)

                order_subtotal = refreshed.negotiated_price
                order_tax = 0
                order_total = order_subtotal + order_tax

                order = Order.objects.create(
                    customer=request.user,
                    seller=product.seller,
                    status='pending',
                    payment_method=payment_method,
                    shipping_address=shipping_address,
                    shipping_full_name=shipping_address.full_name,
                    shipping_phone=shipping_address.phone,
                    shipping_address_line_1=shipping_address.address_line_1,
                    shipping_city=shipping_address.city,
                    shipping_state=shipping_address.state,
                    shipping_postal_code=shipping_address.postal_code,
                    shipping_country=shipping_address.country,
                    subtotal=order_subtotal,
                    total=order_total,
                )

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_sku=product.sku,
                    product_image=product.main_image,
                    price=refreshed.negotiated_price,
                    quantity=1,
                )
                product.stock = max(0, product.stock - 1)
                product.save(update_fields=['stock'])
                refreshed.status = NegotiatedOrder.STATUS_COMPLETED
                refreshed.save(update_fields=['status'])

                messages.success(request, 'Order placed successfully!')
                return redirect('customers:orders')

        except Exception as e:
            messages.error(request, f'Error processing negotiated order: {str(e)}')
            return redirect('checkout_with_negotiation', order_id=negotiated_order.id)

    context = {
        'negotiated_order': negotiated_order,
        'product': product,
        'addresses': addresses,
    }
    return render(request, 'customers/checkout_negotiated.html', context)

@login_required
def messages_view(request):
    from sellers.models import Message

    order_id = request.GET.get('order_id')
    selected_order_id = None
    if order_id:
        try:
            selected_order_id = int(order_id)
        except (TypeError, ValueError):
            selected_order_id = None

    allowed_partner_ids = set(
        Order.objects.filter(customer=request.user)
        .exclude(seller__isnull=True)
        .values_list('seller_id', flat=True)
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
        seller_partner_ids = set(
            User.objects.filter(id__in=partner_ids, seller_profile__isnull=False)
            .values_list('id', flat=True)
        )
        allowed_partner_ids.update(seller_partner_ids)

    selected_user_id_param = request.GET.get('user_id')
    if selected_user_id_param:
        try:
            selected_user_id_int = int(selected_user_id_param)
        except (TypeError, ValueError):
            selected_user_id_int = None

        if selected_user_id_int:
            seller_exists = User.objects.filter(id=selected_user_id_int, seller_profile__isnull=False).exists()
            if seller_exists:
                allowed_partner_ids.add(selected_user_id_int)

    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        message_text = request.POST.get('message')

        if recipient_id and message_text:
            try:
                if int(recipient_id) not in allowed_partner_ids:
                    messages.error(request, 'You are not allowed to message this user.')
                    return redirect('customers:messages')

                recipient = User.objects.get(id=recipient_id)
                if not hasattr(recipient, 'seller_profile'):
                    messages.error(request, 'You can only message sellers.')
                    return redirect('customers:messages')

                linked_order = None
                if selected_order_id:
                    linked_order = (
                        Order.objects.filter(
                            pk=selected_order_id,
                            customer=request.user,
                            seller=recipient,
                        )
                        .first()
                    )
                if not linked_order:
                    linked_order = (
                        Order.objects.filter(customer=request.user, seller=recipient)
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
                return redirect(f"{request.path}?{urlencode(query)}")
            except Exception as e:
                messages.error(request, f'Error sending message: {str(e)}')

    all_messages = Message.objects.filter(
        Q(sender=request.user, recipient_id__in=allowed_partner_ids)
        | Q(recipient=request.user, sender_id__in=allowed_partner_ids)
    ).select_related('sender', 'recipient')

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
            if msg.created_at > conversations[partner.id]['last_message'].created_at:
                conversations[partner.id]['last_message'] = msg

        if msg.recipient == request.user and not msg.is_read:
            conversations[partner.id]['unread_count'] += 1

    conversations_list = sorted(
        conversations.values(),
        key=lambda x: x['last_message'].created_at,
        reverse=True
    )

    selected_user_id = request.GET.get('user_id')
    selected_conversation = None
    chat_messages = []

    if selected_user_id:
        try:
            selected_user_id = int(selected_user_id)
            if selected_user_id not in allowed_partner_ids:
                messages.error(request, 'You are not allowed to view this conversation.')
                return redirect('customers:messages')

            chat_messages = all_messages.filter(
                Q(sender__id=selected_user_id) | Q(recipient__id=selected_user_id)
            )
            if selected_order_id:
                order_ok = Order.objects.filter(
                    pk=selected_order_id,
                    customer=request.user,
                    seller_id=selected_user_id,
                ).exists()
                if not order_ok:
                    messages.error(request, 'You are not allowed to view this order conversation.')
                    return redirect('customers:messages')

                chat_messages = chat_messages.filter(order_id=selected_order_id)

            chat_messages = chat_messages.order_by('created_at')

            chat_messages.filter(recipient=request.user, is_read=False).update(is_read=True)

            selected_conversation = User.objects.get(id=selected_user_id)
        except (ValueError, User.DoesNotExist):
            pass

    total_unread = all_messages.filter(recipient=request.user, is_read=False).count()

    context = {
        'conversations': conversations_list,
        'selected_conversation': selected_conversation,
        'chat_messages': chat_messages,
        'total_unread': total_unread,
        'selected_order_id': selected_order_id,
    }

    return render(request, 'customers/messages.html', context)

def ai_search_view(request):
    """
    AI Search page
    """
    suggestions = list(
        Product.objects.filter(is_available=True)
        .order_by('-created_at')
        .values_list('name', flat=True)[:50]
    )
    visual_result_count = Product.objects.filter(is_available=True).count()
    return render(
        request,
        'customers/ai_search.html',
        {
            'suggestions': suggestions,
            'visual_result_count': visual_result_count,
        },
    )

def ai_image_search(request):
    if request.method != 'POST':
        return redirect('customers:ai_search')

    uploaded_file = request.FILES.get('search_image')
    if not uploaded_file:
        messages.error(request, 'Please upload an image to search.')
        return redirect('customers:ai_search')

    try:
        from PIL import Image as PILImage
        from services.visual_search_service import find_similar_products

        image = PILImage.open(uploaded_file).convert('RGB')
        matched_products, search_description = find_similar_products(image, top_k=6)

        show_google_fallback = len(matched_products) < 3

        suggestions = list(
            Product.objects.filter(is_available=True)
            .order_by('-created_at')
            .values_list('name', flat=True)[:50]
        )

        context = {
            'search_results': matched_products,
            'show_google_fallback': show_google_fallback,
            'is_visual_search': True,
            'visual_description': search_description,
            'suggestions': suggestions,
            'visual_result_count': len(matched_products),
        }
        return render(request, 'customers/ai_search.html', context)

    except Exception as e:
        logger.exception('Visual search failed: %s', e)
        messages.error(request, 'Could not process the image. Please try again.')
        return redirect('customers:ai_search')

def ai_chatbot_view(request):
    """
    AI Chatbot page
    """
    return render(request, 'customers/ai_chatbot.html')