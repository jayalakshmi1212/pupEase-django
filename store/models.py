from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q

class Offer(models.Model):
    name = models.CharField(max_length=100, verbose_name='Offer Name')
    offer_on = models.CharField(max_length=20, choices=[('product', 'Product'), ('category', 'Category')], verbose_name='Offer On', default='product')
    discount = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Discount')
    maximum_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Maximum Amount', null=True, blank=True)
    starts_at = models.DateTimeField(default=timezone.now, verbose_name='Offer Starts at')
    ends_at = models.DateTimeField(default=timezone.now, verbose_name='Offer Ends at')
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('inactive', 'Inactive')], verbose_name='Status', default='active')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True, related_name='offers', verbose_name='Product')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True, related_name='offers', verbose_name='Category')

    def __str__(self):
        return self.name
    
    def activate(self):
        self.is_active = True
        self.save()

    def deactivate(self):
        self.is_active = False
        self.save()

    def delete(self, *args, **kwargs):
        # Reset product prices before deleting the offer
        offer_product_associations = OfferProductAssociation.objects.filter(offer=self)
        for association in offer_product_associations:
            product = association.product
            product.price = product.original_price  # Assuming original price is stored in 'original_price' field
            product.save()
        super().delete(*args, **kwargs)

class OfferProductAssociation(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True, default='Uncategorized')
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
   

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.category_name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store_app:products_by_category', args=[self.slug])

    def __str__(self):
        return self.category_name


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
  
    stock = models.IntegerField()
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_date=models.DateField(default=timezone.now)
    modified_date=models.DateField(auto_now=True)
    description= models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    def clean(self):
        if not self.image:
            raise ValidationError('Image selection is mandatory.')

        # Call the parent class's clean method
        super().clean()
        
    @property
    def discounted_price(self):
        active_offers = OfferProductAssociation.objects.filter(
            Q(product=self) | Q(category=self.category),
            offer__status='active'
        ).distinct()

        if active_offers:
            max_discount = max(offer.offer.discount for offer in active_offers)
            return self.price * (1 - (max_discount / 100))
        else:
            return self.price  # Default to regular price if no active offers


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile",default=None)
    username = models.CharField(max_length=30,null = True)
    email=models.EmailField(max_length=100,null=False)
    phone_number = models.IntegerField(null=True)
   
    def __str__(self):
        return self.user.username

class Addresses(models.Model):
    COUNTRY_CHOICES = [('IN', 'India')]  # Add more countries if needed
    STATE_CHOICES = [
        ('Andhra Pradesh', 'Andhra Pradesh'),
        ('Arunachal Pradesh', 'Arunachal Pradesh'),
        ('Assam', 'Assam'),
        ('Bihar', 'Bihar'),
        ('Chhattisgarh', 'Chhattisgarh'),
        ('Goa', 'Goa'),
        ('Gujarat', 'Gujarat'),
        ('Haryana', 'Haryana'),
        ('Himachal Pradesh', 'Himachal Pradesh'),
        ('Jharkhand', 'Jharkhand'),
        ('Karnataka', 'Karnataka'),
        ('Kerala', 'Kerala'),
        ('Madhya Pradesh', 'Madhya Pradesh'),
        ('Maharashtra', 'Maharashtra'),
        ('Manipur', 'Manipur'),
        ('Meghalaya', 'Meghalaya'),
        ('Mizoram', 'Mizoram'),
        ('Nagaland', 'Nagaland'),
        ('Odisha', 'Odisha'),
        ('Punjab', 'Punjab'),
        ('Rajasthan', 'Rajasthan'),
        ('Sikkim', 'Sikkim'),
        ('Tamil Nadu', 'Tamil Nadu'),
        ('Telangana', 'Telangana'),
        ('Tripura', 'Tripura'),
        ('Uttar Pradesh', 'Uttar Pradesh'),
        ('Uttarakhand', 'Uttarakhand'),
        ('West Bengal', 'West Bengal'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=20)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50,blank=True,null=True)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, default='IN')
    state = models.CharField(max_length=50, choices=STATE_CHOICES)
    pincode = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)    
    
    
    def save(self, *args, **kwargs):
        if self.is_default:
            Addresses.objects.filter(user = self.user).exclude(pk=self.pk).update(is_default=False)
        super(Addresses, self).save(*args, **kwargs)
        
    def get_user_full_address(self):
        address_parts = f"{self.name}, {self.phone_number}, {self.address_line_1}"
        
        if self.address_line_2:
            address_parts += (', '+self.address_line_2)
        
        address_parts += (f", Pin: {self.pincode}, {self.city}, {self.state}, India")
        
        
        return address_parts
        # return f'{self.name},{self.phone},Pin:{self.pincode},Address:{self.address_line_1},{self.address_line_2},{self.city},{self.state},{self.country}'
    
    def __str__(self):
        return self.name  
    



class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)