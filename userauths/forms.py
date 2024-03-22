from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import User
from django.core.exceptions import ValidationError


class PhoneNumberField(forms.CharField):
    def validate(self, value):
        super().validate(value)
        if len(value) != 10:
            raise ValidationError('Phone number must be 10 digits long')
        if len(set(value)) == 1:
            raise ValidationError('Phone number cannot have all same digits')
        if value.isdigit() and len(set(value)) == 1:
            raise ValidationError('Phone number cannot contain only zeros')


class Usersignup(UserCreationForm):
    username=forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Username'}))
    email=forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'Email'}))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))
    password1=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password'}))
    password2=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Confirm password'}))
    class Meta:
        model=User
        fields=['username','email','phone_number']


    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        # Additional validation can be performed here if needed
        return phone_number


    