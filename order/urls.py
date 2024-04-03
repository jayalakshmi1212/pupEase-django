from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'order'

urlpatterns = [
    # path('place-order/',views.place_order,name="place_order"),
    path('payment/',views.payment,name="payment"),
    path('create_address/',views.create_address,name='create_address'),
    path('user-orders/', views.user_orders, name='user_orders'),
    path('order/<str:order_number>/', views.order_detail, name='order_detail'),
    path('cancel_order/<str:order_number>/',views.cancel_order,name='cancel_order'),
     path('generate-pdf/<str:order_number>/', views.generate_pdf, name='generate_pdf'),
    path('paymenthandler/',views.paymenthandler,name='paymenthandler')
]