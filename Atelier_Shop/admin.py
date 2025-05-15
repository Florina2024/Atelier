from django.contrib import admin
from .models import A_Notification, B_Main_Product, S_Shipping, Z_Contact, Z_Subscription, GalleryImage, LatestColImage, FooterImage

admin.site.register(A_Notification)
admin.site.register(B_Main_Product)
admin.site.register(S_Shipping)
admin.site.register(Z_Contact)
admin.site.register(Z_Subscription)
@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'uploaded_at')
class FooterImageAdmin(admin.ModelAdmin):
    list_display = ('image', 'alt_text')  # Kjo siguron që imazhi dhe alt text shfaqen në panel
admin.site.register(FooterImage, FooterImageAdmin)
