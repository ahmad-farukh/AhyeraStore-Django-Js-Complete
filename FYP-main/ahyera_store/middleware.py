from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from urllib.parse import urlencode

class RoleAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Public paths that don't require authentication or role checks
        self.public_paths = [
            '/auth/',
            '/admin/',
            '/static/',
            '/media/',
        ]
        self.protected_prefixes = [
            '/sellers/',
            '/customers/',
        ]

    def __call__(self, request):
        # Allow public paths
        if any(request.path.startswith(path) for path in self.public_paths):
            return self.get_response(request)

        # Check if user is authenticated
        if not request.user.is_authenticated:
            if any(request.path.startswith(prefix) for prefix in self.protected_prefixes):
                login_url = '/auth/login/'
                next_url = request.get_full_path()
                if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                    next_url = '/'
                return redirect(f"{login_url}?{urlencode({'next': next_url})}")

            return self.get_response(request)

        # User is authenticated, determine role
        if request.user.is_superuser:
            request.user.role = 'superuser'
        else:
            request.user.role = 'seller' if hasattr(request.user, 'seller_profile') else 'customer'

            # Enforce access control
            path = request.path
            
            # Block /sellers/ for non-sellers (except superusers)
            if path.startswith('/sellers/') and request.user.role != 'seller' and request.user.role != 'superuser':
                return render(request, '403.html', status=403)
            
            # Block /customers/ for non-customers (if we want to be strict, but usually customers are the default)
            # The requirement says: "Blocks access to: /customers/* URLs if user is not a customer"
            # Sellers might also be customers in some systems, but here the roles seem distinct.
            # However, a seller might want to buy something? 
            # For now, let's strictly follow the requirement.
            if path.startswith('/customers/') and request.user.role != 'customer' and request.user.role != 'superuser':
                 return render(request, '403.html', status=403)

        response = self.get_response(request)
        return response
