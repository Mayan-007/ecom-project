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
        return User.objects.get(id=request.session['user_id'])
    elif request.session.has_key('vendor_id'):
        return Vendor.objects.get(id=request.session['vendor_id'])
    else:
        return False

def index(request):
    if checkSession(request): return render(request, 'index.html')
    return redirect('login')

def categories(request):
    categories = Category.objects.all()
    if checkSession(request):
        return render(request, 'categories.html', {'categories': categories})
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

def vendorLogin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            vendor = Vendor.objects.get(email=email)
            if vendor.password == password:
                request.session['vendor_id'] = vendor.id
                return redirect('index')
            else:
                return render(request, 'vendor_login.html', {'error': 'Invalid Password'})
        except:
            return render(request, 'vendor_login.html', {'error': 'Invalid Email'})
    return render(request, 'vendor_login.html')

def vendorRegister(request):
    if request.method == 'POST':
        name = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        password = request.POST['password']
        vendor = Vendor(name=name, email=email, phone=phone, address=address, password=password)
        try:
            oldVendors = Vendor.objects.filter(email=email)
            if len(oldVendors) > 0:
                return render(request, 'vendor_register.html', {'error': 'Email already exists'})
            else:
                vendor.save()
                return redirect('vendor_login')
        except:
            return render(request, 'vendor_register.html', {'error': 'Something went wrong'})
    return render(request, 'vendor_register.html')

def logout(request):
    if request.session.has_key('user_id'):
        del request.session['user_id']
    elif request.session.has_key('vendor_id'):
        del request.session['vendor_id']
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

def profile(request):
    user = checkSession(request)
    if user:
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

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
 
            # verify the payment signature.
            result = client.utility.verify_payment_signature(params_dict)
            amount = int(request.session['order_amount'])*100  # Rs. 200
            # capture the payemt
            client.payment.capture(payment_id, amount)

            #Order Save Code
            order = Order()
            user = User.objects.get(id=request.session['user_id'])
            order.user_id = user
            order.user_name = request.session['user_name']
            order.user_email = request.session['user_email']
            order.user_phone = request.session['user_phone']
            order.shipping_address = request.session['shipping_address']
            order.order_amount = int(request.session['order_amount'])
            order.payment_method = request.session['payment_method']
            order.transaction_id = payment_id
            order.save()
            
            cartItems = Cart.objects.filter(user_id=user)
            for cartItem in cartItems:
                cartItem.order_id = order
                product = Product.objects.get(id=cartItem.product_id.id)
                product.quantity = product.quantity - cartItem.product_qty
                cartItem.save()
            
            del request.session['user_name']
            del request.session['user_email']
            del request.session['user_phone']
            del request.session['shipping_address']
            del request.session['order_amount']
            del request.session['payment_method']
            # render success page on successful caputre of payment
            return redirect('orderSuccessView')
        except Exception as e:
            print(e)
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
            print(order.id)
            cart = Cart.objects.filter(order_id=order.id)
            for cartItem in cart:
                product = Product.objects.get(id=cartItem.product_id.id)
                myOrders.append({
                    'productImage': product.img.url,
                    'productName': product.name,
                    'productQty': cartItem.product_qty,
                    'orderAmount': order.order_amount,
                    'transactionId': order.transaction_id,
                })
        return render(request, 'myorders.html', {'myorders': myOrders})
    return redirect('login')

def searchview(request):
    if checkSession(request):
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
    return redirect('login')

def forgotpassword(request):
    if request.method == 'POST':
        print(request.POST)
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            if user:
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
            vendor = Vendor.objects.get(email=email)
            if vendor:
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

def cart(request):
    user = checkSession(request)
    success = False
    if user:
        if request.method == 'POST':
            productId = request.POST['product_id']
            productQty = request.POST['quantity']
            product = Product.objects.get(id=productId)
            cart = Cart()
            cart.product_id = product
            cart.product_qty = int(productQty)
            cart.user_id = user
            cart.order_id = None
            cart.cart_amount = int(productQty)*int(product.price)
            cart.save()
            success = 'Product added to cart successfully'
        cart = Cart.objects.filter(user_id=user)
        if len(cart) == 0:
            return render(request, 'cart.html', {'isEmptyCart': True})
        cartItems = []
        for item in cart:
            product = Product.objects.get(id=item.product_id.id)
            cartItems.append({
                'productImage': product.img.url,
                'productName': product.name,
                'productQty': item.product_qty,
                'productTotalPrice': item.product_qty*product.price,
                'id': item.id,
            })
        if request.session.has_key('message'):
            success = request.session['message']
            del request.session['message']
        if success:
            return render(request, 'cart.html', {'cartItems': cartItems, 'success': success})
        return render(request, 'cart.html', {'cartItems': cartItems})
    return redirect('login')

def deleteCartItem(request, id):
    if checkSession(request):
        cartItem = Cart.objects.get(id=id)
        cartItem.delete()
        request.session['message'] = 'Product deleted from cart successfully'
        return redirect('cart')
    return redirect('login')

def addproduct(request):
    if request.session.has_key('vendor_id'):
        vendor = Vendor.objects.get(id=request.session['vendor_id'])
        categories = Category.objects.all()
        if request.method == 'POST':
            name = request.POST['productname']
            img = request.FILES['productimg']
            price = request.POST['productprice']
            quantity = request.POST['productquantity']
            category = Category.objects.get(id=request.POST['productcategory'])
            description = request.POST['productdescription']
            product = Product(
                vendor_id=vendor,
                name=name,
                img=img,
                price=price,
                category=category,
                product_desc=description,
                quantity=quantity,
            )
            product.save()
            return render(request, 'addproduct.html', {'categories': categories, 'message': 'Product added successfully'})
        return render(request, 'addproduct.html', {'categories': categories})
    return redirect('vendor_login')

def checkout(request):
    user = checkSession(request)
    if user:
        cartItems = Cart.objects.filter(user_id=user)
        if request.method == 'POST':
            request.session['user_name'] = request.POST['username']
            request.session['user_email'] = request.POST['email']
            request.session['user_phone'] = request.POST['phone']
            request.session['shipping_address'] = request.POST['address']
            order_amount = 0
            for cart in cartItems:
                order_amount += cart.cart_amount
            request.session['order_amount'] = order_amount
            request.session['payment_method'] = 'Razorpay'
            return redirect('razorpayview')
        return render(request, 'checkout.html', {'user': user})
    return redirect('login')

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