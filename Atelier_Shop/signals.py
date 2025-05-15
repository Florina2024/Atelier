from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from Product.models import G_Customer

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create a G_Customer for the newly created user
        G_Customer.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Save the G_Customer profile whenever the User is saved
    if instance.g_customer:
        instance.g_customer.save()