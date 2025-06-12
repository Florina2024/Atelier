import json
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from Atelier_Shop.models import *
from Product.models import *
from django.http import JsonResponse, HttpResponseRedirect
import datetime
from .utils import cookieCart
from .utils import cartData, guestOrder
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from uuid import UUID
import hashlib
import hmac
from django.urls import reverse


def shop(request):
    cat = request.GET.get('category', '')  # Kategoria që mund të jetë bosh ose e zgjedhur
    categories = A_Category.objects.all()  # Merrni të gjitha kategoritë
    products = D_Product.objects.all()  # Merrni të gjitha produktet

    print("Selected category:", cat)  # Shtoni këtë për të kontrolluar kategorinë që po përdorni

    # Nëse ka një kategori të zgjedhur, filtroni produktet sipas saj
    if cat and cat != "all":
        products = products.filter(subcategory__category__id=cat)
        print("Filtered products:", products)  # Shihni produktet pas filtrimit

    # Krijoni listën e produkteve për t'u kthyer si JSON
    product_data = []
    for product in products:
        product_data.append({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'main_image': product.main_image.url if product.main_image else '',
            'category': product.subcategory.category.category if product.subcategory and product.subcategory.category else 'No Category'
        })

    total_new_items = products.count()
    data = cartData(request)
    cartItems = data['cartItems']

    # Kthejeni përgjigjen si JSON për kërkesën AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'products': product_data,
            'total_new_items': total_new_items
        })

    # Për dërgim në template
    context = {
        'categories': categories,  # Dërgoni të gjitha kategoritë
        'products': products,  # Dërgoni produktet e filtruar
        'category': cat,
        'total_new_items': total_new_items,
        'cartItems': cartItems
    }

    return render(request, 'shop.html', context)

def collection(request, col=None):
    if request.method == 'GET':
        categories = A_Category.objects.all()
        subcategories = B_Subcategory.objects.all()
        collections = C_Collection.objects.all()
        menu = B_Main_Product.objects.all()
        footer = Z_Contact.objects.all()
        footer1 = footer[0] if footer else None
        gifts = C_Gift.objects.all()

        data = cartData(request)
        cartItems = data['cartItems']

        context = {'categories': categories, 'subcategories': subcategories, 'collections': collections,
                    'collection': col, 'menu': menu,
                   'cartItems': cartItems, 'gifts': gifts, 'collection': col, 'footer': footer1}
        return render(request, 'collections.html', context)

from django.http import JsonResponse

def new_arrivals(request):
    categories = A_Category.objects.all()
    category_id = request.GET.get('category', 'all')

    if category_id == "all":
        new_products = D_Product.objects.filter(is_new=True).order_by('-id')
    else:
        new_products = D_Product.objects.filter(subcategory__category__id=category_id, is_new=True).order_by('-id')

    total_new_items = new_products.count()
    data = cartData(request)
    cartItems = data['cartItems']

    # Nëse është AJAX request, kthe JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        products_data = [
            {
                "name": product.name,
                "price": product.price,
                "main_image": product.main_image.url,
                "category": product.subcategory.category.id
            }
            for product in new_products
        ]
        return JsonResponse({"products": products_data})

    # Përndryshe, kthe template normal
    return render(request, 'new_arrivals.html', {
        'new_products': new_products,
        'categories': categories,
        'total_new_items': total_new_items,
        'cartItems': cartItems
    })

def category_page(request, category_id):
    # Get the category object using the category_id
    category = get_object_or_404(A_Category, id=category_id)

    # Retrieve the collections for this category
    collections = C_Collection.objects.filter(category=category)

    # Retrieve the products for this category
    category_products = D_Product.objects.filter(subcategory__category=category)
    data = cartData(request)
    cartItems = data['cartItems']

    return render(request, 'category.html', {
        'category': category,
        'collections': collections,
        'category_products': category_products,
        'cartItems': cartItems
    })

def collection_page(request, collection_slug):
    collection = get_object_or_404(C_Collection, slug=collection_slug)
    products = collection.products.all()  # Merrni të gjitha produktet që janë të lidhura me këtë koleksion
    return render(request, 'collection_page.html', {'collection': collection, 'products': products})

