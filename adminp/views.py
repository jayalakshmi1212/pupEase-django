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
from store.models import Coupon,Brand
from django.http import JsonResponse
from django.db.models import Q


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
    orders = Order.objects.order_by('-created_at') # Retrieve all orders from the database
    search_query = request.GET.get('q')
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |  # Search by order number
            Q(user__username__icontains=search_query)  # Search by username
            # Add more fields to search as needed
        )
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



def update_order_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        status = request.POST.get('status')

        # Fetch the order object
        order = Order.objects.get(pk=order_id)

        # Update the status of the order
        order.status = status
        order.save()

        # Redirect back to the admin order detail page
        return redirect('adminp:admin_order_detail', order_number=order.order_number)
    else:
        # If the request method is not POST, redirect to some error page
        return redirect('error_page_url')





##############################################

def adminhome(request):
    Products = Product.objects.all()
    orders = Order.objects.filter(is_ordered=True)
    categories = Category.objects.all()
    brands = Brand.objects.all()
    payments = Payment.objects.filter(status='SUCCESS')
    
    # Calculate total revenue
    revenue = sum(float(payment.amount_paid) for payment in payments)

    # Calculate monthly revenue
    current_month = timezone.now().month
    monthly_payments = payments.filter(created_at__month=current_month)
    if monthly_payments:
       monthly_revenue = monthly_payments.aggregate(total=Sum('amount_paid'))['total'] or 0
    else:
        monthly_revenue=0
    

    
    # Top 10 best selling products
    top_selling_products = Product.objects.annotate(total_quantity_sold=Sum('sale__quantity_sold')).order_by(
        '-total_quantity_sold')[:5]

    # Top 10 best selling categories
    top_selling_categories = Category.objects.annotate(total_quantity_sold=Sum('product__sale__quantity_sold')).order_by(
        '-total_quantity_sold')[:5]

    # Top 10 best selling brands
    top_selling_brands = Brand.objects.annotate(total_quantity_sold=Sum('product__sale__quantity_sold')).order_by(
        '-total_quantity_sold')[:5]

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
        "brands": brands,
        "top_selling_products": top_selling_products,
        "top_selling_categories": top_selling_categories,
        "top_selling_brands": top_selling_brands,
        
    }
    
    return render(request, 'adminp/admin_home.html', context)


from django.http import JsonResponse
from django.db.models import Sum
from datetime import datetime

def monthly_data_view(request):
    # Calculate monthly revenue
    current_month = datetime.now().month
    monthly_payments = Payment.objects.filter(created_at__month=current_month)
    monthly_revenue = monthly_payments.aggregate(total=Sum('amount_paid'))['total'] or 0

    # Your other calculations for monthly data

    # Serialize the data
    data = {
        'monthly_revenue': monthly_revenue,
        # Add other monthly data here
    }

    return JsonResponse(data)

def yearly_data_view(request):
    # Calculate yearly revenue
    current_year = datetime.now().year
    yearly_payments = Payment.objects.filter(created_at__year=current_year)
    yearly_revenue = yearly_payments.aggregate(total=Sum('amount_paid'))['total'] or 0

    # Your other calculations for yearly data

    # Serialize the data
    data = {
        'yearly_revenue': yearly_revenue,
        # Add other yearly data here
    }

    return JsonResponse(data)



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


##########################################-------coupon---------###############################################


@never_cache
@login_required(login_url='admin_login')
def all_coupon(request):
    coupon = Coupon.objects.all()
    paginator = Paginator(coupon,8)
    page = request.GET.get('page')
    paged_coupons = paginator.get_page(page)
    context = { 'coupon':paged_coupons }
    return render(request, 'adminp/all_coupon.html', context)


@never_cache

