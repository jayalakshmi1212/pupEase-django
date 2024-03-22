from django.urls import path
from adminp import views

app_name='adminp'

urlpatterns=[
    path("adminhome",views.adminhome,name='admin_home'),
    path("adminuser/",views.adminuser,name='admin_user'),
    path('adminlogin/',views.admin_login,name='admin_login'),
    path('toggle_user_status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('adminlogout/',views.admin_logout,name='adminlogout'),
    path('orders/', views.order_list, name='order_list'),
    path('change_status/', views.change_order_status, name='change_order_status'),
    path('admin_order_detail/<str:order_number>/',views.admin_order_detail,name='admin_order_detail'),

]

