from django.db import models

# Create your models here.
from django.db import models
# Create your models here.
from django.utils import timezone
from datetime import timedelta, timezone
from django.db import models
from carts.models import Cart,Cartitem
from store.models import Addresses,UserProfile
from store.models import Product
from userauths.models import User
from django.utils.crypto import get_random_string
from django.conf import settings

# Create your models here.
class Payment(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_id  = models.CharField(max_length=200)
    payment_method = models.CharField(max_length=200)
    amount_paid = models.CharField(max_length=50)
    status      = models.CharField(max_length=100)
    payment_order_id = models.CharField(max_length= 100, null=True, blank=True)
    payment_signature   = models.CharField(max_length=100, null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    """ spike_use = models.BooleanField(default=False)
    spike_discount = models.PositiveBigIntegerField(default = 0)
    coupon_use = models.BooleanField(default = False)
    coupon_discount = models.PositiveIntegerField(default=0)
    coupon_code = models.CharField(max_length=50,default='') """
     
    def __str__(self):
        return self.payment_id
    
class Shipping_Addresses(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=20)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50,blank=True,null=True)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=2)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)    
    
    
    def save(self, *args, **kwargs):
        if self.is_default:
            Shipping_Addresses.objects.filter(user = self.user).exclude(pk=self.pk).update(is_default=False)
        super(Shipping_Addresses, self).save(*args, **kwargs)
        
    def get_user_full_address(self):
        address_parts = f"{self.name}, {self.phone_number}, {self.address_line_1}"
        
        if self.address_line_2:
            address_parts += (', '+self.address_line_2)
        
        address_parts += (f", Pin: {self.pincode}, {self.city}, {self.state}, India")
        
        
        return address_parts
        # return f'{self.name},{self.phone},Pin:{self.pincode},Address:{self.address_line_1},{self.address_line_2},{self.city},{self.state},{self.country}'
    
    def __str__(self):
        return self.name    


from django.contrib.auth import get_user_model
User = get_user_model()
class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('failed','failed'),
       
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True) 
    order_number = models.CharField(max_length=50, unique=True, blank=True)  # Make order_number unique
    address = models.ForeignKey(Addresses, on_delete=models.SET_NULL, null=True, blank=True)
    shipping_address = models.ForeignKey(Shipping_Addresses,on_delete=models.SET_NULL,unique=False, null= True ,blank=True,related_name = 'order_of_shipping')
    order_note = models.CharField(max_length=50, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=50, choices=STATUS, default='New')
    ip = models.CharField(max_length=50, blank=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deliverd_at = models.DateTimeField(null=True)
    returned_at = models.DateTimeField(null=True)

    def __str__(self):
        if self.address:
            return self.address.name
        return f"Order {self.id} (No Address)"

    def can_return_products(self):
        if self.deliverd_at:
            current_date = timezone.now()
            return self.deliverd_at + timedelta(days=3) >= current_date
        return False
   
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate a unique order number if it's not already set
            self.order_number = get_random_string(length=10)
        super().save(*args, **kwargs)
    def can_return_products(self):
        # Define the logic to check if products can be returned
        return self.status == 'Delivered' and self.deliverd_at is not None

#
from django.db.models import Sum

class SalesReport:
    @staticmethod
    def overall_sales_count():
        return Order.objects.count()
    
    @staticmethod
    def overall_order_amount():
        return Order.objects.aggregate(total_amount=Sum('order_total'))['total_amount'] or 0
    
    @staticmethod
    def overall_discount_amount():
        return Order.objects.aggregate(total_discount=Sum('discount_amount'))['total_discount'] or 0

 
class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Reference the Product model directly
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.product.name 
    
    def save(self, *args, **kwargs):
        if not self.pk:  # if this is a new OrderProduct instance
            # Decrease the stock of the associated product
            product = self.product
            if product:
                product.stock -= self.quantity
                product.save()
        super().save(*args, **kwargs)

     
    def total_price(self):
        return self.quantity * self.product_price
    
class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    balance = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.first_name + str(self.balance)

class Transaction(models.Model):
    TRANSACTION_CHOICES =(
        ("CREDIT", "Credit"),
        ("DEBIT", "Debit"),
        )
    wallet           = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount           = models.IntegerField(default=0)
    transaction_type = models.CharField(choices=TRANSACTION_CHOICES,max_length=10)
    created_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_type + str(self.wallet) + str(self.amount)