from django.apps import AppConfig


class GestionaleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestionale'


from django.apps import AppConfig


class RealEstateConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'real_estate'
