from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
import re


class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration
    """
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('seller', 'Seller'),
    ]
    
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, widget=forms.RadioSelect, initial='customer')
    email = forms.EmailField(required=True)
    
    # Seller specific fields
    business_name = forms.CharField(required=False)
    phone = forms.CharField(required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    city = forms.CharField(required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        
        if user_type == 'seller':
            if not cleaned_data.get('business_name'):
                self.add_error('business_name', 'Business Name is required for sellers.')
            if not cleaned_data.get('phone'):
                self.add_error('phone', 'Phone number is required for sellers.')
            if not cleaned_data.get('address'):
                self.add_error('address', 'Address is required for sellers.')
            if not cleaned_data.get('city'):
                self.add_error('city', 'City is required for sellers.')
                
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,4}$', email):
            raise forms.ValidationError('Enter a valid email address e.g. name@example.com')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username.isalpha():
            raise forms.ValidationError('Username can only contain letters, no numbers or special characters.')
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match. Please make sure both passwords are identical.')

        if password2:
            if len(password2) < 8:
                raise forms.ValidationError('Password is too short. It must be at least 8 characters long.')
            if not any(c.isdigit() for c in password2):
                raise forms.ValidationError('Password must contain at least one number (0-9).')
            if not any(c.isupper() for c in password2):
                raise forms.ValidationError('Password must contain at least one uppercase letter (A-Z).')
            if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?/~`' for c in password2):
                raise forms.ValidationError('Password must contain at least one special character e.g. !@#$%^&*')

        return password2


class UserLoginForm(AuthenticationForm):
    """
    Form for user login
    """
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
