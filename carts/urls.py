from django.urls import path
from .import views
app_name='cart'

urlpatterns=[
     path('cart/',views.cart,name='cart'),
     path('cart/count/', views.cart_count, name='cart_count'),
     path('add/<int:product_id>/', views.add_cart, name='add_cart'),
     path('remove/<int:product_id>/', views.remove_cart, name='remove_cart'),
     path('remove_item/<int:product_id>/', views.remove_cart_item, name='remove_cart_item'),


    path('checkout/',views.checkout,name="checkout"),
]