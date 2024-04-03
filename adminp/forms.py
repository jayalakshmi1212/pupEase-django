from django import forms
from store.models import  Category, Product


# class OfferForm(forms.ModelForm):
#     name = forms.CharField(label='Offer Name')
#     offer_on = forms.ChoiceField(label='Offer On', choices=[('product', 'Product'), ('category', 'Category')])
#     discount = forms.DecimalField(label='Discount')
#     starts_at = forms.DateTimeField(label='Offer Starts at')
#     ends_at = forms.DateTimeField(label='Offer Ends at')
#     status = forms.ChoiceField(label='Status', choices=[('active', 'Active'), ('inactive', 'Inactive')])

#     product = forms.ModelChoiceField(queryset=Product.objects.all(), required=False, label='Product')
#     category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, label='Category')
#     offered_product_category = forms.CharField(required=False, label='Offered Product/Category')

#     class Meta:
#         model = Offer
#         fields = ['name', 'offer_on', 'discount', 'starts_at', 'ends_at', 'product', 'category', 'status']
#         widgets = {
#             'starts_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
#             'ends_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         offer_on = cleaned_data.get('offer_on')
#         product = cleaned_data.get('product')
#         category = cleaned_data.get('category')
#         offered_product_category = cleaned_data.get('offered_product_category')

#         if offer_on == 'product' and not product:
#             self.add_error('product', 'Please select a product.')
#         elif offer_on == 'category' and not category:
#             self.add_error('category', 'Please select a category.')
#         elif not offered_product_category:
#             self.add_error('offered_product_category', 'This field is required.')

#         return cleaned_data