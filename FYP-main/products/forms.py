from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):

    new_category = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-600 outline-none mt-2',
            'placeholder': 'Or type a new category name here...'
        }),
        label='Create New Category'
    )

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'stock', 'main_image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-600 outline-none',
                'placeholder': 'Enter product name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-600 outline-none',
                'placeholder': 'Describe your product',
                'rows': 4
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-600 outline-none',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-600 outline-none'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-600 outline-none',
                'placeholder': '0',
                'min': '0'
            }),
            'main_image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-600 outline-none',
                'accept': 'image/*'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        new_category = cleaned_data.get('new_category', '').strip()

        if not category and not new_category:
            raise forms.ValidationError(
                'Please select an existing category or enter a new category name.'
            )

        if new_category:
            category_obj, created = Category.objects.get_or_create(
                name=new_category,
                defaults={'name': new_category}
            )
            cleaned_data['category'] = category_obj

        return cleaned_data


class NegotiationOfferForm(forms.Form):
    offer = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-600 outline-none',
            'placeholder': 'Enter your offer price',
            'step': '0.01',
            'min': '0'
        })
    )