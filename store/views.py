from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import *
from django.contrib.auth import authenticate,login,logout
from .utils import cookieCart,cartData,guestOrder
import json
import datetime
from django.contrib.auth.models import User


# Create your views here.

def signup(request):
    if request.method=="POST":
        name=request.POST['name']
        password=request.POST['pass1']
        confirm_password=request.POST['pass2']
        if password!=confirm_password:
            messages.warning(request,"Password is Not Matching")
            return render(request,'store/signup.html')  
        email=request.POST['name'] +"@gmail.com"
        user = User.objects.create_user(name,email,password)
        #user.is_active=False
        user.save()
        customer,created = Customer.objects.get_or_create(user=user,name=name,email=email)
        customer.save()
        return redirect("/")
    return render(request,"store/signup.html")

def handlelogin(request):
    if request.method=="POST":

        username=request.POST['name']
        userpassword=request.POST['pass1']
        myuser=authenticate(username=username,password=userpassword)

        if myuser is not None:
            login(request,myuser)
            #messages.success(request,"Login Success")
            return redirect('/store')

        else:
            #messages.error(request,"Invalid Credentials")
            return redirect("/")

    return render(request,'store/login.html')  

    

def handlelogout(request):
    logout(request)
    #messages.info(request,"Logout Success")
    return render(request,'store/login.html')


def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    
    products = Product.objects.all()
    context={'products': products, 'cartItems':cartItems}
    return render(request,'store/store.html',context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
        
    context={'items':items, 'order':order,'cartItems':cartItems}
    return render(request,'store/cart.html',context)


def checkout(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context={'items':items, 'order':order, 'cartItems': cartItems}
    
    return render(request,'store/checkout.html',context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:',action)
    print('productId:',productId)

    customer=request.user.customer
    product = Product.objects.get(id=productId)
    order,created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem,created = OrderItem.objects.get_or_create(order = order, product = product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()


    return JsonResponse('Item was added', safe=False)

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def processOrder(request):
        transaction_id = datetime.datetime.now().timestamp()
        data = json.loads(request.body)

        if request.user.is_authenticated:
            customer = request.user.customer
            order,created = Order.objects.get_or_create(customer = customer, complete = False)
            
            
        else:
            customer,order = guestOrder(request,data)

        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == float(order.get_cart_total):
            order.complete = True
        order.save()

        
        if order.shipping == True:
            ShippingAddress.objects.create(
                customer = customer,
                order = order,
                address = data['shipping']['address'],
                city = data['shipping']['city'],
                state = data['shipping']['state'],
                zipcode = data['shipping']['zipcode'],
            )
        return JsonResponse('Payment complete', safe=False)

def success(request):
    return render(request,'store/success.html')