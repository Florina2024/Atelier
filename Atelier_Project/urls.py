from django.contrib import admin  # Importo admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from Atelier_Shop import views
from Product import views as P_views

urlpatterns = [
    path('admin/', admin.site.urls),  # Shto admin panelin
    path('', views.index, name='index'),
    path('new_arrivals/', P_views.new_arrivals, name='new_arrivals'),
    path('category_page/<int:category_id>/', P_views.category_page, name='category_page'),
    path('shop/', P_views.shop, name='shop'),
    path('collection/', P_views.collection, name='collection'),
    path('collection_page/<slug:collection_slug>/', P_views.collection_page, name='collection_page'),
    path('product/<int:product_id>/', P_views.product, name='product'),
    path('addToCart/', P_views.addToCart, name='addToCart'),
    path('cart_modal/', P_views.cart_modal, name='cart_modal'),
    path('gifts-under-100/', P_views.gifts_under_100, name='gifts_under_100'),
    path('gifts-100-150/', P_views.gifts_100_150, name='gifts_100_150'),
    path('gifts-over-150/', P_views.gifts_over_150, name='gifts_over_150'),
    path('update_item/', P_views.update_item, name='update_item'),
    path('checkout/', P_views.checkout, name='checkout'),
    path('message/', views.message, name='message'),
    path('success/', views.message, name='success'),

    path('initiate_payment/<str:order_id>/', P_views.initiate_payment, name='initiate_payment'),
    path('payment_gateway/<str:order_id>/<str:mac>/<str:customer_email>/<str:amount_in_cents>', P_views.payment_gateway, name='payment_gateway'),
    path('payment_success/', P_views.payment_success, name='payment_success'),
    path('payment_canceled/', P_views.payment_canceled, name='payment_canceled'),
    path('notifications/', P_views.notifications, name='notifications'),
    path('elements/', P_views.elements, name='elements'),
    path('process_order_online/', P_views.process_order_online, name='process_order_online'),
    path('paypal/', include('paypal.standard.ipn.urls')),
    # path('paypal/<int:order_id>/<int:amount_in_cents>/', P_views.paypal, name='paypal')
    path('paypal/<str:order_id>/', P_views.paypal, name='paypal'),
    path('payment-success/', P_views.payment_success, name='payment_success'),
    path('payment-cancelled/', P_views.payment_canceled, name='payment_canceled'),
    path('paypal-ipn/', P_views.paypal_ipn, name='paypal_ipn'),  # për IPN
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

