from django.contrib import admin
from .models import CustomerProfile, ShippingAddress, Cart, CartItem, Wishlist, Order, OrderItem


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'newsletter_subscribed', 'created_at']
    list_filter = ['newsletter_subscribed', 'sms_notifications', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'full_name', 'city', 'state', 'is_default', 'created_at']
    list_filter = ['is_default', 'city', 'state', 'country']
    search_fields = ['customer__username', 'full_name', 'phone', 'city', 'postal_code']
    readonly_fields = ['created_at', 'updated_at']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['added_at', 'updated_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['customer', 'get_total_items', 'get_total', 'created_at', 'updated_at']
    search_fields = ['customer__username', 'customer__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Total Items'
    
    def get_total(self, obj):
        return f'Rs. {obj.get_total():.2f}'
    get_total.short_description = 'Total'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'get_total_price', 'added_at']
    list_filter = ['added_at']
    search_fields = ['cart__customer__username', 'product__name']
    readonly_fields = ['added_at', 'updated_at']
    
    def get_total_price(self, obj):
        return f'Rs. {obj.get_total_price():.2f}'
    get_total_price.short_description = 'Total Price'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'added_at']
    list_filter = ['added_at']
    search_fields = ['customer__username', 'product__name']
    readonly_fields = ['added_at']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_sku', 'price', 'quantity', 'subtotal', 'created_at']
    fk_name = 'order'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'status', 'payment_status', 'total', 'created_at']
    list_filter = ['status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'customer__username', 'customer__email', 'shipping_full_name']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'delivered_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'status', 'payment_status', 'payment_method')
        }),
        ('Shipping Details', {
            'fields': (
                'shipping_address',
                'shipping_full_name',
                'shipping_phone',
                'shipping_address_line_1',
                'shipping_address_line_2',
                'shipping_city',
                'shipping_state',
                'shipping_postal_code',
                'shipping_country',
            )
        }),
        ('Pricing', {
            'fields': ('subtotal', 'shipping_cost', 'tax', 'discount', 'total')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'delivered_at')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'quantity', 'price', 'subtotal', 'is_fulfilled']
    list_filter = ['is_fulfilled', 'created_at']
    search_fields = ['order__order_number', 'product_name', 'product_sku']
    readonly_fields = ['product_name', 'product_sku', 'subtotal', 'created_at', 'fulfilled_at']
