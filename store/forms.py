from django import forms
from .models import Category
from store.models import Product
from .models import UserProfile
from django.core import validators
import re
from .models import Addresses
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator,MinLengthValidator



class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description', 'is_active','image']



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'stock', 'image','is_active','description']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['username', 'phone_number', 'email']

    def clean_phone_number(self):
        phone_number = str(self.cleaned_data.get('phone_number'))  # Convert to string

        # Check if phone number consists of only zeros
        if all(char == '0' for char in phone_number):
            raise ValidationError("Phone number cannot consist of only zeros.", code='invalid')

        # Check if phone number contains only digits and has exactly 10 digits
        if not phone_number.isdigit() or len(phone_number) != 10:
            raise ValidationError("Phone number must be a 10-digit numeric value.", code='invalid')

        # Check if phone number contains repeating digits
        if len(set(phone_number)) == 1:
            raise ValidationError("Phone number cannot have all digits as the same number.", code='invalid')

        # Return the cleaned phone number
        return phone_number

    # Override the __init__ method to add CSS classes to form fields with errors
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            if self.errors.get(field_name):
                self.fields[field_name].widget.attrs['class'] = 'form-control is-invalid'
            else:
                self.fields[field_name].widget.attrs['class'] = 'form-control'

def validate_phone_number(value):
    if not value.strip().isdigit():
        raise ValidationError("Phone number should only contain digits.")
    if len(value.strip()) != 10:
        raise ValidationError("Phone number must be exactly 10 digits.")
    if value.strip().startswith('0'):
        raise ValidationError("Phone number should not start with '0'.")


class AddressForm(forms.ModelForm):
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'phone_number':
                field.validators.append(MaxLengthValidator(limit_value=10, message="Phone number must be exactly 10 digits."))
                field.validators.append(validate_phone_number)
        
    class Meta:
        model = Addresses
        exclude = ('user','is_default','is_active')  