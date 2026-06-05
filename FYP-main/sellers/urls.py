# sellers/urls.py
from django.urls import path
from . import views

app_name = 'sellers'

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('orders/', views.orders_view, name='orders'),
    path('orders/<int:order_id>/status/', views.order_status_update_view, name='order_status_update'),
    path('orders/<int:order_id>/conversation/', views.order_conversation_redirect, name='order_conversation'),
    path('messages/', views.messages_view, name='messages'),
    path('delivery/', views.delivery_view, name='delivery'),
    path('payment/', views.payment_view, name='payment'),
    path('sales-graph/', views.sales_graph_view, name='sales_graph'),
    
    # Product Management
    path('add-product/', views.add_product_view, name='add_product'),
    path('edit-product/<int:pk>/', views.edit_product_view, name='edit_product'), # Added this
    path('product-preview/<int:pk>/', views.product_preview_view, name='product_preview'),
    path('bulk-delete/', views.bulk_delete_products_view, name='bulk_delete_products'), # Added this (FIX)
]