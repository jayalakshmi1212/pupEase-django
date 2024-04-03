from django.http import HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.conf import settings
from userauths.models import User
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from order.models import Order,OrderProduct,Product,Payment
from store.models import Category,Product

from django.db.models import Sum
from django.utils import timezone
from datetime import datetime
from datetime import date,timedelta
from calendar import month_name
from django.views import View
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
from django.core.paginator import Paginator


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
        paginator = Paginator(data, 10)
        page = request.GET.get('page')
        paged_data = paginator.get_page(page)
        return render(request, 'adminp/admin_user.html', {'userdata': paged_data})
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
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'adminp/order_list.html', {'orders': page_obj})



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








##############################################

def adminhome(request):
    Products = Product.objects.all()
    orders = Order.objects.filter(is_ordered=True)
    categories = Category.objects.all()
    payments = Payment.objects.filter(status='SUCCESS')
    
    # Calculate total revenue
    revenue = sum(float(payment.amount_paid) for payment in payments)

    # Calculate monthly revenue
    current_month = timezone.now().month
    monthly_payments = payments.filter(created_at__month=current_month)
    monthly_revenue = monthly_payments.aggregate(total=Sum('amount_paid'))['total'] or 0

    # Calculate user signups and orders for the past 6 months
    current_datetime = timezone.now()
    start_date = current_datetime - timedelta(days=180)
    data = [['Month', 'New User Signups', 'New Orders']]
    while start_date < current_datetime:
        end_date = start_date.replace(day=1) + timedelta(days=31)
        new_user_signups = User.objects.filter(date_joined__gte=start_date, date_joined__lt=end_date).count()
        new_orders = Order.objects.filter(created_at__gte=start_date, created_at__lt=end_date).count()
        data.append([start_date.strftime('%B'), new_user_signups, new_orders])
        start_date = end_date

    # Filter orders based on date range and status
    all_orders = Order.objects.all().order_by('-id').exclude(status='New')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status = request.GET.get('status')
    if start_date:
        all_orders = all_orders.filter(created_at__gte=start_date)
    if end_date:
        all_orders = all_orders.filter(created_at__lt=end_date)
    if status and status != 'Status':
        all_orders = all_orders.filter(status=status)
    
    paginator = Paginator(all_orders, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

   

    context = {
        
        "revenue": revenue,
        "monthly_revenue": monthly_revenue,
        "orders": orders,
        "all_orders": page_obj,
        "order_count": orders.count(),
        "product_count": Products.count(),
        "category_count": categories.count(),
        'data': data,
        
    }
    
    return render(request, 'adminp/admin_home.html', context)


class SalesReportPDFView(View):
    def save_pdf(self,params:dict):
        template = get_template("adminp/sales_report.html")
        html = template.render(params)
        response = BytesIO()
        pdf =pisa.pisaDocument(BytesIO(html.encode('UTF-8')),response)
        
        if not pdf.err:
            return HttpResponse(response.getvalue(), content_type='application/pdf'),True
        return '',None
    # @login_required(login_url='accounts:signin')
    def get(self, request, *args, **kwargs):
        # if not is_superuser(request):
        #     return redirect('store:home')
        total_users = len(User.objects.all())
        new_orders = len(Order.objects.all().exclude(status="new"))
        revenue_total = 0
        payments = Payment.objects.filter(status = 'SUCCESS')
        revenue_total = 0
        for payment in payments.all():
            revenue_total += int(float(payment.amount_paid ))   
        current_date = date.today()

        current_month = timezone.now().month
        monthly_payments = Payment.objects.filter(
        status='SUCCESS',
        created_at__month=current_month
        )
        monthly_revenue = monthly_payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        status = request.GET.get('status')
        # Convert start_date and end_date to timezone-aware datetime objects
        start_date = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d')) if start_date else None
        end_date = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d')) if end_date else None

        # Filter orders based on date range and status
        all_orders = Order.objects.all()
        if start_date and end_date:
            all_orders = all_orders.filter(created_at__gte=start_date, created_at__lt=end_date)
        elif start_date:
            all_orders = all_orders.filter(created_at__gte=start_date)
        elif end_date:
            all_orders = all_orders.filter(created_at__lt=end_date)
        if status and status != 'Status':
            all_orders = all_orders.filter(order_status=status)
      
        params = {
            'total_users' :total_users,
            'new_orders' : new_orders,
            'revenue_total' : revenue_total,
            # 'd_month' :delivered_orders_this_month,
            'd_month_len' : len(monthly_payments),
            'revenue_this_month' : monthly_revenue,
            'all_orders': all_orders,  # Pass filtered orders to the template

        }
        file_name, success = self.save_pdf(params)
        
        if success:
            response = HttpResponse(file_name, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
            return response
        else:
            # Handle error case here, like displaying an error message to the user.
            return HttpResponse("Failed to generate the invoice.", status=500)

