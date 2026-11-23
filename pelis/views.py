import json
import time
from decimal import Decimal, InvalidOperation
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import Pelicula

VERSION_KEY = "peliculas_version"
USAR_CACHE = True

def obtener_version():
    cache.add(VERSION_KEY,1,None)
    return cache.get(VERSION_KEY)

# Create your views here.

def validar_datos(datos):
    titulo = datos["titulo"]
    genero = datos["genero"]
    anio = datos["anio"]
    calificacion = Decimal(str(datos["calificacion"]))

    if not isinstance(titulo, str) or not titulo.strip():
        raise ValueError("El titulo es obligatorio")
    
    if not isinstance(genero, str) or not genero.strip():
        raise ValueError("El genero es obligatorio")
    
    if isinstance(anio, bool) or not isinstance(anio, int):
        raise ValueError("El año debe ser entero")
    
    if anio < 1900:
        raise ValueError("Año inválido")
    
    if not calificacion.is_finite() or not 0 <= calificacion <=10:
        raise ValueError("La calificación debe estar entre 0 y 10")

    return titulo.strip(), genero.strip(), anio, calificacion

@csrf_exempt
def peliculas(request):

    if request.method == 'GET':

        genero = request.GET.get("genero","").strip()

        clave = f"peliculas:v{obtener_version}:genero={genero.lower()}"

        inicio = time.perf_counter()
        datos = cache.get(clave) if USAR_CACHE else None

        if USAR_CACHE:cache.set(clave, datos, timeout=None)

        if datos is not None:
            origen = "HIT"
        else:
            origen = "MISS"
            consulta = Pelicula.objects.all().order_by("id")
            if genero:
                consulta = consulta.filter(genero__iexact=genero)
            datos = {"peliculas": list(consulta.values())}
            cache.set(clave,datos, timeout=None)

        ms = (time.perf_counter() - inicio) * 1000
        print(f"[CACHE {origen}] {clave} -> {ms:.2f}")

        respuesta = JsonResponse(datos)
        respuesta["X-Cache"] = origen
        return respuesta


    elif request.method == 'POST':

        try:
            datos = json.loads(request.body)

            titulo, genero, anio, calificacion = validar_datos(datos)

            pelicula = Pelicula.objects.create(
                titulo = titulo,
                genero = genero,
                anio = anio,
                calificacion = calificacion
            )

            return JsonResponse({
                "mensaje": "Pelicula registrada correctamente",
                "id": pelicula.id
            }, status=201)

        except (
            ValueError,
            KeyError,
            TypeError,
            InvalidOperation,
            json.JSONDecodeError
        ):
            return JsonResponse({
                "error": "Datos inválidos"
            }, status=400)

    return JsonResponse ({
        "error": "Metodo no permitido"
    }, status=405)

@csrf_exempt
def actualizar_peliculas(request, pelicula_id):

    if request.method not in ('PUT', 'DELETE'):
        return JsonResponse({
            "error": "Metodo no permitido"
        }, status=405)

    try:
        pelicula = Pelicula.objects.get(id=pelicula_id)
    except Pelicula.DoesNotExist:
        return JsonResponse({
            "error": "Película no encontrada"
        }, status=404)

    if request.method == 'DELETE':
        pelicula.delete()
        return JsonResponse({
            "mensaje": "Película eliminada correctamente"
        })

    try:
        datos = json.loads(request.body)
        titulo, genero, anio, calificacion = validar_datos(datos)
    except (
        ValueError,
        KeyError,
        TypeError,
        InvalidOperation,
        json.JSONDecodeError
    ):
        return JsonResponse({
            "error": "Datos inválidos"
        }, status=400)

    pelicula.titulo = titulo
    pelicula.genero = genero
    pelicula.anio = anio
    pelicula.calificacion = calificacion
    pelicula.save()

    return JsonResponse({
        "mensaje": "Película actualizada correctamente"
    })

def inicio(request):

    lista_peliculas = Pelicula.objects.all()

    return render(
        request,
        'peliculas/index.html',
        {'peliculas': lista_peliculas}
    )