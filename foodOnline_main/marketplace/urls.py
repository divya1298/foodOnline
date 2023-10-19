from django.urls import path
from . import views

urlpatterns = [
    path('', views.marketplace, name='marketplace'),
    path('<slug:slug>/', views.vendor_details, name='vendor_details'),

    # CART
    path('add_to_cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
]