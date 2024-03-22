from django.shortcuts import render
from django.http import HttpResponse
import datetime
from django.shortcuts import render
from carts.models import Cart, Cartitem
from django.shortcuts import render, get_object_or_404, redirect
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



def place_order(request):
    current_user = request.user
    cart_items = Cartitem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    
    if cart_count <= 0:
        return redirect('store:index')
    
    total = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
    
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = current_user
            address.save()

            # Check if user has selected an address
            if not current_user.profile.selected_address:
                messages.error(request, "Please select an address before placing the order.")
                return redirect('cart:checkout')  # Adjust the URL name according to your project

            # Generate unique order number
            order_number = get_random_string(length=10)  # Example: Generate a random string of length 10
            print(order_number)

            order = Order.objects.create(
                user=current_user,
                order_number=order_number,  # Assign the generated order number
                address=address,
                order_note=request.POST.get('order_note', ''),
                order_total=grand_total,
                tax=tax,
                ip=request.META.get('REMOTE_ADDR'),
                deliverd_at=timezone.now() + timezone.timedelta(days=5)
            )

            for cart_item in cart_items:
                OrderProduct.objects.create(
                    order=order,
                    user=current_user,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    product_price=cart_item.product.price,
                    ordered=True
                )

            # Set session variable to indicate order has been placed
            request.session['order_placed'] = True

            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'payment_method': 'Cash on Delivery'
            }
            return render(request, 'carts/payment.html', context)
    else:
        form = AddressForm()
    
    return render(request, 'carts/delivery-address.html', {'form': form})

def payment(request):
    current_user = request.user
    cart_items = Cartitem.objects.filter(user=current_user)
    total = sum(cart_item.product.price * cart_item.quantity for cart_item in cart_items)
    tax = (2 * total) / 100
    grand_total = total + tax

    selected_address_id = request.POST.get('selected_address')
    selected_address = None
    if selected_address_id:
        try:
            selected_address = Addresses.objects.get(id=selected_address_id)
        except Addresses.DoesNotExist:
            pass

    payment = Payment.objects.create(
        user=current_user,
        payment_id=f'COD-{current_user.pk:05d}-{timezone.now().strftime("%Y%m%d%H%M%S")}',
        payment_method='Cash on Delivery',
        amount_paid=grand_total,
        status='Processed',
    )

    order = Order.objects.create(
        user=current_user,
        order_total=total,
        tax=tax,
        ip=request.META.get('REMOTE_ADDR'),
        payment=payment,
        address=selected_address,
        status='confirmed' 
    )

    for cart_item in cart_items:
        OrderProduct.objects.create(
            order=order,
            user=current_user,
            product=cart_item.product,
            quantity=cart_item.quantity,
            product_price=cart_item.product.price,
            ordered=True
        )

    order.is_ordered = True
    # Calculate the delivery date (5 days after the order date)
    delivery_date = timezone.now() + timedelta(days=5)
    order.deliverd_at = delivery_date
    order.save()

    context = {
        'order': order,
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
        'payment_method': 'Cash on Delivery',
        'selected_address': selected_address
    }

    cart_items.delete()
    return render(request, 'carts/payment.html', context)



def order_success(request):
    current_user = request.user
    cart_items = Cartitem.objects.filter(user=current_user)
    total = sum(cart_item.product.price * cart_item.quantity for cart_item in cart_items)
    tax = (2 * total) / 100
    grand_total = total + tax

    orders = Order.objects.filter(user=current_user, is_ordered=True)

    if orders.count() == 1:
        order = orders.first()
    else:
        return redirect('cart:order_success')

    context = {
        'order': order,
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
        'payment_method': 'Cash on Delivery'
    }

    cart_items.delete()
    return render(request, 'carts/order-success.html', context)


def create_address(request):
    if request.method == 'POST':
        form = AddressForm(data=request.POST, user=request.user)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.is_active = True
            address.save()
            messages.success(request, "Address successfully added!")
            return redirect('cart:checkout')
    else:
        form = AddressForm(user=request.user)

    return render(request, 'carts/checkout.html', {'form': form})
def order_success(request):
    current_user = request.user
    cart_items = Cartitem.objects.filter(user=current_user)
    total = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
    
    tax = (2 * total) / 100
    grand_total = total + tax

    orders = Order.objects.filter(user=current_user, is_ordered=True)

    if orders.count() == 1:
        order = orders.first()
    else:
        return redirect('store:index')

    context = {
        'order': order,
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
        'payment_method': 'Cash on Delivery'
    }

    cart_items.delete()
    return render(request, 'carts/order-success.html', context)

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
            error = form.errors
            print(error)
            context = {'form': form, 'error': error}
            return render(request, 'cart/create_address.html', context)
    
    form = AddressForm(user=request.user)
    return render(request, 'carts/checkout.html', {'form': form})


def user_orders(request):
    user = request.user
    orders = Order.objects.filter(user=user).prefetch_related('orderproduct_set', 'address')

    orders_info = []
    for order in orders:
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

    return render(request, 'carts/user_orders.html', {'user_orders': orders_info})


def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    selected_address = order.address  # Assigning order.address to selected_address
    
    # Fetching related order products
    order_products = order.orderproduct_set.all()

    context = {
        'order': order,
        'selected_address': selected_address,
        'order_products': order_products,  # Passing order products to the template
    }
    return render(request, 'carts/order_detail.html', context)


def cancel_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    order.status = 'cancelled'
    order.save()
    return JsonResponse({'message': 'Order cancelled successfully'})

from xhtml2pdf import pisa

def generate_pdf(request, order_number):
    # Retrieve the order object using the order number
    order = get_object_or_404(Order, order_number=order_number)

    # Render the HTML template with order details
    template_path = 'carts/invoice_template.html'
    context = {'order': order}
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