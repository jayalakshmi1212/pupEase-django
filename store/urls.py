from django.urls import path
from store import views
from wallet.views import wallet as walletviews
from wallet.views import paymenthandler2 as paymenthandlerView
from wallet.views import payment_failed as paymentfailedView


app_name='store'

urlpatterns=[
    path("",views.index,name='index'),
    path("shop/",views.shop,name='shop'),
    path("about/",views.about,name='about'),
    path("contact/",views.contact,name='contact'),

    #category
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('category/<slug:category_slug>/', views.category_detail, name='category_detail'),
     path('categories/<int:category_id>/edit/', views.edit_category, name='edit_category'),
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('add_category/',views.add_category,name='add_category'),

    #product
    path('product_list/', views.product_list, name='product_list'),
    path('product/<int:pk>/update/', views.product_update, name='product_update'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('add_product/', views.add_product, name='product_add'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
   
    #user profile
    path('myaccountmanager/',views.myaccountmanager,name='my_account_manager'),
    path('accountdetails/',views.accountdetails,name='account_details'),
    path('editprofile/',views.editprofile,name='edit_profile'),

    #user address
    path('addressbook/',views.addressbook,name='address_book'),
    path('addaddress/', views.addaddress, name='add_address'),
    path('editaddress/<int:pk>', views.editaddress, name='edit_address'),
    path('deleteaddress/<int:pk>', views.deleteaddress, name='delete_address'),
    path('defaultaddress/<int:pk>', views.defaultaddress, name='default_address'),

    #filter
    path('shop0/',views.shop0,name='shop0'),
    path('shop1/',views.shop1,name='shop1'),
    path('shop_ase_price/',views.shop_ase_price,name='shop_ase_price'),
    path('shop_des_price/',views.shop_des_price,name='shop_des_price'), 
    path('shop_new_arrivals/',views.shop_new_arrivals,name='shop_new_arrivals'),                                        
    
    #wishlist
    path('wishlist/',views.wishlist,name='wishlist'),
    path('add_to_wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('remove_from_wishlist_in_product_detail/<int:product_id>/',views.remove_from_wishlist_in_product_detail,name='remove_from_wishlist_in_product_detail'),
    path('wishlist/add_to_cart/<int:product_id>/',views.add_to_cart_from_wishlist, name='add_to_cart_from_wishlist'),

    #wallet
    path('wallet/',walletviews, name='wallet'),
    path('paymenthandler2/',paymenthandlerView,name='paymenthandler2'),
    path('payment-failed/',paymentfailedView,name='payment_failed'),
    
    #coupon
    path('apply_coupon/',views.apply_coupon,name='apply_coupon'),
    path('get_coupons/',views.get_coupons,name='get_coupons'),
    path('remove_coupon/', views.remove_coupon, name='remove_coupon'),
    #brand
    
]
    

    