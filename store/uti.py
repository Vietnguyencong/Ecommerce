import json
from .models import *

def cookieCart(request):
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}
        print('cart:', cart)
        items = []
        order = {'get_cart_total': 0, 'get_total_items': 0, 'shipping':False}
        cartItems = order['get_total_items']

        for i in cart :
            # prevent the product that has been removed 
            try:
                cartItems += cart [i]['quantity']
                product = Product.objects.get(id = i)
                total = cart[i]['quantity'] * product.price
                order['get_cart_total'] += total
                order['get_total_items'] += cart[i]['quantity']
                item = {
                    'product':{
                        'id': product.id, 
                        'name': product.name, 
                        'price': product.price, 
                        'imageUrl': product.imageUrl, 
                        'digital': product.digital,
                    },
                    'quantity': cart[i]['quantity'],
                    'get_sub_total': total, 
                }
                items.append(item)
                if item['product']['digital'] == False:
                    order['shipping'] = True
            except:
                pass
        return  {'items':items,'order': order, 'cartItems': cartItems}
    


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        items = order.orderitem_set.all()
        cartItems = order.get_total_items 
    else:
        cookieData = cookieCart(request)
        items = cookieData['items']
        order = cookieData['order']
        cartItems = cookieData['cartItems']

    return  {'items':items,'order': order, 'cartItems': cartItems}

def guest_checkout(request, data):
    print("user is not login")
    print('COOKIES:', request.COOKIES)
    name = data['form']['name']
    email = data['form']['email']
    customer,created = Customer.objects.get_or_create( email = email )
    customer.name  = name; 
    customer.save()

    order = Order.objects.create(customer = customer, complete =False)
    cart = cookieCart(request)
    items = cart['items']
    for item in items: 
        product = Product.objects.get(id = item['product']['id'])
        orderItem =  OrderItem.objects.create(
            product = product, 
            order = order,
            quantity = item['quantity'],
        )
    return (customer , order)