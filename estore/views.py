from estore.filters import ProductFilter
from django.shortcuts import render, redirect
from .models import*
from django.http import JsonResponse
import json
import datetime
from . utils import cookieCart, cartData, guestOrder
from . forms import CreateUserForm, CustomerForm
from django.contrib.auth import authenticate, login, logout

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group


# Create your views here.
def store(request):
   data = cartData(request)
   cartItems = data['cartItems']
  
   products = Product.objects.all()
   myFilter = ProductFilter(request.GET, queryset=products)
   products = myFilter.qs
   
   context = {'products':products, 'cartItems':cartItems, 'myFilter':myFilter}
   return render(request, 'estore/store.html', context)


def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'items':items, 'order':order, 'cartItems': cartItems}
    return render(request, 'estore/cart.html', context)

def about(request):
    return render(request, 'estore/about.html')


    
def checkout(request):
   
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'estore/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print ('Action:', action)
    print ('productId:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    
    orderItem.save()
    
    if orderItem.quantity <=0:
        orderItem.delete()
    return JsonResponse('Item added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
       
    else:
        customer,order = guestOrder(request, data)

    total = float (data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.cart_total:
            order.complete = True
    order.save()
    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],

        )

    return JsonResponse('Payment complete', safe=False)


def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            Customer.objects.create(
                user=user,
                name = username,
                email = email,
            )
          
            messages.success(
                request, 'Account successfully created for ' + username)
            return redirect('login')
    context = {'form': form}
    return render(request, 'estore/register.html', context)


def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('store')
        else:
            messages.info(request, 'Username or Password incorrect')

    context = {}
    return render(request, 'estore/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('store')
