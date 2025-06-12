from django.shortcuts import render
from .models import GalleryImage, FooterImage
from Product.models import D_Product, A_Category, D_Product, B_Subcategory, C_Collection, G_Customer
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_protect
from Atelier_Shop .models import *
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.conf import settings
from Product.utils import cookieCart
from Product.utils import cartData, guestOrder

def index(request):
    if request.method == 'GET':
        try:
            collection = C_Collection.objects.first()  # Fetching the first collection as an example
        except C_Collection.DoesNotExist:
            collection = None  # If no collection exists, set it to None
        # Fetch the necessary data from the database
        categories = A_Category.objects.all()
        subcategories = B_Subcategory.objects.all()
        collections = C_Collection.objects.all()
        menu = B_Main_Product.objects.all()
        marque_all = A_Notification.objects.first()
        main_product = B_Main_Product.objects.first()
        footer1 = Z_Contact.objects.first()
        col = C_Collection.objects.all()
        images = GalleryImage.objects.select_related('product').all()
        products = D_Product.objects.all()
        products_group1 = D_Product.objects.all()[:6]
        products_group2 = D_Product.objects.all()[6:12]
        footer_images = FooterImage.objects.all()
        products_in_collection = D_Product.objects.filter(collection=collection)
        gallery_images_for_collection = GalleryImage.objects.filter(product__in=products_in_collection)
        new_products = D_Product.objects.filter(is_new=True).order_by('-id')[:4]
        popular_products = D_Product.objects.filter(is_new=True).order_by('-id')[:4]
        wishlist = request.session.get('wishlist', [])

        # Handle the cart data
        data = cartData(request)
        cartItems = data['cartItems']
        order = data['order']
        items = data['items']

        # Handle user authentication and G_Customer for logged-in users or guest users
        g_customer = None  # Default to None
        if request.user.is_authenticated:
            try:
                # For logged-in users, get the associated G_Customer object
                g_customer = request.user.g_customer
            except G_Customer.DoesNotExist:
                g_customer = None
        else:
            # For guests (not logged in), create a guest customer
            g_customer = G_Customer(name="Guest", surname="User", email="guest@example.com")

        # Add the G_Customer to the context to display personalized data
        context = {
            'categories': categories,
            'subcategories': subcategories,
            'collections': collections,
            'marque_all': marque_all,
            'main_product': main_product,
            'footer': footer1,
            'col': col,
            'menu': menu,
            'images': images,
            'collection': collection,
            'products': products,
            'footer_images': footer_images,
            'gallery_images': gallery_images_for_collection,
            'new_products': new_products,
            'cartItems': cartItems,
            'products1': products_group1,
            'products2': products_group2,
            'popular_products':popular_products,
            'items':items,
            'wishlist': wishlist,
            'g_customer': g_customer  # Pass the G_Customer (or guest) info to the template
        }

        return render(request, 'index.html', context)

def collections(request):
    if request.method == 'GET':
        categories = A_Category.objects.all()
        subcategories = B_Subcategory.objects.all()
        collections = reversed(C_Collection.objects.all())
        menu = B_Main_Product.objects.all()
        col = C_Collection.objects.all()
        marque = A_Notification.objects.first()
        footer1 = Z_Contact.objects.first()

        # marque_all = A_Notification.objects.all()
        # marque = marque_all[0]
        # footer = Z_Contact.objects.all()
        # footer1 = footer[0]

        data = cartData(request)
        cartItems = data['cartItems']

        context = {'categories': categories, 'subcategories': subcategories, 'collections': collections, 'marque': marque, 'footer': footer1, 'col': col, 'menu': menu,
                   'cartItems': cartItems}
        return render(request, 'allCollections.html', context)

def size_guide(request):
    if request.method == 'GET':
        categories = A_Category.objects.all()
        subcategories = B_Subcategory.objects.all()
        collections = reversed(C_Collection.objects.all())
        menu = B_Main_Product.objects.all()
        col = C_Collection.objects.all()

        marque_all = A_Notification.objects.all()
        marque = marque_all[0]
        footer = Z_Contact.objects.all()
        footer1 = footer[0]

        data = cartData(request)
        cartItems = data['cartItems']

        context = {'categories': categories, 'subcategories': subcategories, 'collections': collections,
                   'marque': marque, 'footer': footer1, 'col': col, 'menu': menu,
                   'cartItems': cartItems}

        return render(request, 'size_guide.html', context)

