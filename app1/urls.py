from django.urls import path
from app1.views import *

urlpatterns = [
    path('', index, name='index'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout, name='logout'),
    path('products/', allproduct, name='allproduct'),
    path('products/<int:id>', filterproduct, name='filterproduct'),
    path('product/<int:id>', singleproduct, name='singleproduct'),
    path('changepassword/', changepassword, name='changepassword'),
    path('profile/', profile, name='profile'),
    path('contact-us', contactus, name='contactus'),
    path('buynow/', buyNow, name='buynow'),
    path('razorpay/', razorpayView, name='razorpayview'),
    path('paymenthandler/', paymenthandler, name='paymenthandler'),
    path('paymentstatus/', successview, name='orderSuccessView'),
    path('myorders/', myorders, name='myorders'),
    path('search/', searchview, name='search'),
]