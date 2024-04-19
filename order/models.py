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
    

class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
       
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True) 
    order_number = models.CharField(max_length=50, unique=True, blank=True)  # Make order_number unique
    address = models.ForeignKey(Addresses, on_delete=models.SET_NULL, null=True, blank=True)
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
        if self.delivered_at:
            current_date = timezone.now()
            return self.delivered_at + timedelta(days=3) >= current_date
        return False
   
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate a unique order number if it's not already set
            self.order_number = get_random_string(length=10)
        super().save(*args, **kwargs)
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

    def total(self):
       return self.product_price * self.quantity


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