import json
from . models import *
import uuid

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    print('Cart:', cart)
    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0}

    # Generate a unique guest order ID (if not already present in cookies)
    guest_order_id = request.COOKIES.get('guest_order_id', str(uuid.uuid4()))

    order['id'] = guest_order_id  # Store the temporary order ID for guest users

    cartItems = order['get_cart_items']

    for i in cart:
        try:
            cartItems += cart[i]["quantity"]

            product = D_Product.objects.get(id=i)
            total = (product.price * cart[i]["quantity"])

            order['get_cart_total'] += total
            order['subtotal'] = order['get_cart_total']
            order['get_cart_items'] += cart[i]["quantity"]

            item = {
                'product': {'id': product.id, 'name': product.name, 'price': product.price, 'imageURL': product.imageURL},
                'quantity': cart[i]['quantity'],
                'size': cart[i]['size'],
                'get_total': total,
            }
            items.append(item)
        except:
            pass

    response = {'cartItems': cartItems, 'order': order, 'items': items}

    return response

def cartData(request):
    if request.user.is_authenticated:
        # customer = request.user.g_customer
        customer, created = G_Customer.objects.get_or_create(user=request.user)
        order, created = H_Order.objects.get_or_create(customer=customer, complete=False)
        items = order.i_orderitem_set.all()
        # cartItems = order.get_cart_items
        cartItems = sum([item.quantity for item in items])
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
    return {'cartItems': cartItems, 'order': order, 'items': items}

def guestOrder(request, data):
    print('user is not loged in')
    print('Cookies', request.COOKIES)
    name = data['form']['name']
    surname = data['form']['surname']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = G_Customer.objects.get_or_create(
        email=email,
    )
    customer.name = name
    customer.surname = surname
    customer.save()

    order = H_Order.objects.create(
        customer=customer,
        complete=False,
    )
    for item in items:
        product = D_Product.objects.get(id=item['product']['id'])

        orderItem = I_OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity'],
            size=item['size'],
        )

    return customer, order
