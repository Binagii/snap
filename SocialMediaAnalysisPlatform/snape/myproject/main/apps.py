from django.apps import AppConfig
from neomodel import config

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    
class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        from django.conf import settings
        config.DATABASE_URL = settings.NEOMODEL_NEO4J_BOLT_UR


