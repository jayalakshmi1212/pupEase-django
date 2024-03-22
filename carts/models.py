from django.db import models
from store.models import Product
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import get_user_model

# Create your models here.
class Cart(models.Model):
    cart_id=models.CharField(max_length=250,blank=True)
    date_added=models.DateField(auto_now_add=True)


    def __str__(self) :
        return self.cart_id


def get_default_user():
    User = get_user_model()
    return User.objects.first().pk  

class Cartitem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    is_active=models.BooleanField(default=True)


    def sub_total(self):
        return self.product.price * self.quantity


    def __str__(self) :
        return self.product