from django.apps import AppConfig


class AtelierShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Atelier_Shop'

    def ready(self):
        import Atelier_Shop.signals
