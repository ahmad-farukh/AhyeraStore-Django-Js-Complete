from django.contrib import admin
from .models import Category, Product, ProductReview


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'is_available', 'rating', 'seller', 'created_at']
    list_filter = ['category', 'is_available', 'ai_recommended', 'is_trending', 'is_featured', 'created_at']
    search_fields = ['name', 'description', 'sku']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'is_available']
    readonly_fields = ['created_at', 'updated_at', 'rating', 'num_reviews']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'category', 'seller')
        }),
        ('Pricing', {
            'fields': ('price', 'original_price', 'discount_percentage')
        }),
        ('Inventory', {
            'fields': ('stock', 'is_available', 'sku', 'brand')
        }),
        ('Images', {
            'fields': ('main_image', 'image_2', 'image_3', 'image_4')
        }),
        ('AI & Features', {
            'fields': ('ai_recommended', 'is_trending', 'is_featured')
        }),
        ('Stats', {
            'fields': ('rating', 'num_reviews', 'created_at', 'updated_at')
        }),
    )


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'created_at']
    search_fields = ['product__name', 'user__username', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at']
