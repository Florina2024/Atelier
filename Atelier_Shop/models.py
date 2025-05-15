from django.db import models
from django.utils.timezone import now
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from Product.models import D_Product

# Create your models here.
class A_Notification(models.Model):
    text = models.CharField(max_length=300, default='')

    def __str__(self):
        return self.text

class B_Main_Product(models.Model):
    product = models.ForeignKey(D_Product, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.product.name

class GalleryImage(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)  # Optional title
    image = models.ImageField(upload_to='gallery/')  # Main image
    overlay_image = models.ImageField(upload_to='gallery/overlays/', blank=True, null=True)  # Small image over main
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Price field
    uploaded_at = models.DateTimeField(default=now)
    product = models.ForeignKey(D_Product, on_delete=models.CASCADE, related_name='gallery_images', null=True, blank=True)  # New field

    def __str__(self):
        return self.title if self.title else "Gallery Image"

class LatestColImage(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)  # Optional title
    image = models.ImageField(upload_to='latest_col_images/')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)  # Pld

    def __str__(self):
        return self.name if self.name else "LatestCol Image"

class FooterImage(models.Model):
    image = models.ImageField(upload_to='footer_images/')
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.alt_text if self.alt_text else "Footer Image"

class S_Shipping(models.Model):
    description = RichTextField(blank=True, null=True)

class Z_Contact(models.Model):
    instagram_username = models.CharField(max_length=100, default='')
    instagram_link = models.CharField(max_length=100, default='')
    phone = models.CharField(max_length=30, default='')
    email_one = models.EmailField(max_length=100, default='')
    email_two = models.EmailField(max_length=100, default='')

class Z_Subscription(models.Model):
    full_name = models.EmailField(max_length=40)
    email = models.EmailField(max_length=50)

    def __str__(self):
        return self.full_name