def gifts_under_100(request):
    categories = A_Category.objects.all()
    category_id = request.GET.get('category', 'all')

    # Filtrimi i produkteve që janë mes 50$ dhe 100$
    if category_id == "all":
        under_100_products = D_Product.objects.filter(price__gte=0, price__lte=100).order_by('-id')
    else:
        under_100_products = D_Product.objects.filter(
            subcategory__category__id=category_id, price__gte=50, price__lte=100
        ).order_by('-id')

    total_new_items = under_100_products.count()
    data = cartData(request)
    cartItems = data['cartItems']

    # Filtrimi i kategorive që kanë të paktën një produkt në intervalin 50$ - 100$
    categories_with_products = [
        category for category in categories if D_Product.objects.filter(subcategory__category=category, price__gte=50, price__lte=100).exists()
    ]

    # Nëse është AJAX request, kthe JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        products_data = [
            {
                "name": product.name,
                "price": product.price,
                "main_image": product.imageURL,  # Supozojmë që 'imageURL' është URL-ja e imazhit
                "category": product.subcategory.category.id
            }
            for product in under_100_products
        ]
        return JsonResponse({
            "products": products_data,
            "categories": [{'id': category.id, 'category': category.category} for category in categories_with_products]
        })

    # Përndryshe, kthe template normal
    return render(request, 'gifts_under_100.html', {
        'under_100_products': under_100_products,
        'categories': categories_with_products,
        'total_new_items': total_new_items,
        'cartItems': cartItems
    })
def gifts_100_150(request):
    categories = A_Category.objects.all()
    category_id = request.GET.get('category', 'all')

    # Filtrimi i produkteve që janë mes 50$ dhe 100$
    if category_id == "all":
        between_100_150_products = D_Product.objects.filter(price__gte=100, price__lte=150).order_by('-id')
    else:
        between_100_150_products = D_Product.objects.filter(
            subcategory__category__id=category_id, price__gte=50, price__lte=100
        ).order_by('-id')

    total_new_items = between_100_150_products.count()
    data = cartData(request)
    cartItems = data['cartItems']

    # Filtrimi i kategorive që kanë të paktën një produkt në intervalin 50$ - 100$
    categories_with_products = [
        category for category in categories if D_Product.objects.filter(subcategory__category=category, price__gte=100, price__lte=150).exists()
    ]

    # Nëse është AJAX request, kthe JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        products_data = [
            {
                "name": product.name,
                "price": product.price,
                "main_image": product.imageURL,  # Supozojmë që 'imageURL' është URL-ja e imazhit
                "category": product.subcategory.category.id
            }
            for product in between_100_150_products
        ]
        return JsonResponse({
            "products": products_data,
            "categories": [{'id': category.id, 'category': category.category} for category in categories_with_products]
        })

    # Përndryshe, kthe template normal
    return render(request, 'gifts_between_100_150.html', {
        'between_100_150_products': between_100_150_products,
        'categories': categories_with_products,
        'total_new_items': total_new_items,
        'cartItems': cartItems
    })
def gifts_over_150(request):
    categories = A_Category.objects.all()
    category_id = request.GET.get('category', 'all')

    # Filtrimi i produkteve që janë mbi 150$
    if category_id == "all":
        over_150_products = D_Product.objects.filter(price__gt=150).order_by('-id')  # 'price__gt' për mbi 150$
    else:
        over_150_products = D_Product.objects.filter(
            subcategory__category__id=category_id, price__gt=150
        ).order_by('-id')

    total_new_items = over_150_products.count()
    data = cartData(request)
    cartItems = data['cartItems']

    # Filtrimi i kategorive që kanë të paktën një produkt mbi 150$
    categories_with_products = [
        category for category in categories if D_Product.objects.filter(subcategory__category=category, price__gt=150).exists()
    ]

    # Nëse është AJAX request, kthe JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        products_data = [
            {
                "name": product.name,
                "price": product.price,
                "main_image": product.imageURL,  # Supozojmë që 'imageURL' është URL-ja e imazhit
                "category": product.subcategory.category.id
            }
            for product in over_150_products
        ]
        return JsonResponse({
            "products": products_data,
            "categories": [{'id': category.id, 'category': category.category} for category in categories_with_products]
        })

    # Përndryshe, kthe template normal
    return render(request, 'gifts_over_150.html', {
        'over_150_products': over_150_products,
        'categories': categories_with_products,
        'total_new_items': total_new_items,
        'cartItems': cartItems
    })

