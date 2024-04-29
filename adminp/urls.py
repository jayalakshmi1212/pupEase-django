from django.urls import path
from adminp import views
from .views import DeleteCouponView
from .views import ToggleCouponStatusView

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
    path('update_order_status/', views.update_order_status, name='update_order_status'),
    
    path('sales-report-pdf/', views.SalesReportPDFView.as_view(), name='sales_report_pdf'),

    path('all_coupon/',views.all_coupon,name='all_coupon'),
    path('create_coupon/',views.create_coupon,name='create_coupon'),
    path('coupon/',views.all_coupon,name='coupon'),
    path('edit_coupon/',views.edit_coupon,name='edit_coupon'),
    path('delete_coupon/', DeleteCouponView.as_view(), name='delete_coupon'),
    path('toggle_coupon_status/', ToggleCouponStatusView.as_view(), name='toggle_coupon_status'),


    path('all_brand/', views.all_brand, name='all_brand'),
    path('create_brand/', views.create_brand, name='create_brand'),
    path('brand/<int:brand_id>/delete/', views.delete_brand, name='delete_brand'),
    path('toggle_brand_active/<int:brand_id>/', views.toggle_brand_active, name='toggle_brand_active'),
    path('edit_brand/<int:brand_id>/', views.edit_brand, name='edit_brand'),

]

