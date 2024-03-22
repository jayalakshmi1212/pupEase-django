from django.urls import path
from userauths import views

app_name = 'userauths'

urlpatterns = [
    path('login/',views.printlogin,name='loginpage'),
    path("signup/", views.printsignup, name='signuppage'),
    path("logout/", views.printlogout, name="readlogout"),
    path("verify_otp/",views.verify_otp,name='verify_otp'),
    path("invalid/",views.invalid_otp,name='invalid_page'),
    path('forgotpassword/',views.forgotpassword,name='forgotpassword'),
    path('resetpassword/<uidb64>/<token>/',views.resetpassword_validation,name='resetpassword_validate'),
    path('resetpassword/',views.reset_password,name='reset_password'),
]
