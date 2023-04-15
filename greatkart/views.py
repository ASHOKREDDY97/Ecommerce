from django.shortcuts import render
from store.models import Product,ReviewRating

from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id

def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('created_date')

    # Get the reviews
    reviews = None
    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        'products': products,
        'reviews': reviews,
    }
    return render(request, 'home.html', context)
# def store(request):

 