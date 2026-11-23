import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from pelis.models import Pelicula

GENEROS = ["Accion", "Aventura", "Animacion", "Comedia", "Drama", "Terror"]

class Command(BaseCommand):
    help = "Carga películas de prueba"

    def add_arguments(self, parser):
        parser.add_argument("cantidad", nargs="?", type=int, default=3000)

    def handle(self, *args, **opts):
        Pelicula.objects.bulk_create([
            Pelicula(
                titulo=f"Pelicula de prueba {i}",
                genero=random.choice(GENEROS),
                anio=random.randint(1950, 2025),
                calificacion=Decimal(random.randint(10, 100)) / 10,
            )
            for i in range(1, opts["cantidad"] + 1)
        ])
        self.stdout.write(self.style.SUCCESS("Películas creadas"))