def product(request, product_id):
    if request.method == 'GET':
        categories = A_Category.objects.all()
        subcategories = B_Subcategory.objects.all()
        collections = C_Collection.objects.all()
        shipping = S_Shipping.objects.all()
        shipping1 = shipping[0] if shipping else None
        latest_col = C_Collection.objects.last()
        footer = Z_Contact.objects.all()
        footer1 = footer[0] if footer else None

        product = get_object_or_404(D_Product, id=product_id)
        # Merrni galerinë, ngjyrat dhe madhësitë për këtë produkt
        gallery = E_Product_Gallery.objects.filter(product=product)
        sizes = E_Product_Size.objects.filter(product=product)
        colors = E_Product_Color.objects.filter(product=product).select_related('color')
        latest_collection = C_Collection.objects.order_by('-created_at').first()
        similar_products = D_Product.objects.filter(subcategory=product.subcategory).exclude(id=product.id)[:3]
        # Recently viewed logic
        recently_viewed = request.session.get('recently_viewed', [])
        if product_id in recently_viewed:
            recently_viewed.remove(product_id)
        recently_viewed.insert(0, product_id)
        if len(recently_viewed) > 5:  # Limito në 6 produkte
            recently_viewed = recently_viewed[:4]
        request.session['recently_viewed'] = recently_viewed
        recently_viewed_products = D_Product.objects.filter(id__in=recently_viewed).exclude(id=product.id)

        data = cartData(request)
        cartItems = data['cartItems']
        order = data['order']
        items = data['items']

        products = D_Product.objects.filter(subcategory_id=product.subcategory.id)
        context = {'categories': categories, 'subcategories': subcategories, 'collections': collections, 'product': product,
                   'shipping': shipping1, 'colors': colors, 'gallery': gallery, 'latest_col': latest_col, 'products': products, 'sizes': sizes,
                   'cartItems': cartItems, 'items':items, 'latest_collection': latest_collection, 'recently_viewed_products':recently_viewed_products, 'similar_products':similar_products, 'footer': footer1}
        return render(request, 'product_details.html', context)

def addToCart(request):
    if request.method == 'GET':
        categories = A_Category.objects.all()
        subcategories = B_Subcategory.objects.all()
        collections = reversed(C_Collection.objects.all())
        shipping = S_Shipping.objects.all()
        shipping1 = shipping[0] if shipping else None
        footer = Z_Contact.objects.all()
        footer1 = footer[0] if footer else None
        latest_collection = C_Collection.objects.order_by('-created_at').first()

        latest_col = C_Collection.objects.last()

        data = cartData(request)
        cartItems = data['cartItems']
        order = data['order']
        items = data['items']

        all_cupons = K_Cupon.objects.all()
        amount_in_cents = 0
        if hasattr(order, 'get_cart_total') and order.get_cart_total:
            amount_in_cents = int(float(order.get_cart_total) * 100)

        context = {'categories': categories, 'subcategories': subcategories, 'collections': collections, 'product': product, 'shipping': shipping1,
                   'latest_col': latest_col, 'latest_collection':latest_collection, 'cartItems': cartItems, 'items': items, 'order': order, 'footer': footer1, 'amount_in_cents':amount_in_cents, 'all_cupons': all_cupons}
        return render(request, 'addToCart.html', context)

def cart_modal(request):
    if request.method == 'GET':
        categories = A_Category.objects.all()
        subcategories = B_Subcategory.objects.all()
        collections = reversed(C_Collection.objects.all())
        shipping = S_Shipping.objects.all()
        shipping1 = shipping[0] if shipping else None
        footer = Z_Contact.objects.all()
        footer1 = footer[0] if footer else None
        latest_collection = C_Collection.objects.order_by('-created_at').first()

        latest_col = C_Collection.objects.last()

        data = cartData(request)
        cartItems = data['cartItems']
        order = data['order']
        items = data['items']
        total = order.get_cart_total if order else 0

        all_cupons = K_Cupon.objects.all()

        context = {'categories': categories, 'subcategories': subcategories, 'collections': collections, 'product': product, 'shipping': shipping1,
                   'latest_col': latest_col, 'latest_collection':latest_collection, 'total': total, 'cartItems': cartItems, 'items': items, 'order': order, 'footer': footer1, 'all_cupons': all_cupons}
        return render(request, 'cart_modal.html', context)

@csrf_protect
def apply_cupon(request):
    if request.method == 'POST':
        apply = request.POST
        code = apply['code']
        cupon = K_Cupon.objects.get(code=code)

        if request.user.is_authenticated:
            customer = request.user.g_customer
            order = H_Order.objects.get(customer=customer, complete=False)

            discount = float(order.get_cart_total - (order.get_cart_total * cupon.discount) / 100)
            c_order = H_Order.objects.get(id=order.id)

            InsertCuponOrder = K_Cupon_Order(order=c_order, discount=discount)
            InsertCuponOrder.save()

            return HttpResponseRedirect('/addToCart/')

        else:
            cookieData = cookieCart(request)
            cartItems = cookieData['cartItems']
            order = cookieData['order']
            items = cookieData['items']

            discount = float(order.get_cart_total - (order.get_cart_total * cupon.discount) / 100)
            InsertCuponOrder = K_Cupon_Order(order=order, discount=discount)
            InsertCuponOrder.save()

            return HttpResponseRedirect('/addToCart/')

