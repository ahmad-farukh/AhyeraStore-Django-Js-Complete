from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    # Homepage
    path('', views.home, name='home'),  # Changed from home_view to home
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    
    # Addresses
    path('addresses/', views.address_list, name='addresses'),
    path('addresses/add/', views.address_add, name='address_add'),
    path('addresses/<int:pk>/delete/', views.address_delete, name='address_delete'),
    
    # Orders
    path('orders/', views.order_list, name='orders'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/conversation/', views.order_conversation_redirect, name='order_conversation'),
    path('orders/<int:pk>/chat/', views.order_chat_view, name='order_chat'),
    
    # Messages
    path('messages/', views.messages_view, name='messages'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<int:product_id>/', views.wishlist_remove, name='wishlist_remove'),
    
    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    
    # Checkout
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/negotiation/<int:order_id>/', views.checkout_with_negotiation, name='checkout_with_negotiation'),
    
    # AI Features
    path('ai-search/', views.ai_search_view, name='ai_search'),
    path('ai-search/image/', views.ai_image_search, name='ai_image_search'),
    path('ai-chatbot/', views.ai_chatbot_view, name='ai_chatbot'),
]