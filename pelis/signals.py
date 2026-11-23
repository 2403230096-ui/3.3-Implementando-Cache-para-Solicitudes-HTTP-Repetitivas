from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Pelicula

VERSION_KEY = "peliculas_version"

@receiver([post_save, post_delete], sender=Pelicula)
def invalidar_cache_peliculas(sender, **kwargs):
    cache.add(VERSION_KEY,1,None)
    cache.incr(VERSION_KEY)