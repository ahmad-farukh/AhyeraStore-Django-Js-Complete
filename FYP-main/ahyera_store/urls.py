# ahyera_store/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from customers import views as customer_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),      # authentication:login
    path('sellers/', include('sellers.urls')),          # sellers:profile
    path('customers/', include('customers.urls')),      # customers:home
    path('products/', include('products.urls')),        # products:list
    path('checkout/negotiation/<int:order_id>/', customer_views.checkout_with_negotiation, name='checkout_with_negotiation'),
    path('', include('core.urls')),                     # core:landing (if exists)
]

# Static and Media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)