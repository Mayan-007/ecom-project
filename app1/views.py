import razorpay
from django.shortcuts import render, redirect
from app1.models import *
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.core.mail import send_mail
import random

RAZOR_KEY_ID = 'rzp_test_pU8vcIpmq3B5Nc'
RAZOR_KEY_SECRET = 'EQlRxTerlLDZD7qDqYWug0Gt'
client = razorpay.Client(auth=(RAZOR_KEY_ID, RAZOR_KEY_SECRET))

# Create your views here.
def checkSession(request):
    if request.session.has_key('user_id'):
        return True

def index(request):
    categories = Category.objects.all()
    if checkSession(request):
        user = User.objects.get(id=request.session['user_id'])
        return render(request, 'index.html', {'categories': categories, 'user': user})
    return redirect('login')

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(email=email)
            print(user.password)
            if user.password == password:
                request.session['user_id'] = user.id
                return redirect('index')
            else:
                return render(request, 'login.html', {'error': 'Invalid Password'})
        except:
            return render(request, 'login.html', {'error': 'Invalid Email'})
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        name = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        password = request.POST['password']
        user = User(name=name, email=email, phone=phone, address=address, password=password)
        try:
            oldUsers = User.objects.filter(email=email)
            if len(oldUsers) > 0:
                return render(request, 'register.html', {'error': 'Email already exists'})
            else:
                user.save()
                return redirect('login')
        except:
            return render(request, 'register.html', {'error': 'Something went wrong'})
    return render(request, 'register.html')

def logout(request):
    del request.session['user_id']
    return redirect('login')

def allproduct(request):
    products = Product.objects.all()
    if checkSession(request):
        return render(request, 'product.html', {'products': products})
    return redirect('login')

def filterproduct(request, id):
    products = Product.objects.filter(category=id)
    if checkSession(request):
        return render(request, 'product.html', {'products': products})
    return redirect('login')

def singleproduct(request, id):
    product = Product.objects.get(id=id)
    if checkSession(request):
        return render(request, 'singleproduct.html', {'product': product})
    return redirect('login')

def changepassword(request):
    if checkSession(request):
        if request.method == 'POST':
            oldpassword = request.POST['oldpassword']
            newpassword = request.POST['newpassword']
            confirmpassword = request.POST['confirmpassword']
            if newpassword != confirmpassword:
                return render(request, 'changepassword.html', {'error': 'Password does not match'})
            user = User.objects.get(id=request.session['user_id'])
            try:
                if user.password == oldpassword:
                    user.password = newpassword
                    user.save()
                    return redirect('logout')
                else:
                    return render(request, 'changepassword.html', {'error': 'Invalid Password'})
            except:
                return render(request, 'changepassword.html', {'error': 'Something went wrong'})
        return render(request, 'changepassword.html')
    return redirect('login')

def profile(request):
    user = User.objects.get(id=request.session['user_id'])
    if checkSession(request):
        return render(request, 'profile.html', {'user': user})
    if request.method == 'POST':
        name = request.POST['username']
        address = request.POST['address']
        user.name = name
        user.address = address
        try:
            user.save()
            return redirect('profile')
        except:
            return render(request, 'profile.html', {'error': 'Something went wrong'})
    return redirect('login')

def contactus(request):
    if request.method == 'POST':
        name = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone'] if 'phone' in request.POST else ''
        message = request.POST['message']
        contact = Contact(name=name, email=email, phone=phone, message=message)
        try:
            contact.save()
            return redirect('index')
        except:
            return render(request, 'contactus.html', {'error': 'Something went wrong'})
    return render(request, 'contactus.html')

def buyNow(request):
    if checkSession(request):
        user = User.objects.get(id=request.session['user_id'])
        if request.method == 'POST':
            product = Product.objects.get(id=request.POST['product_id'])
            quantity = int(request.POST['quantity'])
            if product.quantity < quantity:
                return render(request, 'singleproduct.html', {'product': product, 'error': 'Quantity not available'})
            request.session['product_id'] = product.id
            request.session['quantity'] = quantity
            request.session['user_id'] = user.id
            request.session['order_amount'] = quantity*product.price
            request.session['payment_method'] = 'Razorpay'
            return redirect('razorpayview')
    return redirect('login')

