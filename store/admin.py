from django.contrib import admin

# Register your models here.
from django.contrib import admin
from store.models import Category
from store.models import Product,UserProfile,Variation,Brand,Sale


class Varitionadmin(admin.ModelAdmin):
    list_display=('product','variation_category','variation_value','is_active')
    list_editable=('is_active',)
    list_filter=('product','variation_category','variation_value','is_active')

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Sale)
admin.site.register(UserProfile)
admin.site.register(Brand)
admin.site.register(Variation,Varitionadmin)
