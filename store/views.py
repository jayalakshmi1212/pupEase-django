from django.http import HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
from store.models import Category
from django.views.generic import ListView
from store.forms import CategoryForm
from store.models import Product,Discount,Variation
from carts.models import Cartitem
from store.forms import ProductForm
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm
from .models import Addresses
from .forms import AddressForm
from django.contrib import messages
from userauths.models import User
from django.db.models import Q
from .models import Wishlist
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.http import JsonResponse
from .models import Coupon,Brand
import json
from django.utils import timezone
from carts.models import Cart
from django.db.models import Value, CharField
from django.db.models.functions import Lower


@never_cache
def index(request):
    # if request.user.is_authenticated:
    #     if request.user.is_superuser:
    #         return redirect("adminp:admin_home")
    products = Product.objects.filter(is_active=True)  # Query the Product model
    paginator=Paginator(products,3)
    page=request.GET.get('page')
    paged_products=paginator.get_page(page)

    context = {
        'products': paged_products,  # Pass the queried products to the template context
    }
    return render(request, 'store/index.html', context)

def shop(request):
    # Fetch all active categories
    categories = Category.objects.filter(is_active=True)
    
    # Query the Product model
    products = Product.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    print(products.values_list())
    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    category_slug = request.GET.get('category')
    brand_name = request.GET.get('brand')
    print(category_slug)
    if category_slug and brand_name:
        products = products.filter(category__slug=category_slug, brand__brand_name=brand_name)
    elif category_slug:
        products = products.filter(category__slug=category_slug)
    elif brand_name:
        products = products.filter(brand__brand_name=brand_name)

    # Sorting functionality
    sort_by = request.GET.get('sort')
    if sort_by == 'popularity':
        products = products.order_by('-popularity')  # Adjust field name if needed
    elif sort_by == 'price_low_to_high':
        products = products.order_by('price')
    elif sort_by == 'price_high_to_low':
        products = products.order_by('-price')
    elif sort_by == 'average_rating':
        products = products.order_by('-average_rating')  # Adjust field name if needed
    elif sort_by == 'new_arrivals':
        products = products.order_by('-created_date')  # Adjust field name if needed
    elif sort_by == 'featured':
        products = products.filter(is_featured=True)  # Adjust field name if needed
        
    elif sort_by == 'a_to_z':
        products = products.annotate(lower_name=Lower('name')).order_by('lower_name')
    elif sort_by == 'z_to_a':
        products = products.annotate(lower_name=Lower('name')).order_by('-lower_name')
    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'selected_category_slug': category_slug,
        'sort_by': sort_by,
        'search_query': search_query,
        'selected_brand': brand_name,
    }
    return render(request, 'store/shop.html', context)



def about(request):
    return render(request,"store/about.html")

def contact(request):
    return render(request,"store/contact.html")

#________________________category_management___________________________________________
#_____________________________________________________________________________________

