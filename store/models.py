from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator


############################------------------------category---------------------------#####################################

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True, default='Uncategorized')
    cat_discount = models.IntegerField( null=True, blank=True)
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


######################################---------------brand-----------------###########################################

class Brand(models.Model):
    brand_name  = models.CharField(max_length=50,unique=True)
    is_active   = models.BooleanField(default=True)

    def __str__(self):
        return self.brand_name
############################------------------------product---------------------------#####################################



class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    pro_discount = models.IntegerField(null=True, blank=True)
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
        # Calculate the discounted price based on the pro_discount percentage
        if self.pro_discount is not None:
            discount = Decimal(self.pro_discount) / 100
            discounted_price = self.price - (self.price * discount)
            return discounted_price
        else:
            return self.price
    
    @property
    def discount_percentage(self):
        # Calculate the discount percentage
        if self.pro_discount is not None:
            discount = Decimal(self.pro_discount) / 100
            return discount * 100
        else:
            return 0


class VariationManager(models.Manager):
    def weight(self):
        return super(VariationManager,self).filter(variation_category='weight',is_active=True)
    
    def Age(self):
        return super(VariationManager,self).filter(variation_category='Age',is_active=True)

variation_category_choice=(
    ('weight','weight'),
    ('Age','Age')
)

class Variation(models.Model):
     product=models.ForeignKey(Product,on_delete=models.CASCADE)
     variation_category=models.CharField(max_length=100,choices=variation_category_choice)
     variation_value=models.CharField(max_length=100)
     is_active=models.BooleanField(default=True)
     created_at=models.DateTimeField(auto_now=True)

     objects = VariationManager()

     def __str__(self):
        return self.variation_value

     def __unicode__(self) :
         return self.product
     
    



############################------------------------User profile---------------------------#####################################


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
    

############################------------------------wishlist---------------------------#####################################


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)



############################------------------------coupon management---------------------------#####################################


class Coupon(models.Model):
    coupon_code         = models.CharField(max_length=100)
    is_expired          = models.BooleanField(default=False)
    discount_percentage = models.IntegerField(default=10, validators=[MinValueValidator(0), MaxValueValidator(100)])
    minimum_amount      = models.IntegerField(default=400)
    max_uses            = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    expire_date         = models.DateField()
    total_coupons       = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)  
    

    def save(self, *args, **kwargs):
        # Get the current date
        current_date = timezone.now().date()
        
        # Compare expire_date with current_date
        if self.total_coupons <= 0 or self.expire_date < current_date:
            self.is_expired = True
        else:
            self.is_expired = False
        # Save the instance
        super().save(*args, **kwargs)


    def __str__(self):
        return self.coupon_code


class CouponUsage(models.Model):
    Coupon=models.ForeignKey(Coupon,on_delete=models.CASCADE)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.DO_NOTHING)
    is_used=models.BooleanField(default=False)
     
class Discount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True, blank=True)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    date_applied = models.DateTimeField(auto_now_add=True)