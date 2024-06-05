from django.shortcuts import render
from django.http import HttpResponse
import datetime
from django.shortcuts import render
from carts.models import Cart, Cartitem
from django.shortcuts import render, get_object_or_404, redirect
from order.models import Wallet,Transaction
from store.forms import AddressForm
from django.http import HttpResponse
from datetime import datetime as dt
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import HttpResponse
from carts.models import Cart, Cartitem
from .models import Order, OrderProduct, Payment
from store.forms import AddressForm
from django.utils import timezone
from django.contrib import messages
from .models import Addresses
from datetime import timedelta
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.template.loader import get_template
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
import razorpay
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import F
from order.models import Shipping_Addresses



def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse  # Import HttpResponse module
from django.shortcuts import get_object_or_404


def payment(request): #this is order success page

    print("order/payment entry")
    
    user = request.user
    
    # Retrieve cart items
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_items = Cartitem.objects.filter(cart=cart, is_active=True, product__stock__gt=0)
    
    # Calculate total based on cart items
    total = 0
    quantity = 0
    for cart_item in cart_items:
        if cart_item.product.discounted_price:
            total += (cart_item.product.discounted_price * cart_item.quantity)
        else:
            total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    
    # Calculate tax and grand total
    tax = (2 * total) / 100
    grand_total = total + tax
    discounted_total = request.session.get('discounted_total', grand_total)
    
    order = Order.objects.filter(user=user).last()
    print("paymeny/order1",order.__dict__)
    
    # Update payment method based on selected option
    order.status='confirmed'
    order.is_ordered = True

    grand_total = discounted_total

    # Create OrderProduct instances
    for cart_item in cart_items:
        OrderProduct.objects.create(
            order=order,
            user=user,
            product=cart_item.product,
            quantity=cart_item.quantity,
            product_price=cart_item.product.price,
            ordered=True
        )

    # Mark order as ordered
    # Calculate the delivery date (5 days after the order date)
    delivery_date = timezone.now() + timedelta(days=5)
    order.deliverd_at = delivery_date
    order.save()
    if 'discounted_total' in request.session:
       del request.session['discounted_total']
    # print('payment_method:',order.payment.payment_method)
    print("paymeny/order",order.__dict__)
    print("paymeny/orderproduct",OrderProduct)
    # Delete cart items
    cart_items.delete()
    dummy_orders=Order.objects.filter(is_ordered = False)
    dummy_orders.delete()

    shipping_address, created = Shipping_Addresses.objects.get_or_create(
    user=order.address.user,
    name=order.address.name,
    phone_number=order.address.phone_number,
    address_line_1 = order.address.address_line_1 , 
    address_line_2 = order.address.address_line_2 , 
    city = order.address.city , 
    country = order.address.country ,
    state = order.address.state , 
    pincode = order.address.pincode , 
    
)
    order.shipping_address = shipping_address
    order.save()
    payment_method = order.payment.payment_method if order.payment else "COD"
    print(payment_method)
    
    context = {
        'order': order,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
        'selected_address': order.address,
        'payment_method': payment_method,

    }
    return render(request, 'carts/payment.html', context)




   
def order_success(request):
    return redirect(request,'order/order_success.html')
 

def create_address(request):
    if request.method == 'POST':
        form = AddressForm(data=request.POST, user=request.user)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.is_active = True  # Ensure the address is active
            address.save()
            messages.success(request, "Address successfully added!")
            return redirect('cart:checkout')
    else:
        form = AddressForm(user=request.user)
    
    # Render the template with the form
    return render(request, 'carts/create_address.html', {'form': form})


def user_orders(request):
    print('order/user_orders')
    user = request.user
    orders = Order.objects.filter(
        user=user,
        status__in=['New', 'confirmed', 'failed','cancelled','Delivered']  # Include orders with status "New", "confirmed", or "failed"
    ).annotate(
        latest_created_at=F('created_at')
    ).order_by('-latest_created_at').prefetch_related('orderproduct_set', 'address')
    for order in orders:
      print(f"Order Number: {order.order_number}, Status: {order.status}")
    
    for order in orders:
        if order.status == 'failed':
            order.save()  # Ensure all failed orders are marked as failed in the database


    paginator = Paginator(orders, 6)  # Show 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    orders_info = []
    for order in orders:
       print(f"Order Number: {order.order_number}, Status: {order.status}")
    
    # Check if the order status is "failed" and take action accordingly
       if order.status == 'failed':
        # Perform some action for failed orders
        print("This order has failed.")

    for order in page_obj:
        products_info = []
        for order_product in order.orderproduct_set.all():
            products_info.append({
                'product_image': order_product.product.image.url if order_product.product.image else None,
                'product_name': order_product.product.name,
            })

        orders_info.append({
            'order_number': order.order_number,
            'order_total': order.order_total,
            'tax': order.tax,
            'status': order.status,
            'created_at': order.created_at,
            'deliverd_at': order.deliverd_at, 
            'selected_address': order.address,
            'products_info': products_info,
        })
        

    return render(request, 'carts/user_orders.html', {'user_orders': orders_info, 'page_obj': page_obj})


