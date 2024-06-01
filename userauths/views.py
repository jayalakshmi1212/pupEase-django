from datetime import timedelta,datetime
from django.utils import timezone
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from userauths.forms import Usersignup
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
from django.conf import settings
import random
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.contrib.auth.models import User as customuser
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from order.models import Wallet



User=settings.AUTH_USER_MODEL
@never_cache
def printlogin(request):
    print("jaya")
    if request.user.is_authenticated:
        return redirect("store:index")
    # else:
    #     print("jaya super")
    #     return redirect("store:index")
    
    if request.method=='POST':
        print("jaya double super")
        email=request.POST.get('email')
        password=request.POST.get('password')

        try:
            user=User.objects.get(email=email)
        except:
            messages.warning(request,f"User with {email} does not exist")
        user=authenticate(request,email=email,password=password)

        if user is not None:
            login(request,user)
            
            return redirect('store:index')
        else:
            messages.warning(request,"User does not exist,create an account.")   

    return render(request,"userauths/login.html")



def printsignup(request):
    if request.method == 'POST':
        form = Usersignup(request.POST)
        if form.is_valid():
            new_user = form.save()  # Save the user
            
            # Create a wallet for the new user
            Wallet.objects.create(user=new_user, balance=0.0)
            
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            new_user = form.save()
            username = form.cleaned_data.get('username')
           
            new_user = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password1'])
            login(request, new_user)
            otp = random.randint(100000, 999999)
            print(otp)
            request.session['otp'] = str(otp)
            
            # Check if otp_expiry_time already exists in the session
            if 'otp_expiry_time' not in request.session:
                expiration_time = timezone.now() + timedelta(minutes=1)
                request.session['otp_expiry_time'] = expiration_time.isoformat()  # Expires after 1 minute
            
            send_mail(
                'Doghouse OTP Verification',
                'Your OTP is ' + str(otp),
                'jayalakshmim720@gmail.com',
                [email],
                fail_silently=False,
            )
            return redirect("userauths:verify_otp")
    else:
        form = Usersignup()

    # If form is not valid, include form errors in the context
    context = {
        'form': form,
        'errors': form.errors if request.method == 'POST' else None,
    }
    return render(request, 'userauths/signup.html', context)



def printlogout(request):
    if request.user.is_authenticated:
        logout(request) 
    return redirect('userauths:loginpage')



@never_cache
def verify_otp(request):
    
    if 'otp' in request.session: 
        if request.method == 'POST':
            otp = request.POST.get('otp')
            otp_expiry_time_str = request.session.get('otp_expiry_time')
            otp_expiry_time = datetime.fromisoformat(otp_expiry_time_str)

            if otp == request.session.get('otp') and timezone.now() <= otp_expiry_time:
                # Perform actions after OTP verification
                messages.success(request, f"Hey Your account was created successfully")
                return redirect('store:index')
            else:
                messages.error(request, 'Invalid otp')
                return redirect('userauths:invalid_page')
            
        else:
            otp_expiry_time_str = request.session.get('otp_expiry_time')
            otp_expiry_time = datetime.fromisoformat(otp_expiry_time_str)
            return render(request, "userauths/verify.html", {'otp_expiry_time':otp_expiry_time})

    else:
        return redirect('userauths:signuppage')


def invalid_otp(request):
    
    return render(request,'userauths/invalid.html')

User = get_user_model() 
def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            
            current_site = get_current_site(request)
            subject = 'Reset your password'
            body = render_to_string('userauths/resetmailcontent.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(subject, body, to=[to_email])
            send_email.send()
            messages.success(
                request, 'Password reset email has been sent to your email address')
            return render(request, 'userauths/forgotpassword.html')
        else:
            messages.error(request, "Account doesn't exist for the provided email.")
            return redirect('userauths:forgotpassword')
    return render(request, 'userauths/forgotpassword.html')


def resetpassword_validation(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password.!')
        return redirect('userauths:reset_password')
    else:
        messages.error(request, 'Sorry, the activation link has expired.!')
        return redirect('userauths:loginpage')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password == confirm_password:
            uid = request.session.get('uid')
            user = User.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password successfully reset.")
            return redirect('userauths:loginpage')  # Redirect to login page after successful reset
        else:
            messages.error(request, "Passwords do not match.")
            return redirect('userauths:reset_password')  # Redirect back to the reset password page
    else:
        return render(request, 'userauths/reset_password.html')