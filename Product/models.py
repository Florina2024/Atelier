from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.utils.text import slugify  # Importo slugify

class A_Category(models.Model):
    category = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.category

class B_Subcategory(models.Model):
    category = models.ForeignKey(A_Category, on_delete=models.CASCADE, null=True, blank=True)
    subcategory = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.category.category + ': ' + self.subcategory

class C_Collection(models.Model):
    collection = models.CharField(max_length=100, default='')
    slug = models.SlugField(unique=True, blank=True)
    main_image = models.ImageField(null=True, blank=True)
    info = models.CharField(max_length=200, default='')
    description = RichTextField(blank=True, null=True)
    cover_image = models.ImageField(null=True, blank=True)
    footer_description = RichTextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:  # Krijo slug automatikisht nëse nuk është dhënë
            self.slug = slugify(self.collection)
        # Sigurohuni që slug është unik
        while C_Collection.objects.filter(slug=self.slug).exists():
            self.slug = f"{self.slug}-{self.id}"  # Shtoni një identifikues unik
        super(C_Collection, self).save(*args, **kwargs)

    def __str__(self):
        return self.collection

class C_Gift(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(null=True, blank=True)
    price_category = models.CharField(
        max_length=20, choices=[
            ('under_100', 'Under 100$'),
            ('between_100_150', 'Between 100$ and 150$'),
            ('over_150', 'Over 150$'),
        ], default='under_100'
    )

    def __str__(self):
        return self.name

class D_Product(models.Model):
    name = models.CharField(max_length=100, default='')
    subcategory = models.ForeignKey(B_Subcategory, on_delete=models.CASCADE, null=True, blank=True)
    collection = models.ForeignKey(C_Collection, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    main_image = models.ImageField(null=True, blank=True)
    description = RichTextField(blank=True, null=True)
    details = RichTextField(blank=True, null=True)
    is_new = models.BooleanField(default=False)

    @property
    def imageURL(self):
        try:
            url = self.main_image.url
        except:
            url = ''
        return url

    def __str__(self):
        # Sigurohuni që subcategory dhe category janë të disponueshme
        category_name = self.subcategory.category.category if self.subcategory and self.subcategory.category else 'No Category'
        return f'{category_name}: {self.subcategory.subcategory}: {self.name}'

    # def __str__(self):
    #     return self.subcategory.category.category + ': ' + self.subcategory.subcategory + ': ' + self.name

class D_Colors_List(models.Model):
    color = models.CharField(max_length=100, default='')
    code = models.CharField(max_length=10, default='')

    def __str__(self):
        return self.color

class E_Product_Gallery(models.Model):
    product = models.ForeignKey(D_Product, on_delete=models.CASCADE, null=True, blank=True, related_name='images')
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.product.name

class E_Product_Color(models.Model):
    product = models.ForeignKey(D_Product, on_delete=models.CASCADE, null=True, blank=True)
    color = models.ForeignKey(D_Colors_List, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.product.name + ', ' + self.color.color

class E_Product_Size(models.Model):
    product = models.ForeignKey(D_Product, on_delete=models.CASCADE, null=True, blank=True)
    size = models.CharField(max_length=10, default='')

    def __str__(self):
        return self.product.name + ', ' + self.size

class G_Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='g_customer')  # Changed related_name
    name = models.CharField(max_length=50, default='', blank=True)
    surname = models.CharField(max_length=50, default='', blank=True)
    email = models.EmailField(max_length=100, null=True)

    def __str__(self):
        return self.name + ' ' + self.surname

class H_Order(models.Model):
    customer = models.ForeignKey(G_Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=100, null=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    @property
    def get_cart_total(self):
        orderitems = self.i_orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.i_orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    @property
    def get_order_id(self):
        order_id = self.id
        return order_id

    def __str__(self):
        return 'Order ID: ' + str(self.id) + ', Customer: ' + self.customer.name + ' ' + self.customer.surname

class I_OrderItem(models.Model):
    product = models.ForeignKey(D_Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(H_Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    size = models.CharField(max_length=30, null=True)
    color = models.CharField(max_length=50, null=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


    def __str__(self):
        return 'Order ID: ' + str(self.order.id) + ', ' + 'Product: ' + self.product.name + ', Quantity: ' + str(self.quantity)

class J_ShippingAddres(models.Model):
    customer = models.ForeignKey(G_Customer, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(H_Order, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=100, null=True)
    address = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=100, null=True)
    zipcode = models.CharField(max_length=100, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=100, null=True, default='')
    coupon = models.CharField(max_length=100, null=True, default='', blank=True)

    # def __str__(self):
    #     return 'Order: ' + str(self.order.) + ', ' + self.email

class K_Cupon(models.Model):
    code = models.CharField(max_length=100, null=True)
    discount = models.IntegerField(default=0)

    def __str__(self):
        return 'Code: ' + self.code + ', Discount: ' + str(self.discount) + '%'

class K_Cupon_Order(models.Model):
    order = models.ForeignKey(H_Order, on_delete=models.SET_NULL, null=True, blank=True)
    discount = models.DecimalField(max_digits=7, decimal_places=2, default=0)