def create_coupon(request):
    if request.method == 'POST':
        coupon_code           = request.POST.get('coupon_code')
        discount_percentage   = request.POST.get('discount_percentage')
        minimum_amount        = request.POST.get('minimum_amount')
        max_uses              = request.POST.get('max_uses')
        expire_date           = request.POST.get('expire_date')
        total_coupons         = request.POST.get('total_coupons')
        expire_date = datetime.strptime(expire_date, '%d %b %Y').date()
        coupon = Coupon.objects.create(
            coupon_code         = coupon_code,
            discount_percentage = int(discount_percentage),
            minimum_amount      = int(minimum_amount),
            max_uses            = int(max_uses),
            expire_date         = expire_date,
            total_coupons       = int(total_coupons),
        )
        coupon.save()
        return redirect('adminp:all_coupon')
    return render(request, 'adminp/add_coupon.html')

@never_cache
def edit_coupon(request):
    coupon_id = request.GET.get('id')
    old_coupon = Coupon.objects.get(id=coupon_id)
    if request.method == 'POST':
        coupon_code           = request.POST.get('coupon_code')
        discount_percentage   = request.POST.get('discount_percentage')
        minimum_amount        = request.POST.get('minimum_amount')
        max_uses              = request.POST.get('max_uses')
        expire_date           = request.POST.get('expire_date')
        total_coupons         = request.POST.get('total_coupons')
        
        expire_date = datetime.strptime(expire_date, '%d %b %Y').date()
        old_coupon.coupon_code         = coupon_code
        old_coupon.discount_percentage = int(discount_percentage)
        old_coupon.minimum_amount      = int(minimum_amount)
        old_coupon.max_uses            = int(max_uses)
        old_coupon.expire_date         = expire_date
        old_coupon.total_coupons       = int(total_coupons)
        old_coupon.save()
        return redirect('adminp:all_coupon')
    return render(request, 'adminp/edit_coupon.html', {'old_coupon':old_coupon})

class DeleteCouponView(View):
    def get(self, request):
        coupon_id = request.GET.get('id')
        coupon = Coupon.objects.get(id=coupon_id)
        coupon.delete()
        return redirect('adminp:all_coupon')
    


class ToggleCouponStatusView(View):
    def post(self, request):
        coupon_id = request.POST.get('id')
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            # Toggle the active status of the coupon
            coupon.is_active = not coupon.is_active
            coupon.save()
            return JsonResponse({'success': True, 'message': 'Coupon status toggled successfully'})
        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Coupon not found'}, status=404)

# Inside your views.py file
from django import template

register = template.Library()

@register.simple_tag
def coupon_button_text(is_active):
    if is_active:
        return 'Deactivate'
    else:
        return 'Activate'



#________________________________________brand_______________________________________________#

@login_required
def all_brand(request):
    brd = Brand.objects.all()
    context = { 'brd':brd }
    return render(request,'adminp/all_brand.html',context)


@login_required
def create_brand(request):
    if request.method == 'POST':
        brand = request.POST.get('brand')
        brd = Brand(brand_name=brand)
        brd.save()
        return redirect('adminp:all_brand')
    return render(request,'adminp/add_brand.html')



@login_required
def toggle_brand_active(request, brand_id):
    brand = get_object_or_404(Brand, pk=brand_id)
    if request.method == 'POST':
        brand.is_active = not brand.is_active
        brand.save()
        # Redirect back to the admin brand page
        return redirect('adminp:all_brand')
    else:
        # If the request method is not POST, return an error JSON response
        return JsonResponse({'error': 'Invalid request method'})

@login_required
def delete_brand(request, brand_id):
    brand = get_object_or_404(Brand, pk=brand_id)
    is_active = brand.is_active  # Store the current active status
    if request.method == 'POST':
        brand.delete()
        # If the brand was active before deletion, set is_active to False
        if is_active:
            return JsonResponse({'status': 'success', 'is_active': False})
        else:
            return JsonResponse({'status': 'success', 'is_active': True})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def edit_brand(request, brand_id):
    brand = get_object_or_404(Brand, pk=brand_id)
    if request.method == 'POST':
        brand.brand_name = request.POST.get('brand_name')
        brand.save()
        return redirect('adminp:all_brand')
    return render(request, 'adminp/edit_brand.html', {'brand': brand})