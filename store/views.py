from django.http import HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
from store.models import Category
from django.views.generic import ListView
from store.forms import CategoryForm
from store.models import Product
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



@never_cache
def index(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect("adminp:admin_home")
    products = Product.objects.filter(is_active=True)  # Query the Product model

    context = {
        'products': products,  # Pass the queried products to the template context
    }
    return render(request, 'store/index.html', context)

def shop(request):
    # Fetch all active categories
    categories = Category.objects.filter(is_active=True)
    
    # Query the Product model
    products = Product.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
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
        products = products.order_by('name')
    elif sort_by == 'z_to_a':
        products = products.order_by('-name')

    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'store/shop.html', context)



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
    return render(request, 'product/product_detail.html', {'product': product})




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
            return render(request, 'profile\edit-profile.html',context)
    return render(request, 'profile\edit-profile.html',{'form':form})



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
    products = Product.objects.filter(is_active=True).order_by('name')
    context = {'products': products}
    return render(request, 'store/shop.html', context)

def shop1(request):
    products = Product.objects.filter(is_active=True).order_by('-name')
    context = {'products': products}
    return render(request, 'store/shop.html', context)

def shop_ase_price(request):
    products = Product.objects.filter(is_active=True).order_by('price')
    context = {'products': products}
    return render(request, 'store/shop.html', context)

def shop_des_price(request):
    products = Product.objects.filter(is_active=True).order_by('-price')
    context = {'products': products}
    return render(request, 'store/shop.html', context)


# ----------------------------------------wishlist--------------------------------------------------------?


def add_to_wishlist(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, pk=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if not created:
            # Item already exists in the wishlist
            # You can add a message or perform any other action here
            pass
    return redirect('store:product_detail', pk=product_id)
def remove_from_wishlist(request, wishlist_id):
    if request.user.is_authenticated:
        wishlist_item = Wishlist.objects.get(pk=wishlist_id)
        if wishlist_item.user == request.user:
            wishlist_item.delete()
    return redirect('store:wishlist')


@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist/wishlist.html', {'wishlist_items': wishlist_items})