def razorpayView(request):
    currency = 'INR'
    amount = int(request.session['order_amount'])*100
    print(amount)
    # Create a Razorpay Order
    razorpay_order = client.order.create(dict(amount=amount,currency=currency,payment_capture='0'))
    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = 'http://127.0.0.1:8000/paymenthandler/'    
    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url    
    return render(request,'razorpayDemo.html',context=context)

@csrf_exempt
def paymenthandler(request):
    # only accept POST request.
    if request.method == "POST":
        print("IN POST")
        try:
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            
            print(payment_id)
            print(razorpay_order_id)
            print(signature)

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
 
            # verify the payment signature.
            result = client.utility.verify_payment_signature(params_dict)
            
            print("IN TRY")
            amount = int(request.session['order_amount'])*100  # Rs. 200
            # capture the payemt
            client.payment.capture(payment_id, amount)
            print(amount)

            #Order Save Code
            order = Order()
            product = Product.objects.get(id=request.session['product_id'])
            user = User.objects.get(id=request.session['user_id'])
            order.product_id = product
            order.product_qty = request.session['quantity']
            order.user_id = user
            order.order_amount = int(request.session['order_amount'])
            order.payment_method = request.session['payment_method']
            order.transaction_id = payment_id
            
            product.quantity = product.quantity-request.session['quantity']
            product.save()
            order.save()
            del request.session['product_id']
            del request.session['quantity']
            del request.session['order_amount']
            del request.session['payment_method']
            # render success page on successful caputre of payment
            return redirect('orderSuccessView')
        except Exception as e:
            print("IN EXCEPT")
            print(e)
            # if there is an error while capturing payment.
            return HttpResponseBadRequest()
    else:
       # if other than POST request is made.
        return HttpResponseBadRequest()

def successview(request):
    if checkSession(request):
        return render(request,'order_success.html')
    return redirect('login')

def myorders(request):
    if checkSession(request):
        user = User.objects.get(id=request.session['user_id'])
        orders = Order.objects.filter(user_id=user)
        myOrders = []
        for order in orders:
            product = Product.objects.get(id=order.product_id.id)
            myOrders.append({
                'productImage': product.img.url,
                'productName': product.name,
                'productQty': order.product_qty,
                'orderAmount': order.order_amount,
                'transactionId': order.transaction_id,
            })
        return render(request, 'myorders.html', {'myorders': myOrders})
    return redirect('login')

def searchview(request):
    word = request.GET.get('search')
    wordset = word.split(" ")
    products = Product.objects.all()
    searchProducts = []
    for product in products:
        for word in wordset:
            if word.lower() in product.name.lower():
                searchProducts.append(product)
    categories = Category.objects.all()
    for category in categories:
        for word in wordset:
            if word.lower() in category.name.lower():
                products = Product.objects.filter(category_id=category)
                for product in products:
                    searchProducts.append(product)
    return render(request, 'product.html', {'products': searchProducts})

def forgotpassword(request):
    if request.method == 'POST':
        print(request.POST)
        email = request.POST['email']
        try:
            print("1")
            user = User.objects.get(email=email)
            print("12")
            print(user)
            otp = random.randint(1000,9999)
            request.session['otp'] = otp
            request.session['email'] = email
            send_mail(
                'Password Reset',
                'Your OTP is ' + str(otp),
                'mayanprajapati007@gmail.com',
                [email],
                fail_silently=False,
            )
            return redirect('resetpassword')
        except Exception as e:
            print(e)
            return render(request, 'forgotpassword.html', {'error': 'Email not registered'})
    return render(request, 'forgotpassword.html')

def resetpassword(request):
    if request.session['otp'] and request.session['email']:    
        if request.method == 'POST':
            otp = request.POST['otp']
            email = request.session['email']
            if int(otp) == request.session['otp']:
                user = User.objects.get(email=email)
                send_mail(
                    'Password Reset',
                    'Your Password is ' + user.password,
                    'mayanprajapati007@gmail.com',
                    [email],
                    fail_silently=False,
                )
                del request.session['otp']
                del request.session['email']
                return redirect('login')
            else:
                return render(request, 'resetpassword.html', {'error': 'Invalid OTP'})
        return render(request, 'resetpassword.html')
    else:
        return redirect('forgotpassword')

