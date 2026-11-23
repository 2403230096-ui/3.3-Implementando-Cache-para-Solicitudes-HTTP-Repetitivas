from django.apps import AppConfig


class PelisConfig(AppConfig):
    name = "pelis"

    def ready(self):
        from . import signals