def order_detail(request, order_number):
    print('order/order_det')
    order = get_object_or_404(Order, order_number=order_number)
    selected_address = order.address  # Assigning order.address to selected_address
    payment_method = order.payment.payment_method if order.payment else "COD"
    print(payment_method)
    if order.payment and order.payment.status == 'failed':
        order.status = 'failed'
        order.save()

    # Fetching related order products
    order_products = order.orderproduct_set.all()
    
    context = {
        'order': order,
        'selected_address': selected_address,
        'order_products': order_products,  # Passing order products to the template
        'payment_method': payment_method ,
    }
    return render(request, 'carts/order_detail.html', context)

def return_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        if order.can_return_products():
            # Perform the return action here
            order.status = 'Returned'
            order.returned_at = timezone.now()
            order.save()
            messages.success(request, f"Order {order.order_number} has been returned successfully.")
        else:
            messages.error(request, f"You cannot return this order anymore.")
    
    return redirect('cart:order_detail', order_id=order.id)

def cancel_order(request, order_number):
    print('order/cancel_orde')
    order = get_object_or_404(Order, order_number=order_number)
    if order.payment.payment_method== 'Razor-Pay':
        print('enter into if')
        user_wallet = Wallet.objects.get(user=order.user)
        amount_to_credit = order.order_total
        
        user_wallet.balance += amount_to_credit
        user_wallet.save()
        print("wallet",user_wallet.balance)
        Transaction.objects.create(
            wallet=user_wallet,
            amount=order.order_total,
            transaction_type='CREDIT'
        )
        print('enteredddddddddddd')
    order.status = 'cancelled'
    order.save()
    return JsonResponse({'message': 'Order cancelled successfully'})

from xhtml2pdf import pisa

def generate_pdf(request, order_number):
    # Retrieve the order object using the order number
    order = get_object_or_404(Order, order_number=order_number)
    selected_address = order.address  # Assigning order.address to selected_address
    payment_method = order.payment.payment_method if order.payment else "COD"

    # Render the HTML template with order details
    template_path = 'carts/invoice_template.html'
    context = {'order': order,
                'selected_address': selected_address,
                'payment_method':payment_method
                }
    template = get_template(template_path)
    html = template.render(context)

    # Create a PDF file
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    # Generate PDF from HTML content
    pisa_status = pisa.CreatePDF(
        html, dest=response,
        encoding='utf-8'
    )
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse

@csrf_exempt
def paymenthandler(request):
    print("order/Payment Handler endpoint reached")
    if request.method == "POST":
        try:
            # Extract parameters from the POST request
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            print(f'1:{payment_id},2:{razorpay_order_id},3:{signature}')
            
            # Create a dictionary with payment details
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            
            # Verify the payment signature
            client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.KEY_SECRET))
            result = client.utility.verify_payment_signature(params_dict)
            print("Signature verification result:", result)
            
            if not result:
                print('Payment signature verification failed.')
                return JsonResponse({'message': 'Payment signature verification failed.'}, status=400)
            
            # Update payment status to 'SUCCESS' if signature verification passes
            print('kaaaaaaaaaaaaaaaaaaa')
            payment = Payment.objects.get(payment_order_id=razorpay_order_id)
            payment.status = 'SUCCESS'
            payment.payment_id = payment_id
            payment.payment_signature = signature
            payment.save()

            # Fetch the order associated with the payment
            order = Order.objects.get(payment=payment)
            order.is_ordered = True
            order.save()
            print("paymenthandler/order",order.__dict__)

            # Redirect to payment success page
            return redirect('order:payment')
            #return HttpResponseRedirect(reverse('order:payment'))  # Change 'payment_success' to the actual URL name of your payment success page
        except Exception as e:
            print('Exception:', str(e))
            try:
                # Retrieve the payment object associated with the failed transaction
                payment = Payment.objects.get(payment_order_id=razorpay_order_id)
                payment.status = 'failed'
                payment.save()

                # Update the order status to "failed"
                order = Order.objects.get(payment=payment)
                order.status = 'failed'
                order.save()
            except Payment.DoesNotExist:
                pass  # Handle the case where payment object doesn't exist

            return render(request, 'carts/paymentfail.html')
    else:
        print('non-post request is recieved')
        print('Invalid request method.')
        return redirect('cart:checkout')



def Failedpayments(request):
     # Query failed payments
    failed_payments = Payment.objects.filter(status='failed')

    context = {
        'failed_payments': failed_payments,
    }
    # Pass failed payment details to the template
    return render(request, 'carts/failedpayments.html',  context)