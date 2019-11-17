from django.urls import path 
from django.conf.urls import url
#views
from .views import (
    IndexView,
    ItemDetailView,
    OrderSummaryView,
    add_to_cart,
    remove_from_cart,
    increase_quantity,   
    remove_single_item_from_cart,
    CheckoutView,
    AddCouponView,
    OnlinePaymentView,
    BankpPaymentView,
    Profile,


    add_to_cart2
 
)


app_name= 'src' 

urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('item/<slug>/', ItemDetailView.as_view(), name='item-detail'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('increase-quantity/<pk>/', increase_quantity, name='increase-quantity'),   
    path('remove-from-cart/<pk>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<pk>/', remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('order-summary/',  OrderSummaryView.as_view(), name='order-summary'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('online/<payment_option>/', OnlinePaymentView.as_view(), name='online'),
    path('bank/<payment_option>/', BankpPaymentView.as_view(), name='bank'),
    path('profile/<slug>/', Profile.as_view(), name='profile'),



    path('add-cart/<slug>/', add_to_cart2, name='add-cart'),
] 