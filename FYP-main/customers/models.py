from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta


class CustomerProfile(models.Model):
    """
    Extended profile for customers
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Preferences
    newsletter_subscribed = models.BooleanField(default=False)
    sms_notifications = models.BooleanField(default=False)
    
    # Profile image
    profile_image = models.ImageField(upload_to='customers/profiles/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Customer Profile'
        verbose_name_plural = 'Customer Profiles'
    
    def __str__(self):
        return f'{self.user.username} Profile'


class ShippingAddress(models.Model):
    """
    Customer shipping addresses
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipping_addresses')
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address_line_1 = models.CharField(max_length=300)
    address_line_2 = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Pakistan')
    
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Shipping Address'
        verbose_name_plural = 'Shipping Addresses'
        ordering = ['-is_default', '-created_at']
    
    def save(self, *args, **kwargs):
        # If this is set as default, unset other default addresses
        if self.is_default:
            ShippingAddress.objects.filter(customer=self.customer, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.full_name} - {self.city}'


class Cart(models.Model):
    """
    Shopping cart for customers
    """
    customer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Shopping Cart'
        verbose_name_plural = 'Shopping Carts'
    
    def __str__(self):
        return f'{self.customer.username}\'s Cart'
    
    def get_total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    def get_subtotal(self):
        """Calculate cart subtotal"""
        return sum(item.get_total_price() for item in self.items.all())
    
    def get_total(self):
        """Calculate cart total (can add tax, shipping later)"""
        return self.get_subtotal()


class CartItem(models.Model):
    """
    Individual items in a shopping cart
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['cart', 'product']
        ordering = ['-added_at']
    
    def __str__(self):
        return f'{self.quantity}x {self.product.name}'
    
    def get_total_price(self):
        """Calculate total price for this cart item"""
        return self.product.get_discount_price() * self.quantity
    
    def clean(self):
        """Validate that quantity doesn't exceed stock"""
        from django.core.exceptions import ValidationError
        if self.quantity > self.product.stock:
            raise ValidationError(f'Only {self.product.stock} items available in stock.')


class Wishlist(models.Model):
    """
    Customer wishlist/favorites
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'
        unique_together = ['customer', 'product']
        ordering = ['-added_at']
    
    def __str__(self):
        return f'{self.customer.username} - {self.product.name}'


class Order(models.Model):
    """
    Customer orders
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
        ('wallet', 'Digital Wallet'),
    ]
    
    # Order identification
    order_number = models.CharField(max_length=50, unique=True, editable=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_orders')
    
    # ADDED: Link to Seller (Crucial for Multi-Vendor)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_orders', null=True, blank=True)
    
    # Order status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')
    
    # Shipping information
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True)
    shipping_full_name = models.CharField(max_length=200)
    shipping_phone = models.CharField(max_length=20)
    shipping_address_line_1 = models.CharField(max_length=300)
    shipping_address_line_2 = models.CharField(max_length=300, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100, default='Pakistan')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Notes
    customer_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['customer', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import random
            import string
            from django.utils import timezone
            timestamp = timezone.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.order_number = f'ORD-{timestamp}-{random_str}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'Order {self.order_number} - {self.customer.username}'
    
    def get_total_items(self):
        """Get total number of items in order"""
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    """
    Individual items in an order
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    
    # Product details (snapshot)
    product_name = models.CharField(max_length=300)
    product_sku = models.CharField(max_length=100)
    product_image = models.ImageField(upload_to='orders/', blank=True, null=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Fulfillment (Required by Admin to prevent crash)
    is_fulfilled = models.BooleanField(default=False)
    fulfilled_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        ordering = ['id']
    
    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity
        if self.product and not self.product_name:
            self.product_name = self.product.name
            self.product_sku = self.product.sku
            self.product_image = self.product.main_image
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.quantity}x {self.product_name}'


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='notifications')
    event_key = models.CharField(max_length=200, unique=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Notification for {self.user.username}'


def _negotiated_order_default_expires_at():
    return timezone.now() + timedelta(hours=24)

class NegotiatedOrder(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='negotiated_orders')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    negotiated_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    expires_at = models.DateTimeField(default=_negotiated_order_default_expires_at)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer} - {self.product} - {self.negotiated_price}"