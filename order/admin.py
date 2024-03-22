

# Register your models here.
from django.contrib import admin
from .models import Order, Payment, OrderProduct
# Register your models here.

admin.site.register(Payment)
admin.site.register(Order)
admin.site.register(OrderProduct)

