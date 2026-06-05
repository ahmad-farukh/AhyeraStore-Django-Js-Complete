from django.contrib import admin
# Remove Order and OrderItem from imports
from .models import SellerProfile, Message

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'city', 'rating', 'total_sales', 'is_active']
    list_filter = ['is_active', 'city', 'created_at']
    search_fields = ['business_name', 'user__username', 'email', 'phone']
    readonly_fields = ['rating', 'total_sales', 'total_revenue', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User & Business', {
            'fields': ('user', 'business_name', 'business_description', 'business_logo')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'address', 'city')
        }),
        ('Business Details', {
            'fields': ('tax_id', 'bank_account')
        }),
        ('Stats & Status', {
            'fields': ('rating', 'total_sales', 'total_revenue', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

# DELETED OrderAdmin and OrderItemAdmin

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'recipient__username', 'subject', 'message']
    readonly_fields = ['created_at']