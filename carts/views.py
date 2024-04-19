from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from carts.models import Cart, Cartitem
from order.models import Order,Wallet,Transaction
from store.models import Product, Addresses,Variation,Discount
from store.forms import AddressForm
from django.contrib import messages
import json
import razorpay
from order.models import Order,Payment
from django.conf import settings
import datetime
from django.http import JsonResponse,HttpResponseBadRequest
from django.utils.crypto import get_random_string


# Utility function to get or create a cart session
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

# View to add a product to the cart
@login_required
def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    user = request.user
    product_variation=[]
    if request.method=='POST':
        for item in request.POST:
            key=item
            value=request.POST[key]
            
            try:
                variation=Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass

        

   
    # Check if product is in stock
    if product.stock <= 0:
        return HttpResponse("This product is out of stock.")

    # Check if adding this product will exceed maximum quantity per person
    max_quantity_per_person = 5  # Example value, adjust as needed
    cart_items_count_for_product = Cartitem.objects.filter(product=product, user=user).count()
    if cart_items_count_for_product >= max_quantity_per_person:
        return HttpResponse("You have reached the maximum quantity allowed for this product.")

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))

    try:
        cart_item = Cartitem.objects.get(product=product, cart=cart)
        if cart_item.quantity < product.stock:  # Check if adding more would exceed available stock
            cart_item.quantity = F('quantity') + 1 
            if len(product_variation) > 0:
                cart_item.variations.clear()
                for item in product_variation:
                    cart_item.variations.add(item) # Ensure atomic increment of quantity
            cart_item.save()
    except Cartitem.DoesNotExist:
        if product.stock > 0:  # Ensure product is in stock before adding to cart
            cart_item = Cartitem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
                user=user  # Associate the cart item with the authenticated user
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                for item in product_variation:
                    cart_item.variations.add(item)
            cart_item.save()

    return redirect('cart:cart')


def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = get_object_or_404(Cartitem, product__id=product_id, cart=cart)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart:cart')


def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = Cartitem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart:cart')


# View to display the cart
def cart(request):
    total = 0
    quantity = 0
    tax = 0
    grand_total = 0
    cart_items = None
    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = Cartitem.objects.filter(cart=cart, is_active=True, product__stock__gt=0)  # Filter out-of-stock products
        for cart_item in cart_items:
            # Calculate total based on discounted price if available
            if cart_item.product.discounted_price:
                total += (cart_item.product.discounted_price * cart_item.quantity)
            else:
                total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
    except Cart.DoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }

    return render(request, 'carts/cart.html', context)


@login_required
def checkout(request):
    print('cart/checkout')
    current_user = request.user
    form = AddressForm(user=current_user)
    addresses = Addresses.objects.filter(user=current_user, is_active=True).order_by('-is_default').distinct()

    total = 0
    quantity = 0
    cart_items = None
    tax = 0
    grand_total = 0
    selected_address = None


   
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = Cartitem.objects.filter(cart=cart, is_active=True, product__stock__gt=0)  # Filter out-of-stock products
        
        for cart_item in cart_items:
            # Calculate total based on discounted price if available
            if cart_item.product.discounted_price:
                total += (cart_item.product.discounted_price * cart_item.quantity)
            else:
                total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2 * total) / 100
       

        discounted_total = request.session.get('discounted_total')
        if discounted_total:
            grand_total = discounted_total
        else:
            grand_total = total + tax

        print('grandtotal:', grand_total)
    except Cart.DoesNotExist:
        pass

    if request.method == 'POST':
        print('checkout/post')
        
        payload = json.loads(request.body)
        selected_payment_method = payload.get('selected_payment_method')
        selected_address_id = payload.get('selected_address')
        print("Selected payment method:", selected_payment_method) 
        print(selected_address_id,"selected address id")

        draft_order = Order()
        draft_order.user = request.user
        draft_order.order_total = grand_total
        # Generate order number
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr, mt, dt)
        current_date = d.strftime("%Y%m%d")
        order_number = get_random_string(length=10) 
        draft_order.order_number = order_number
        draft_order.tax =tax
        draft_order.status ='New'
        address=Addresses.objects.get(id=selected_address_id)
        draft_order.address=address
        draft_order.save()
        print(draft_order.order_number)
        print("order/checkout/180")
        payment = _process_payment(request.user, draft_order.order_number, selected_payment_method, grand_total)
        print("payment_process_payment",payment)
        draft_order.payment = Payment.objects.get(payment_order_id=payment['payment_order_id'])
        draft_order.save()
        print("draft_order",draft_order)

        return JsonResponse({'message': 'Success', 'context': payment})
            

    context = {
        'form': form,
        'addresses': addresses,
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
        'selected_address': selected_address,
    }

    return render(request, 'carts/checkout.html', context)



def _process_payment(user, order_number, payment_methods_instance, grandtotal):
    payment = None
    print(order_number,"mmmmmmmmmmmmmmmm")
    print("ordr/process_payment......................")
    if payment_methods_instance == 'Razor-Pay':
        print("cart/_processpayment/razorpay")
        client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.KEY_SECRET))
        data = {
            'amount': (int(grandtotal) * 100),
            'currency': 'INR',
        }
        payment1 = client.order.create(data=data)
        payment_order_id = payment1['id']
        payment = Payment.objects.create(
            user = user,
            payment_id = payment_order_id,
            payment_method=payment_methods_instance,
            amount_paid=0,
            status='PENDING',
            payment_order_id=payment_order_id,
        )
        payment1 = {
            'payment_id': payment.id,
            'payment_order_id': payment.payment_order_id,
            'amount': (int(grandtotal) * 100),
        }
        return payment1
    else:
        print("cart/_processpayment/cod")
       
        try:
            print(user)
            payment = Payment.objects.create(
                payment_method=payment_methods_instance,
                amount_paid=0,
                payment_id  = order_number,
                status='PENDING',
                payment_order_id=order_number,
                user = user
            )
            print("uuuuuuuuuuuuuuu")
            payment_data = {
                'payment_id': payment.id,
                'payment_order_id': payment.payment_order_id,
            }
            print("kkkkkkkkkkkkkkkkkkkkk")
            print(payment)
            print("kkkkkkkkkkkkkkkkkkkkk")
            return payment_data
        except Exception as e:
            print("Error occurred:", e)