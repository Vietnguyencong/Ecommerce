from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import json
import datetime
from .uti import cookieCart, cartData, guest_checkout

# get request
def store(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {'products': products, 'items':items,'order': order, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)

def cart(request):# only for sign in user
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    
    context = {'items':items,'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    context = {'items':items,'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)

# post request 
# for authenticate user 
def updateItem(request):
    data= json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product= Product.objects.get(id=productId)
    order, created= Order.objects.get_or_create(customer = customer, complete = False)

    orderItem, created = OrderItem.objects.get_or_create(order= order, product=product)
    if (action == 'add'):
        orderItem.quantity = orderItem.quantity + 1
    elif action == 'remove':
        orderItem.quantity = orderItem.quantity -1 
    orderItem.save()
    if (orderItem.quantity <= 0):
        orderItem.delete()
    print("Action:", action)
    print("prpductid:", productId)
    return JsonResponse('Item was added', safe=False)

# for both authen and unauthen user 
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, complete=False)
        
    else:
        customer, order = guest_checkout(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    # if total == order.get_cart_total:
    order.complete = True
    order.save()
    if order.shipping :
        ShippingAddress.objects.create(
            customer = customer, 
            order = order, 
            address = data['shipping']['address'],
            city = data['shipping']['city'],
            state = data['shipping']['state'],
            zipcode = data['shipping']['zipcode'],
        )
    return JsonResponse('payment submitted .. ', safe=False)