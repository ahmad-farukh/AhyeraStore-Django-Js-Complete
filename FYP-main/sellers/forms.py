from django import forms
from .models import SellerProfile
import re


class SellerProfileForm(forms.ModelForm):
    """
    Form for creating and updating seller profiles
    """
    class Meta:
        model = SellerProfile
        fields = [
            'business_name',
            'business_description',
            'business_logo',
            'phone',
            'email',
            'address',
            'city',
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter your business name'
            }),
            'business_description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Describe your business...',
                'rows': 4
            }),
            'business_logo': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'e.g., +92 300 1234567'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'your.email@example.com'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Full business address',
                'rows': 3
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'City'
            }),
        }
        labels = {
            'business_name': 'Business Name',
            'business_description': 'Business Description',
            'business_logo': 'Business Logo',
            'phone': 'Phone Number',
            'email': 'Business Email',
            'address': 'Business Address',
            'city': 'City',
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not re.match(r'^(\+92|0)\d{10}$', phone.replace(' ', '').replace('-', '')):
            raise forms.ValidationError('Enter a valid Pakistani number e.g. 03001234567')
        return phone
