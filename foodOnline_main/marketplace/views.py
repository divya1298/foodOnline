from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from vendor.models import Vendor
from menu.models import Category, FoodItem
from django.db.models import Prefetch
from .models import Cart
from .context_processors import get_cart_counter
from django.contrib.auth.decorators import login_required


# Create your views here.
def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    context = {
        'vendors': vendors,
    }
    return render(request, 'marketplace/listing.html', context)


def vendor_details(request, slug):
    vendor = get_object_or_404(Vendor, slug=slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/vendor_details.html', context)


def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        # check if the food exists
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # Check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status': 'Success', 'message': 'Incremented the cart quantity',
                                         'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity})
                except:
                    chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status': 'Success', 'message': 'Added the food to the cart',
                                         'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'The food does not exist'})

        return JsonResponse({'status': 'Success', 'message': 'User is logged in'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})


def decrease_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Check if the food item exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # Check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    if chkCart.quantity > 1:
                        # decrease the cart quantity
                        chkCart.quantity -= 1
                        chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity = 0
                    return JsonResponse(
                        {'status': 'Success', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity,
                         'cart_amount': get_cart_amounts(request)})
                except:
                    return JsonResponse({'status': 'Failed', 'message': 'You do not have this item in your cart!'})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This food does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})

    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})


@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)


def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                cart_items = Cart.objects.get(user=request.user, id=cart_id)
                if cart_items:
                    cart_items.delete()
                    return JsonResponse({'status': 'Success', 'message': 'Cart Items has been deleted!',
                                         'cart_counter': get_cart_counter(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'Cart Items does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
