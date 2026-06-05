from django.db import models
from django.contrib.auth.models import User
from products.models import Product
# Import Order from customers to use the single source of truth
from customers.models import Order

class SellerProfile(models.Model):
    """
    Extended profile for sellers
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    business_name = models.CharField(max_length=300)
    business_description = models.TextField(blank=True)
    business_logo = models.ImageField(upload_to='sellers/logos/', blank=True, null=True)
    
    # Contact information
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)

    delivery_radius = models.IntegerField(default=120, help_text="Delivery radius in km")
    
    # Business details
    tax_id = models.CharField(max_length=50, blank=True)
    bank_account = models.CharField(max_length=100, blank=True)
    
    # Ratings and stats
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_sales = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.business_name


class Message(models.Model):
    """
    Messages between customers and sellers
    """
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Now points to the Order model in customers app
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True, related_name='messages')
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.sender.username} → {self.recipient.username}: {self.subject}'