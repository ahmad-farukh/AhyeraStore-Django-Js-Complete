from django.shortcuts import render, redirect
from products.models import Product

def home_view(request):
    # 1. Handle Logged-In Users
    if request.user.is_authenticated:
        # If user is a seller, send to seller dashboard
        if hasattr(request.user, 'seller_profile'):
            return redirect('sellers:dashboard')
        # Otherwise, send to customer homepage (The main shopping feed)
        return redirect('customers:home')

    # 2. Handle Guest Users (Landing Page)
    # Fetch products for the landing page
    featured_products = Product.objects.filter(is_featured=True)[:4]
    latest_products = Product.objects.filter(is_available=True).order_by('-created_at')[:8]
    
    context = {
        'featured_products': featured_products,
        'latest_products': latest_products,
    }
    
    # Render 'home.html' where we put the Hero Section and AI Features
    return render(request, 'home.html', context)