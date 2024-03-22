from django.contrib import admin

# Register your models here.
from django.contrib import admin
from store.models import Category
from store.models import Product,UserProfile



admin.site.register(Category)
admin.site.register(Product)
admin.site.register(UserProfile)
