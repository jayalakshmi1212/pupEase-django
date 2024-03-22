from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from carts.models import Cart, Cartitem
from store.models import Product, Addresses
from store.forms import AddressForm
from django.contrib import messages

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
            cart_item.quantity = F('quantity') + 1  # Ensure atomic increment of quantity
            cart_item.save()
    except Cartitem.DoesNotExist:
        if product.stock > 0:  # Ensure product is in stock before adding to cart
            cart_item = Cartitem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
                user=user  # Associate the cart item with the authenticated user
            )

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
    current_user = request.user
    form = AddressForm(user=current_user)
    addresses = Addresses.objects.filter(user=current_user, is_active=True).order_by('-is_default').distinct()

    total = 0
    quantity = 0
    cart_items = None
    tax = 0
    grand_total = 0
    selected_address = None

    if request.method == 'POST':
        # Handle the delivery address form submission
        form = AddressForm(request.POST, user=current_user)
        if form.is_valid():
            form.save()
            messages.success(request, "Address successfully added!")
            # Redirect to the same page to refresh the address list
            return redirect('carts:checkout')

        # Retrieve the selected address ID from the POST request
        selected_address_id = request.POST.get('selected_address')
        if selected_address_id:
            try:
                selected_address = Addresses.objects.get(id=selected_address_id, user=current_user, is_active=True)
            except Addresses.DoesNotExist:
                messages.error(request, "Invalid selected address.")

    try:
        if request.user.is_authenticated:
            cart_items = Cartitem.objects.filter(user=current_user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = Cartitem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    # Check if the order has been placed successfully
    if 'order_placed' in request.session and request.session['order_placed']:
        # If order has been placed, set cart_items to None
        cart_items = None

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