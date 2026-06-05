from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Product List (browse/search products)
    path('', views.product_list_view, name='list'),
    
    # Product Management (Seller Only)
    path('create/', views.product_create_view, name='create'),
    path('<int:pk>/update/', views.product_update_view, name='update'),
    path('<int:pk>/delete/', views.product_delete_view, name='delete'),
    path('<int:pk>/toggle/', views.product_toggle_availability_view, name='toggle_availability'),

    # Product Detail (view single product)
    path('<slug:slug>/negotiate/', views.negotiate_view, name='negotiate'),
    path('<slug:slug>/', views.product_detail_view, name='detail'),
]