from django.urls import path
from . import views

urlpatterns = [
    path('', views.store_home, name='home'),
    path('add-to-cart/<int:shoe_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<str:item_key>/', views.remove_from_cart, name='remove_from_cart'), # <-- NEW LINE
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/<int:shoe_id>/', views.checkout, name='checkout'),
    path('cart-checkout/', views.cart_checkout, name='cart_checkout'),
    path('success/', views.success_page, name='success'),
    path('callback/', views.mpesa_callback, name='mpesa_callback'),
]