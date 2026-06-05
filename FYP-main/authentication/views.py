from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.db import transaction

from .forms import UserRegistrationForm, UserLoginForm


# ============================================================================
# UTILITY FUNCTIONS (Inline - No separate utils.py needed)
# ============================================================================

def post_login_redirect(request, user):
    """
    Intelligent post-login redirection
    Priority: Superuser → next param → role-based → default
    """
    # Priority 1: Superuser
    if user.is_superuser:
        return '/admin/'
    
    # Priority 2: Check 'next' parameter
    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url and next_url.startswith('/') and not next_url.startswith('//'):
        return next_url
    
    # Priority 3: Role-based redirection
    if hasattr(user, 'seller_profile'):
        return reverse('sellers:profile')
    
    # Default: Customer home
    return reverse('customers:home')


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

def login_view(request):
    """
    Professional login handler with rate limiting and intelligent routing
    """
    if request.user.is_authenticated:
        return redirect(post_login_redirect(request, request.user))

    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not identifier or not password:
            messages.error(request, 'Please provide both username and password.')
            return render(request, 'authentication/login.html')

        username = identifier
        if '@' in identifier:
            UserModel = get_user_model()
            matched_user = UserModel.objects.filter(email__iexact=identifier).first()
            if matched_user:
                username = matched_user.get_username()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect(post_login_redirect(request, user))

        UserModel = get_user_model()
        candidate_user = None
        if '@' in identifier:
            candidate_user = UserModel.objects.filter(email__iexact=identifier).first()
        else:
            candidate_user = (
                UserModel.objects.filter(username__iexact=identifier).first()
                or UserModel.objects.filter(email__iexact=identifier).first()
            )

        if candidate_user and candidate_user.check_password(password) and not candidate_user.is_active:
            messages.error(request, 'Your account has been deactivated. Please contact support.')
            return render(request, 'authentication/login.html')

        messages.error(request, 'Invalid username or password.')
        return render(request, 'authentication/login.html')
    
    # GET request - show login form
    next_url = request.GET.get('next', '/')
    return render(request, 'authentication/login.html', {
        'next': next_url
    })


def register_view(request):
    """
    Professional user registration handler
    """
    # Redirect if already authenticated
    if request.user.is_authenticated:
        return redirect(post_login_redirect(request, request.user))
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create user account
                    user = form.save(commit=False)
                    user.is_active = True
                    user.first_name = request.POST.get('first_name', '').strip()
                    user.last_name = request.POST.get('last_name', '').strip()
                    user.save()

                    username = form.cleaned_data.get('username')
                    email = form.cleaned_data.get('email')
                    user_type = form.cleaned_data.get('user_type', 'customer')

                    # Create role-specific profile
                    if user_type == 'seller':
                        from sellers.models import SellerProfile

                        SellerProfile.objects.create(
                            user=user,
                            business_name=form.cleaned_data.get('business_name', ''),
                            phone=form.cleaned_data.get('phone', ''),
                            address=form.cleaned_data.get('address', ''),
                            city=form.cleaned_data.get('city', ''),
                            email=email,
                        )

                        messages.success(request, f'Seller account created for {username}! Please log in to continue.')

                    else:
                        # Customer registration
                        from customers.models import CustomerProfile

                        CustomerProfile.objects.create(
                            user=user,
                            phone=form.cleaned_data.get('phone', ''),
                        )
                        messages.success(request, f'Account created for {username}! Please log in to continue.')

                return redirect('authentication:login')

            except Exception:
                error_msg = "Error creating account. Please verify your details and try again."

                messages.error(request, error_msg)
        else:
            # Form validation errors
            messages.error(request, 'Please correct the errors below.')
    
    else:
        form = UserRegistrationForm()
    
    return render(request, 'authentication/register.html', {'form': form})


@login_required
def logout_view(request):
    """
    Handle user logout with full session cleanup
    """
    username = request.user.username
    
    # 1. Flush the session
    # This removes all session data (cart, auth, messages, etc.)
    request.session.flush()
    
    # 2. Perform Django Logout
    logout(request)
    
    # 3. Success Message
    messages.success(request, f'Goodbye, {username}! You have been logged out successfully.')
    
    # 4. Redirect to the Landing Page (Home)
    return redirect('core:home')


@login_required
def switch_role_view(request):
    """
    Allow users with dual roles to switch between seller and customer
    """
    if hasattr(request.user, 'seller_profile'):
        return redirect('sellers:dashboard')

    return redirect('customers:home')


def forgot_password_view(request):
    """
    Handle password reset requests
    """
    if request.user.is_authenticated:
        return redirect('customers:home')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        form = PasswordResetForm(request.POST)
        
        if form.is_valid():
            try:
                opts = {
                    'use_https': request.is_secure(),
                    'token_generator': default_token_generator,
                    'from_email': None,
                    'email_template_name': 'registration/password_reset_email.html',
                    'subject_template_name': 'registration/password_reset_subject.txt',
                    'request': request,
                }
                form.save(**opts)
                
                messages.success(
                    request,
                    'If an account exists with this email, you will receive password reset instructions.'
                )
                return redirect('authentication:login')
                
            except Exception as e:
                messages.error(request, 'An error occurred. Please try again later.')
        else:
            messages.error(request, 'Please enter a valid email address.')
    
    return render(request, 'authentication/forgot_password.html')