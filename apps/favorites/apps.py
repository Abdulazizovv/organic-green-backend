"""
App configuration for Favorites
"""
from django.apps import AppConfig


class FavoritesConfig(AppConfig):
    """
    Configuration for the Favorites app
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.favorites'
    verbose_name = 'Sevimli mahsulotlar'
    
    def ready(self):
        """
        Import signal handlers when the app is ready
        """
        # Import signals if needed in the future
        pass
