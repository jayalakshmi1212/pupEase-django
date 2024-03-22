from django.http import HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.conf import settings
from userauths.models import User
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from order.models import Order,OrderProduct




# Create your views here.
# def is_superuser(request):
#     user = request.user
#     if user.is_superuser:
#         return True
#     return False

# @login_required(login_url='admin_app:admin_login')
# def admin_dashboard(request):
#     if not is_superuser(request):
#         return redirect('user_app:home')
#     return render(request, 'admin_template\index.html')

@never_cache
@login_required(login_url='adminp:admin_login')
def adminhome(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return render(request,'adminp/admin_home.html')
        return redirect("store:index")


def adminuser(request):
   
    if request.user.is_superuser:
        data = User.objects.all().order_by('id').values()
        return render(request, 'adminp/admin_user.html', {'userdata': data})
    else:
         return render(request,'adminp/admin_home.html')
    
from django.http import HttpResponseBadRequest

def toggle_user_status(request, user_id):
    if request.method == 'POST':
        user = User.objects.get(pk=user_id)
        user.is_active = not user.is_active
        user.save()
        return redirect('adminp:admin_user')  # Redirect back to admin user page
    else:
        return HttpResponseBadRequest("Invalid request method")
  


@never_cache
def admin_login(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect("adminp:admin_home")
        else:
            print("jaya super")
            return redirect("store:index")
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('adminp:admin_home')  # Redirect to admin home upon successful login
        else:
            messages.error(request, 'Invalid login credentials.')
            return redirect('adminp:admin_login')  # Redirect back to login page with error message
    else:
        return render(request, 'adminp/admin_login.html')
    

def admin_logout(request):
    logout(request)
    return redirect('adminp:admin_login')


def order_list(request):
    orders = Order.objects.all()  # Retrieve all orders from the database
    return render(request, 'adminp/order_list.html', {'orders': orders})



def change_order_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('new_status')
        order = Order.objects.get(id=order_id)
        order.status = new_status
        order.save()
    return redirect('adminp:order_list')

def admin_order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    selected_address = order.address  # Assigning order.address to selected_address
    
    # Fetching related order products
    order_products = order.orderproduct_set.all()
    for order_product in order_products:
       total_amount = order_product.product_price * order_product.quantity


    context = {
        'order': order,
        'selected_address': selected_address,
        'order_products': order_products,  # Passing order products to the template
    }
    return render(request, 'adminp/admin_order_detail.html', context)