def checkout(request):
    if request.method == 'GET':
        categories = A_Category.objects.all()
        subcategories = B_Subcategory.objects.all()
        collections = reversed(C_Collection.objects.all())
        shipping = S_Shipping.objects.all()
        shipping1 = shipping[0] if shipping else None
        latest_col = C_Collection.objects.last()
        footer = Z_Contact.objects.all()
        footer1 = footer[0] if footer else None
        latest_collection = C_Collection.objects.order_by('-created_at').first()

        data = cartData(request)
        cartItems = data['cartItems']
        order = data['order']
        items = data['items']

        # Kontrolloni nëse order është instancë e H_Order
        if isinstance(order, H_Order):
            # Përdorim instancën e order pa nevojën për 'get()'
            response = render(request, 'checkout.html', {
                'categories': categories,
                'subcategories': subcategories,
                'collections': collections,
                'shipping': shipping1,
                'latest_col': latest_col,
                'latest_collection':latest_collection,
                'cartItems': cartItems,
                'items': items,
                'order': order,  # Direkte përdorim instancën e order
                'footer': footer1,
                'coupons': K_Cupon.objects.all()
            })
            return response
        elif isinstance(order, dict) and 'id' in order:
            # Për përdoruesit guest, ruajmë ID-në në cookies
            response = render(request, 'checkout.html', {
                'categories': categories,
                'subcategories': subcategories,
                'collections': collections,
                'shipping': shipping1,
                'latest_col': latest_col,
                'cartItems': cartItems,
                'items': items,
                'order': order,  # Përdorim fjalorin
                'footer': footer1,
                'coupons': K_Cupon.objects.all()
            })
            response.set_cookie('guest_order_id', order['id'])
            return response
        else:
            # Nëse 'order' nuk është instancë e H_Order dhe as fjalor, mund të bëni ndonjë verifikim tjetër këtu
            response = render(request, 'checkout.html', {
                'categories': categories,
                'subcategories': subcategories,
                'collections': collections,
                'shipping': shipping1,
                'latest_col': latest_col,
                'cartItems': cartItems,
                'items': items,
                'order': None,  # Nëse ka ndodhur një gabim me 'order'
                'footer': footer1,
                'coupons': K_Cupon.objects.all()
            })
            return response

from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse

# @csrf_protect
# def update_item(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             productId = data.get('productId')  # Përdor `.get()` për të shmangur KeyError
#             action = data.get('action')
#             size = data.get('size', None)  # Merr size ose vendos None si default
#
#             print(f"Received: Product ID: {productId}, Action: {action}")
#             print('Size:', size)
#
#             customer = request.user.g_customer
#             product = D_Product.objects.get(id=productId)
#             order, created = H_Order.objects.get_or_create(customer=customer, complete=False)
#
#             # Sigurohu që size nuk është bosh ose None
#             if size:
#                 orderItem, created = I_OrderItem.objects.get_or_create(order=order, product=product, size=size)
#             else:
#                 orderItem, created = I_OrderItem.objects.get_or_create(order=order, product=product)
#
#             if action == 'add':
#                 orderItem.quantity += 1
#             elif action == 'remove':
#                 orderItem.quantity -= 1
#
#             orderItem.save()
#
#             if orderItem.quantity <= 0:
#                 orderItem.delete()
#
#             return JsonResponse({'message': 'Item updated successfully'}, status=200)
#
#         except Exception as e:
#             print(f"Error: {str(e)}")
#             return JsonResponse({'error': str(e)}, status=500)
#
#     return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def update_item(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            productId = data.get('productId')
            action = data.get('action')
            size = data.get('size')
            color = data.get('color')

            product = D_Product.objects.get(id=productId)

            if request.user.is_authenticated:
                customer = G_Customer.objects.get(user=request.user)
                order, created = H_Order.objects.get_or_create(customer=customer, complete=False)
            else:
                session_key = request.session.session_key
                if not session_key:
                    request.session.create()
                    session_key = request.session.session_key

                order, created = H_Order.objects.get_or_create(session_key=session_key, complete=False)

            order_item, created = I_OrderItem.objects.get_or_create(order=order, product=product, size=size, color=color)

            if action == 'add':
                order_item.quantity += 1
                order_item.save()
                print(f"Added one: New quantity = {order_item.quantity}")
            elif action == 'remove':
                order_item.quantity -= 1
                if order_item.quantity <= 0:
                    order_item.delete()
                    print("Order item deleted because quantity <= 0")
                else:
                    order_item.save()
                    print(f"Removed one: New quantity = {order_item.quantity}")

            return JsonResponse({
                'message': 'Quantity updated',
                'quantity': order_item.quantity if not (action == 'remove' and order_item.quantity <= 0) else 0,
                'cart_total': order.get_cart_total()
            })
        except Exception as e:
            print("Error in update_item:", e)
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def update_wishlist(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('productId')
        action = data.get('action')

        wishlist = request.session.get('wishlist', [])

        if action == 'add' and product_id not in wishlist:
            wishlist.append(product_id)
        elif action == 'remove' and product_id in wishlist:
            wishlist.remove(product_id)

        request.session['wishlist'] = wishlist
        request.session.modified = True

        return JsonResponse({
            'product_count': len(wishlist),
            'message': 'Wishlist updated'
        })

    return JsonResponse({'error': 'Invalid request method'}, status=405)
def get_wishlist_items(request):
    wishlist = request.session.get('wishlist', [])
    products = []

    for pid in wishlist:
        product = get_object_or_404(D_Product, pk=pid)
        products.append({
            'id': product.id,
            'title': product.title,
            'price': product.price,
            'image_url': product.image.url if product.image else '',
            # Shto fushat që dëshiron të shfaqësh
        })

    return JsonResponse({'products': products})

@csrf_exempt
def process_cupon(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        print(data['cuponForm']['discount'])
        return JsonResponse('Payment Completed', safe=False)
    else:
        print('Guest User: ' + data['cuponForm']['discount'] + ', ' + data['cuponForm']['total'])
        code = data['cuponForm']['discount']
        total = float(data['cuponForm']['total'])

        cupon = K_Cupon.objects.get(code=code)
        discount = float(total - (total * cupon.discount) / 100)

        context = {'discount': discount}

        return JsonResponse(context, safe=False)

def checkout_process(request, cupon):
    if request.method == 'GET':
        categories = A_Category.objects.all()
        subcategories = B_Subcategory.objects.all()
        collections = reversed(C_Collection.objects.all())
        menu = E_Menu_Product.objects.all()
        shipping = S_Shipping.objects.all()
        shipping1 = shipping[0]
        latest_col = C_Collection.objects.last()
        marque_all = A_Notification.objects.all()
        footer = Z_Contact.objects.all()
        footer1 = footer[0]

        shipping_fee = 10
        coupons = K_Cupon.objects.all()

        marque = marque_all[0]

        data = cartData(request)
        cartItems = data['cartItems']
        order = data['order']
        items = data['items']

        cupon = K_Cupon.objects.get(code=cupon)

        if request.user.is_authenticated:
            customer = request.user.g_customer
            order = H_Order.objects.get(customer=customer, complete=False)

            discount = (order.get_cart_total * cupon.discount) / 100
            new_total = float(order.get_cart_total - discount) +  shipping_fee
            c_order = H_Order.objects.get(id=order.id)

            InsertCuponOrder = K_Cupon_Order(order=c_order, discount=new_total)
            InsertCuponOrder.save()
            context = {'categories': categories, 'subcategories': subcategories, 'collections': collections,
                       'menu': menu, 'product': product, 'shipping': shipping1,
                       'latest_col': latest_col, 'cartItems': cartItems, 'items': items, 'order': order,
                       'marque': marque, 'footer': footer1, 'cupon': cupon,
                       'discount': discount, 'new_total': new_total, 'coupons': coupons}
            return render(request, 'checkout.html', context)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()

            order = H_Order.objects.filter(session_key=session_key, complete=False).first()
            items = order.i_orderitem_set.all() if order else []
            cartItems = sum([item.quantity for item in items]) if order else 0
            total_order = float(order['get_cart_total'])
            discount = float((total_order * cupon.discount) / 100)
            new_total = float(total_order - discount) +  shipping_fee

            context = {'categories': categories, 'subcategories': subcategories, 'collections': collections, 'menu': menu, 'product': product, 'shipping': shipping1,
                       'latest_col': latest_col, 'cartItems': cartItems, 'items': items, 'order': order, 'marque': marque, 'footer': footer1, 'cupon': cupon,
                       'discount': discount, 'new_total': new_total, 'coupons': coupons}
            return render(request, 'checkout.html', context)

@csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    shipping_fee = 10
    if request.user.is_authenticated:
        customer = request.user.g_customer
        order, created = H_Order.objects.get_or_create(customer=customer, complete=False)
        print("Order created:", created)  # <-- Kontrollo nëse krijohet një order
        print("Order ID:", order.id)

    else:
        customer, order = guestOrder(request, data)
        print("Guest Order ID:", order.id)

    cupon_email = ''
    if data['form']['coupon'] == '':

        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == float(order.get_cart_total) + shipping_fee :
            order.complete = True
            order.total = total
        order.save()

    else:
        total = float(data['form']['total'])
        order.transaction_id = transaction_id
        cupon = K_Cupon.objects.get(code=data['form']['coupon'])
        orders = I_OrderItem.objects.filter(order_id=order.id)
        total_orders = 0
        for o in orders:
            total_orders = total_orders + o.get_total
        if total == float(total_orders - (total_orders * cupon.discount)/100) + shipping_fee:
            order.complete = True
            order.total = total
            order.save()

        cupon_discount = cupon.discount
        cupon_code = cupon.code
        cupon_email = '\n\nApplied Cupon: \n' + 'Cupon Code: ' + cupon_code + ', Discount: ' + str(cupon_discount) + '%'

    J_ShippingAddres.objects.create(
        customer=customer,
        order=order,
        phone=data['shipping']['phone'],
        email=customer.email,
        address=data['shipping']['address'],
        city=data['shipping']['city'],
        state=data['shipping']['state'],
        zipcode=data['shipping']['zipcode'],
        payment_method=data['shipping']['payment_method'],
        coupon=data['form']['coupon']
    )
    # Prepare email content for admin
    email_content = ''
    if I_OrderItem.objects.filter(order_id=order.id):
        orders = I_OrderItem.objects.filter(order_id=order.id)
        for o in orders:
            email_content = f'\n\nProduct: {o.product.name}\nQuantity: {o.quantity}\nSize: {o.size}\nColor: {o.color}\nPrice: {o.product.price}€\nSubtotal: {o.get_total}€' + email_content
    subject = 'Zanafeel - New Order'
    full_message = f'You have a new order:\n\nName Surname: {customer.name} {customer.surname}\nOrder ID: {order.id}\nEmail: {customer.email}\nPhone Number: {data["shipping"]["phone"]}' \
                  f'\nAddress: {data["shipping"]["address"]}\nCity: {data["shipping"]["city"]}\nState: {data["shipping"]["state"]}\nZipcode: {data["shipping"]["zipcode"]}' \
                  f'\nPayment Method: {data["shipping"]["payment_method"]}{email_content}{cupon_email}\n\nOrder Total Price: {total}€'

    try:
        send_mail(subject,
                  full_message,
                  settings.EMAIL_HOST_USER,
                  ['jemisha.florina@gmail.com'],
                  fail_silently=False)
        print("Email to admin sent!")
    except Exception as e:
        print(f"Error sending email: {e}")
        logger.error(f"Error sending email: {e}")
        return JsonResponse({'status': 'error', 'message': f'Error sending email: {e}'}, status=500)
    # Prepare email for customer
    subject2 = 'Zanafeel - Your Order'
    full_message2 = f'Welcome to Zanafeel.\nThank you for choosing us! \nOur staff will contact you very soon!\n\nHere is your order information:\n\n' \
                    f'Name Surname: {customer.name} {customer.surname}\nOrder ID: {order.id}\nEmail: {customer.email}\nPhone Number: {data["shipping"]["phone"]}' \
                    f'\nAddress: {data["shipping"]["address"]}\nCity: {data["shipping"]["city"]}\nState: {data["shipping"]["state"]}\nZipcode: {data["shipping"]["zipcode"]}' \
                    f'\nPayment Method: {data["shipping"]["payment_method"]}{email_content}{cupon_email}\n\nOrder Total Price (including Shipping Fee): {total}€'
    try:
        send_mail(subject2,
                    full_message2,
                    settings.EMAIL_HOST_USER,
                    [customer.email],
                    fail_silently=False)
    except Exception as e:
        print(f"Error sending email: {e}")
        logger.error(f"Error sending email: {e}")
        return JsonResponse({'status': 'error', 'message': f'Error sending email: {e}'}, status=500)
    return JsonResponse({'status': 'success', 'message': 'Payment Completed'}, status=200)

@csrf_exempt
def process_order_online(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    shipping_fee = 10
    if request.user.is_authenticated:
        customer = request.user.g_customer
        order, created = H_Order.objects.get_or_create(customer=customer, complete=False)
        print("Order created:", created)  # <-- Kontrollo nëse krijohet një order
        print("Order ID:", order.id)
    else:
        customer, order = guestOrder(request, data)
        print("Guest Order ID:", order.id)

    if data['form']['coupon'] == '':
        total = float(data['form']['total'])
        expected_total = float(order.get_cart_total) + shipping_fee

    else:
        total = float(data['form']['total'])
        # order.transaction_id = transaction_id
        cupon = K_Cupon.objects.get(code=data['form']['coupon'])
        orders = I_OrderItem.objects.filter(order_id=order.id)
        total_orders = sum(o.get_total for o in orders)
        discount_amount = (total_orders * cupon.discount) / 100  # Llogarisim zbritjen
        expected_total = (total_orders - discount_amount) + shipping_fee

    order.transaction_id = transaction_id
    if total == expected_total:
        order.complete = True
        order.total = expected_total
        order.save()
        cupon_discount = cupon.discount
        cupon_code = cupon.code
        cupon_email = '\n\nApplied Cupon: \n' + 'Cupon Code: ' + cupon_code + ', Discount: ' + str(cupon_discount) + '%'

    J_ShippingAddres.objects.create(
        customer=customer,
        order=order,
        phone=data['shipping']['phone'],
        email=customer.email,
        address=data['shipping']['address'],
        city=data['shipping']['city'],
        state=data['shipping']['state'],
        zipcode=data['shipping']['zipcode'],
        payment_method=data['shipping']['payment_method'],
        coupon=data['form']['coupon']
    )
    if order.complete:
        subject = 'Zanafeel - New Order'
        email_content = ''
        orders = I_OrderItem.objects.filter(order_id=order.id)
        for o in orders:
            email_content += f'\n\nProduct: {o.product.name}\nQuantity: {o.quantity}\nSize: {o.size}\nColor: {o.color}\nPrice: {o.product.price}€\nSubtotal: {o.get_total}€'

        full_message = f'You have a new order:\n\nName Surname: {customer.name} {customer.surname}\nOrder ID: {order.id}\nEmail: {customer.email}\nPhone Number: {data["shipping"]["phone"]}' \
                    f'\nAddress: {data["shipping"]["address"]}\nCity: {data["shipping"]["city"]}\nState: {data["shipping"]["state"]}\nZipcode: {data["shipping"]["zipcode"]}' \
                    f'\nPayment Method: {data["shipping"]["payment_method"]}{email_content}\n\nOrder Total Price: {expected_total}€'

        try:
            send_mail(subject, full_message, settings.EMAIL_HOST_USER, ['jemisha.florina@gmail.com'], fail_silently=False)
            print("Email to admin sent!")
        except Exception as e:
            print(f"Error sending email: {e}")
            logger.error(f"Error sending email: {e}")

        # Email për klientin
        subject2 = 'Zanafeel - Your Order'
        full_message2 = f'Welcome to Zanafeel.\nThank you for choosing us! \nOur staff will contact you very soon!\n\nHere is your order information:\n\n' \
                    f'Name Surname: {customer.name} {customer.surname}\nOrder ID: {order.id}\nEmail: {customer.email}\nPhone Number: {data["shipping"]["phone"]}' \
                    f'\nAddress: {data["shipping"]["address"]}\nCity: {data["shipping"]["city"]}\nState: {data["shipping"]["state"]}\nZipcode: {data["shipping"]["zipcode"]}' \
                    f'\nPayment Method: {data["shipping"]["payment_method"]}{email_content}\n\nOrder Total Price (including Shipping Fee): {expected_total}€'

        try:
            send_mail(subject2, full_message2, settings.EMAIL_HOST_USER, [customer.email], fail_silently=False)
        except Exception as e:
            print(f"Error sending email: {e}")
            logger.error(f"Error sending email: {e}")

    # total = order.get_cart_total + shipping_fee
    # amount_in_cents = int(total * 100)
    amount_in_cents = int(expected_total * 100)

    SHOPID = "80729II90009901"
    currency = "978"
    lang = "EN"
    shop_email = "jemisha.florina@gmail.com"
    URLDONE = "https://zanafeel.com/payment_success/"
    URLBACK = "https://zanafeel.com/checkout/"
    URLMS = "https://zanafeel.com/notifications/"
    accountingmode = "I"
    authormode = "I"

    secret_key = "QFjbf-kKQ9UFW-V-946w-Ap-HDQSaq9TJAeM4YX-HmD-vSvF-KGNq-x--AF--PtAva5amfcML9fpdr-gzj--p8mqDCC3BuYdrrqb"
    secret_key = secret_key.strip()
    secret_key_bytes = secret_key.encode('utf-8')
    # combined_text = plain_text
    # mac = hmac.new(secret_key_bytes, combined_text.encode('utf-8'), hashlib.sha256).hexdigest()
    order_id = str(order.id)
    print("Generated ORDERID:", order_id)
    mac_string = f"URLMS={URLMS}&URLDONE={URLDONE}&ORDERID={order_id}&SHOPID={SHOPID}&AMOUNT={amount_in_cents}&CURRENCY={currency}&ACCOUNTINGMODE={accountingmode}&AUTHORMODE={authormode}"
    print("MAC String:", mac_string)

    mac = hmac.new(secret_key_bytes, mac_string.encode('utf-8'), hashlib.sha256).hexdigest()
    print("Generated MAC:", mac)  # <-- Add this line
    customer_email = customer.email

    return JsonResponse({'redirect_url': reverse('payment_gateway', args=[order.id, mac, customer_email, amount_in_cents])})

import hmac
import hashlib

def calculate_mac(order_id, amount_in_cents=50, currency=978, accountingmode="I", authormode="I"):
    # URLMS = "https://zanafeel.com/notifications/"
    # URLDONE = "https://zanafeel.com/payment_success/"
    # SHOPID = 80729II00000102
    if not order_id or amount_in_cents == 0:
        return HttpResponse("Error: Missing or invalid parameters", status=400)
    SHOPID = "80729II90009901"
    currency = "978"
    lang = "EN"
    shop_email = "info@zanafeel.com"
    URLDONE = "https://zanafeel.com/payment_success/"
    URLBACK = "https://zanafeel.com/checkout/"
    URLMS = "https://zanafeel.com/notifications/"
    accountingmode = "I"
    authormode = "I"

    secret_key = "QFjbf-kKQ9UFW-V-946w-Ap-HDQSaq9TJAeM4YX-HmD-vSvF-KGNq-x--AF--PtAva5amfcML9fpdr-gzj--p8mqDCC3BuYdrrqb"
    secret_key = secret_key.strip()
    secret_key_bytes = secret_key.encode('utf-8')
    mac_string = f"URLMS={URLMS}&URLDONE={URLDONE}&ORDERID={order_id}&SHOPID={SHOPID}&AMOUNT={amount_in_cents}&CURRENCY={currency}&ACCOUNTINGMODE={accountingmode}&AUTHORMODE={authormode}"

    mac = hmac.new(secret_key_bytes, mac_string.encode('utf-8'), hashlib.sha256).hexdigest()

    final_mac_string = f"MAC={mac}"

    return f"ORDERID={order_id}&MAC={mac}"

def initiate_payment(request, order_id):
    try:
        # Check if order_id is an integer (logged-in user)
        order = H_Order.objects.get(id=int(order_id))
        customer_email = order.customer.email
        amount_in_cents = int(order.get_cart_total * 100)  # Convert to cents
    except (ValueError, H_Order.DoesNotExist):
        # Handle guest users (UUID order ID from cookies)
        guest_order_id = request.COOKIES.get('guest_order_id')
        if guest_order_id and guest_order_id == order_id:
            order_data = cookieCart(request)['order']
            customer_email = request.COOKIES.get('guest_email', 'guest@example.com')
            amount_in_cents = int(order_data['get_cart_total'] * 100)  # Convert to cents
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid order ID'}, status=400)

    mac = calculate_mac(order_id, amount_in_cents)
    print(mac)

    # Now, pass all required parameters
    return redirect('payment_gateway', order_id=order_id, mac=mac, customer_email=customer_email, amount_in_cents=amount_in_cents)

def payment_gateway(request, order_id, mac, customer_email, amount_in_cents):
    print("Hyra në payment_gateway!")
    context = {
        'order_id': order_id,
        'mac': mac,
        'customer_email': customer_email,
        'amount_in_cents': amount_in_cents,
    }
    print("Payment Gateway Context:", context)
    return render(request, 'payment-page.html', context)

def payment_success(request):
    if request.method == 'GET':
        return render(request, 'payment-message.html')

def payment_canceled(request):
    if request.method == 'GET':
        return render(request, 'payment-message.html')

def notifications(request):
    if request.method == 'GET':
        return render(request, 'payment-message.html')

def elements(request):
    if request.method == 'GET':
        return render(request, 'elements.html')

from django.shortcuts import render
from django.http import JsonResponse
from .models import H_Order
from .utils import cookieCart

from django.conf import settings  # Nëse e ke në settings.py


def paypal(request, order_id):
    paypal_email = getattr(settings, 'PAYPAL_EMAIL', 'sb-la47ff43123895@business.example.com')

    try:
        # Nëse order_id është int (user i regjistruar)
        order = H_Order.objects.get(id=int(order_id))
        items = order.h_orderitem_set.all()
        if not items.exists():
            return render(request, 'empty_cart.html')

        customer_email = order.customer.email
        amount = float(order.get_cart_total)

        context = {
            'order_id': order_id,
            'paypal_email': paypal_email,
            'amount': amount,
            'notify_url': 'https://example.com/paypal-ipn/',
            'return_url': 'https://example.com/payment-success/',
            'cancel_url': 'https://example.com/payment-cancelled/',
            'customer_email': customer_email,
        }

        return render(request, 'paypal.html', context)

    except (ValueError, H_Order.DoesNotExist):
        # Guest user ose UUID nga cookie
        guest_order_id = request.COOKIES.get('guest_order_id')
        if guest_order_id == order_id:
            cart_data = cookieCart(request)
            items = cart_data.get('items', [])
            if not items:
                return render(request, 'empty_cart.html')

            guest_email = request.COOKIES.get('guest_email', 'guest@example.com')
            amount = cart_data['order']['get_cart_total']

            context = {
                'order_id': order_id,
                'paypal_email': paypal_email,
                'amount': amount,
                'notify_url': 'https://example.com/paypal-ipn/',
                'return_url': 'https://example.com/payment-success/',
                'cancel_url': 'https://example.com/payment-cancelled/',
                'customer_email': guest_email,
            }
            return render(request, 'paypal.html', context)
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid order ID'}, status=400)


from django.http import HttpResponse

def paypal_ipn(request):
    # Këtu do vendosësh logjikën për të pranuar njoftimet IPN nga PayPal
    # Për tani, thjesht testimi:
    if request.method == 'POST':
        # Përpunojmë të dhënat e IPN këtu (mund të shtosh validime)
        print("IPN Data received:", request.POST)
        return HttpResponse("IPN received", status=200)
    else:
        return HttpResponse("Invalid request", status=400)