class CategoryListView(ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'

def edit_category(request, category_id):
   
    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('store:category_list')  # Redirect to category list page after editing
    else:
        form = CategoryForm(instance=category)
    return render(request, 'edit_category.html', {'form': form})


def add_category(request):
   
    if request.method == 'POST':
        form = CategoryForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('store:category_list')  # Redirect to category list page after adding category
    else:
        form = CategoryForm()
    return render(request, 'add_category.html', {'form': form})


def delete_category(request, category_id):
    
    category = get_object_or_404(Category, pk=category_id)
    category.is_active = not category.is_active  # Toggle is_active attribute
    category.save()
    return redirect('store:category_list')  # Redirect to category list page after toggling






def category_detail(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    return render(request, 'store/shop.html', {'category': category})




#________________________product_management___________________________________________
#_____________________________________________________________________________________


def product_list(request):
    sort_by = request.GET.get('sort_by')

    if sort_by == 'price_low_to_high':
        products = Product.objects.order_by('price')
    elif sort_by == 'price_high_to_low':
        products = Product.objects.order_by('-price')
    else:
        products = Product.objects.all()

    return render(request, 'product/product_list.html', {'products': products})

def product_update(request, pk):
  
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('store:product_list'))  # Redirect to product list page after update
    else:
        form = ProductForm(instance=product)
    return render(request, 'product/product_update.html', {'form': form})





def product_delete(request, pk):
    
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        # Toggle the is_active field
        product.is_active = not product.is_active
        product.save()
        # Redirect to the appropriate page (home or shop page)
        return redirect('store:product_list')  # Change 'store:index' to your actual URL name for the home page

    # If request method is not POST, render the delete confirmation page
    return render(request, 'product/product_delete.html', {'product': product})


def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('store:product_list')  # Redirect to product list page after saving
    else:
        form = ProductForm()
    return render(request, 'product/product_add.html', {'form': form})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    is_in_wishlist = False
    
    if request.user.is_authenticated:
        # Check if the product is in the wishlist of the current user
        is_in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    return render(request, 'product/product_detail.html', {'product': product, 'is_in_wishlist': is_in_wishlist})




#________________________user_profile___________________________________________
#_____________________________________________________________________________________
@login_required
def myaccountmanager(request):
    current_user = request.user
    if current_user.is_authenticated:
        user =User.objects.get(username = current_user.username)
       
        context = {
            'user' : user, 
            
        }
            
        #context.update(catcom(request))
        try:              #comparing two objects here not fields
            if UserProfile.objects.filter(user = user).exists:
                profile = UserProfile.objects.get(user = user)
                context['profile'] = profile
        except:
            pass
        
        
      
        return render(request, 'profile/dashboard.html')
    
    return redirect('userauths:loginpage')

@login_required
def accountdetails(request):
    current_user = request.user
    user = User.objects.get(username = current_user.username)
    context = {
        'user':user
        }
    #context.update(catcom(request))
    try:
        if UserProfile.objects.filter(user = user).exists:
            profile = UserProfile.objects.get(user = user)
            context['profile'] = profile
    except:
        pass
    return render(request , 'profile/account-details.html',context)
   
from django.db import transaction
@transaction.atomic
@login_required

@login_required
def editprofile(request):

    user = request.user
    try:
        profile=UserProfile.objects.get(user = user)
    except UserProfile.DoesNotExist as e :
        profile = UserProfile(user = user)
    form = UserProfileForm(instance = profile)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(request, "Profile successfully completed!!.....")
            return redirect('store:account_details')
        else:
            error = form.errors
            context = {'form':form, 'error':error}
            return render(request, 'profile/edit-profile.html',context)
    return render(request, 'profile/edit-profile.html',{'form':form})



@login_required
def addressbook(request):
    current_user = request.user
    address_form = AddressForm(user=current_user)
    addresses = Addresses.objects.filter(user=current_user, is_active=True).order_by('-is_default')
    
    context = {
        'address_form': address_form,
        'addresses': addresses, 
    }
    return render(request, 'profile/address-book.html', context)


@login_required
def addaddress(request):
    if request.method == 'POST':
        form = AddressForm(data=request.POST, user=request.user)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user  # Set the user before saving
            address.save()
            messages.success(request, "Address successfully added!!.....")
            return redirect('store:address_book')
        else:
            error = form.errors
            print(error)
            context = {'form': form, 'error': error}
            return render(request, 'profile/add-address.html', context)
    
    form = AddressForm(user=request.user)
    return render(request, 'profile/add-address.html', {'form': form})

@login_required
def editaddress(request, pk):
    user = request.user
    try:
        address = Addresses.objects.get(id=pk)
    except Addresses.DoesNotExist:
        address = None

    if request.method == 'POST':
        form = AddressForm(data=request.POST, instance=address, user=user)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = user  # Set the user before saving
            address.save()
            messages.success(request, "Address successfully Updated!!.....")
            return redirect('store:address_book')
        else:
            error = form.errors
            print(error)
            context = {'form': form, 'error': error}
            return render(request, 'profile/edit-address.html', context)
    else:
        form = AddressForm(instance=address, user=user)
    return render(request, 'profile/edit-address.html', {'form': form})

# The rest of the views remain unchanged

 
@login_required
def deleteaddress(request,pk):
    try:
        address = Addresses.objects.get(id=pk)
        address.is_active = False
        address.save()
        return redirect('store:address_book')                
    
    except Addresses.DoesNotExist:
        return redirect('store:address_book')   

@login_required        
def defaultaddress(request, pk):
    try:  
        other = Addresses.objects.all().exclude(id=pk)
        for address in other:
            address.is_default = False
            address.save()

        address = Addresses.objects.get(id=pk)
        address.is_default = True
        address.save()
        return redirect('store:address_book')   
    except Addresses.DoesNotExist:
        return redirect('store:address_book')   
    
# .......................................................filter.................................................................
    

def shop0(request):
    products = Product.objects.filter(is_active=True).annotate(lower_name=Lower('name')).order_by('lower_name')
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    
    context = {'products': products, 'categories': categories, 'brands': brands}
    return render(request, 'store/shop.html', context)

def shop1(request):
    products = Product.objects.filter(is_active=True).annotate(lower_name=Lower('name')).order_by('-lower_name')
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    context = {'products': products, 'categories': categories, 'brands': brands}
    return render(request, 'store/shop.html', context)

def shop_ase_price(request):
    products = Product.objects.filter(is_active=True).order_by('price')
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    context = {'products': products, 'categories': categories, 'brands': brands}
    return render(request, 'store/shop.html', context)

def shop_des_price(request):
    products = Product.objects.filter(is_active=True).order_by('-price')
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    context = {'products': products, 'categories': categories, 'brands': brands}
    return render(request, 'store/shop.html', context)

def shop_new_arrivals(request):
    products = Product.objects.filter(is_active=True).order_by('-created_date')
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    context = {'products': products, 'categories': categories, 'brands': brands}
    return render(request, 'store/shop.html', context)

# ----------------------------------------wishlist--------------------------------------------------------?
import uuid
@login_required(login_url='userauths:loginpage')
def add_to_wishlist(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, pk=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if not created:
            # Item already exists in the wishlist
            # You can add a message or perform any other action here
             messages.warning(request, f"{product.name} is already in your wishlist.")
    return redirect('store:product_detail', pk=product_id)

def remove_from_wishlist(request, product_id):
    if request.user.is_authenticated:
        wishlist_item = get_object_or_404(Wishlist, product_id=product_id, user=request.user)
        wishlist_item.delete()
    return redirect('store:wishlist')  # Assuming 'store' is the app namespace
@login_required(login_url='userauths:loginpage')
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist/wishlist.html', {'wishlist_items': wishlist_items})

def remove_from_wishlist_in_product_detail(request, product_id):
    if request.user.is_authenticated:
        wishlist_item = get_object_or_404(Wishlist, product_id=product_id, user=request.user)
        wishlist_item.delete()
    return redirect(reverse('store:product_detail', kwargs={'pk': product_id}))  # Assuming 'store' is the app namespace

from carts.views import add_cart
@login_required
def add_to_cart_from_wishlist(request, product_id):
    # Call the existing add_to_cart function
    response = add_cart(request, product_id)

    # Remove the item from the wishlist
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()

    return response
###################################--------------coupon-------------------##########################################
from datetime import datetime
# views.py

from django.http import JsonResponse
from .models import Coupon

def get_coupons(request):
    coupons = Coupon.objects.filter(is_active=True)
    return render(request, 'carts:checkout', {'coupons': coupons})

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

from decimal import Decimal
def  apply_coupon(request):
    print('apply coupon entry')
    if request.method == 'POST':
        payload = json.loads(request.body)
        coupon_code = payload.get('coupon_code')
        print('coupon code:',coupon_code)
            
        try:
            coupon = Coupon.objects.get(coupon_code=coupon_code)
            if not coupon.is_expired:
                # Apply discount to the total price
                # You need to implement this logic based on your models
                cart = Cart.objects.get(cart_id=_cart_id(request))
                user = request.user
                cart_items = user.cart_items.filter(cart=cart,is_active=True, product__stock__gt=0)

                print("Cart items:")
                for cart_item in cart_items:
                    print(cart_item.product.name)
                
                # Calculate total price of all cart items
                total = sum(cart_item.sub_total() for cart_item in cart_items)
                
                # Calculate tax
                tax = (2 * total) / 100
                
                # Calculate grand total
                grand_total = total + tax
                
                # Apply discount based on coupon
                discount_percentage = Decimal(coupon.discount_percentage)
                discount_amount = (discount_percentage / 100) * grand_total
                new_total_price = grand_total - discount_amount
                new_total_price = float(new_total_price)
                discount_percentage =float( discount_percentage )
                request.session['discounted_total'] = new_total_price
                request.session['discount_percentage'] = float(discount_percentage)
                return JsonResponse({'success': True, 'new_total_price': new_total_price, 'discount_percentage': float(discount_percentage)})
            else:
                return JsonResponse({'success': False, 'message': 'Coupon is expired'})
        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid coupon code'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})





from django.views.generic import View

class RemoveCouponView(View):
    def post(self, request):
        # Remove the discounted total from the session if it exists
        if 'discounted_total' in request.session:
            del request.session['discounted_total']
            request.session.modified = True
        if 'discount_percentage' in request.session:
            del request.session['discount_percentage']
        # Return a JSON response indicating success
        return JsonResponse({'success': True})
    

def remove_coupon(request):
    print('enter remove_coupon')
    try:
        del request.session['discounted_total']  # Remove the discounted total from the session
        del request.session['discount_percentage']


        # Recalculate the total price without the coupon discount
        # You need to implement this logic based on your models
        cart = Cart.objects.get(cart_id=_cart_id(request))
        user = request.user
        cart_items = user.cart_items.filter(cart=cart, is_active=True, product__stock__gt=0)
        total = sum(cart_item.sub_total() for cart_item in cart_items)
        tax = (2 * total) / 100
        grand_total = total + tax
        print(grand_total)
        return JsonResponse({'success': True, 'new_total': grand_total})
    except KeyError:
        return JsonResponse({'success': False, 'message': 'Coupon not found in session'})
