from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import HttpResponse
from store.models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id

from .models import Product, ReviewRating,ProductGallery
from django.contrib import messages
from .forms import ReviewForm
from orders.models import OrderProduct


def store(request, category_slug = None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug = category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator=Paginator(products,3) # pagination added here
        page=request.GET.get('page')
        paged_products=paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True)#.order_by('id') # pagination added here
        paginator=Paginator(products,6)# pagination added here
        page=request.GET.get('page')
        paged_products=paginator.get_page(page)
        product_count = products.count()
    context = {
        'product_count': product_count,
        'products': paged_products,
    }

    return render(request,'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug = product_slug)
        #checking same item in add cart
        cart_exists=CartItem.objects.filter(cart__cart_id=_cart_id(request) , product=single_product).exists()
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None
    
    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)


    # Get the product gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    #Updating Review
    user_review = None
    if request.user.is_authenticated:
        user_review = ReviewRating.objects.filter(user=request.user, product_id=single_product).first()


    context = {
        'single_product': single_product,
        'cart_exists': cart_exists, # adding cart_exists in context
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery,
        'user_review': user_review,
    }
    return render(request, 'store/product_detail.html', context)

def search(request): # Search bar Functionality 
    if 'keyword' in request.GET: # if we get keyword in path it stores the path value or url value in keyword variable
        keyword=request.GET['keyword']
        if keyword:
            products=Product.objects.order_by('-created_date').filter(Q (description__icontains=keyword) | Q(product_name__icontains=keyword)) # search bar functionality added here . The main here is the Double underscore functinality
            product_count=products.count()
        context={
            'products':products,
            'product_count':product_count,
        }
    

    return render(request,'store/store.html', context)

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)

 
 


 