@csrf_protect
def newsletter(request):
    categories = A_Category.objects.all()
    subcategories = B_Subcategory.objects.all()
    collections = reversed(C_Collection.objects.all())
    menu = B_Main_Product.objects.all()
    col = C_Collection.objects.all()

    marque_all = A_Notification.objects.all()
    marque = marque_all[0]
    footer = Z_Contact.objects.all()
    footer1 = footer[0]

    data = cartData(request)
    cartItems = data['cartItems']

    if request.method == 'GET':
        context = {'categories': categories, 'subcategories': subcategories, 'collections': collections, 'marque': marque, 'footer': footer1, 'col': col, 'menu': menu,
                   'cartItems': cartItems}
        return render(request, 'newsletter.html', context)
    if request.method == 'POST':
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        register = request.POST
        full_name = register['full_name']
        email = register['email']
        try:
            validate_email(email)
            InsertSubcription = Z_Subscription(full_name=full_name, email=email)
            InsertSubcription.save()

            subject = 'Zanafeel - Subscriptions'
            full_message = 'You have a new subscription from Zanafeel E-commerce:\nFull Name: ' + full_name + '\nEmail: ' + email
            send_mail(subject,
                      full_message,
                      settings.EMAIL_HOST_USER,
                      ['jemisha.florina@gmail.com'],
                      fail_silently=False)

            subject2 = 'Welcome to Zanafeel'
            full_message2 = 'Welcome to Zanafeel.\nGet ready to join our world...' + '\n\nZanafeel\nPhone: +355 00 00 000 \ninfo@zanafeel.com'

            send_mail(subject2,
                      full_message2,
                      settings.EMAIL_HOST_USER,
                      [email],
                      fail_silently=False)

            return HttpResponseRedirect('/success/')
        except ValidationError:
            user_error = "This email is not correct! Please try again."
            context = {'categories': categories, 'subcategories': subcategories, 'collections': collections, 'marque': marque, 'footer': footer1, 'col': col, 'menu': menu, 'user_error': user_error,
                       'cartItems': cartItems}
            return render(request, 'newsletter.html', context)

def message(request):
    if request.method == 'GET':
        categories = A_Category.objects.all()
        subcategories = B_Subcategory.objects.all()
        collections = reversed(C_Collection.objects.all())
        menu = B_Main_Product.objects.all()
        col = C_Collection.objects.all()

        marque_all = A_Notification.objects.all()
        marque = marque_all[0]
        footer = Z_Contact.objects.all()
        footer1 = footer[0]

        data = cartData(request)
        cartItems = data['cartItems']

        context = {'categories': categories, 'subcategories': subcategories, 'collections': collections,
                   'marque': marque, 'footer': footer1, 'col': col, 'menu': menu, 'cartItems': cartItems}
        return render(request, 'messages.html', context)

def not_found(request):
    if request.method == 'GET':
        categories = A_Category.objects.all()
        subcategories = B_Subcategory.objects.all()
        collections = reversed(C_Collection.objects.all())
        menu = B_Main_Product.objects.all()
        col = C_Collection.objects.all()

        marque_all = A_Notification.objects.all()
        marque = marque_all[0]
        footer = Z_Contact.objects.all()
        footer1 = footer[0]

        data = cartData(request)
        cartItems = data['cartItems']

        context = {'categories': categories, 'subcategories': subcategories, 'collections': collections,
                   'marque': marque, 'footer': footer1, 'col': col, 'menu': menu, 'cartItems': cartItems}
        return render(request, '404.html', context)

def return_policy(request):
    if request.method == 'GET':
        menu = B_Main_Product.objects.all()
        marque_all = A_Notification.objects.all()
        marque = marque_all[0]
        footer = Z_Contact.objects.all()
        footer1 = footer[0]

        context = {'menu': menu, 'marque': marque, 'footer': footer1}
        return render(request, 'return_policy.html', context)

def privacy_policy(request):
    if request.method == 'GET':
        menu = B_Main_Product.objects.all()
        marque_all = A_Notification.objects.all()
        marque = marque_all[0]
        footer = Z_Contact.objects.all()
        footer1 = footer[0]

        context = {'menu': menu, 'marque': marque, 'footer': footer1}
        return render(request, 'privacy_policy.html', context)

def terms_and_conditions(request):
    if request.method == 'GET':
        menu = B_Main_Product.objects.all()
        marque_all = A_Notification.objects.all()
        marque = marque_all[0]
        footer = Z_Contact.objects.all()
        footer1 = footer[0]

        context = {'menu': menu, 'marque': marque, 'footer': footer1}
        return render(request, 'terms_and_conditions.html', context)

