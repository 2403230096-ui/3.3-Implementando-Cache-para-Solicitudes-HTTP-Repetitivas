# Caché en Django - Endpoint de películas

## Funcionalidad
Listado de películas (`pelis_pelicula`) en formato JSON.

## Endpoint
`GET http://127.0.0.1:8000/api/peliculas/`

Responde `200 OK` con `{"peliculas": [...]}`. El encabezado `X-Cache` indica si la respuesta salió del caché (`HIT`) o de la base de datos (`MISS`). La consola del servidor también lo muestra.

## Tipo de caché
`LocMemCache` (memoria local de Django), configurado en `settings.py`.
La clave incluye el filtro de género y un número de versión: `peliculas:v<versión>:genero=<filtro>`.

## Estrategia de actualización
**Invalidación al cambiar los datos.** Al crear, editar o eliminar una película, una señal (`pelis/signals.py`) sube el número de versión. La siguiente solicitud no encuentra la clave anterior, consulta la base de datos, guarda el resultado y devuelve los datos actualizados.

## Cómo ejecutar
```
pip install -r requirements.txt
python manage.py migrate
python manage.py cargar_peliculas 3000
python manage.py runserver
```

## Cómo reproducir las pruebas (Postman)
Siempre con `GET http://127.0.0.1:8000/api/peliculas/`:
1. Con `USAR_CACHE = False` en `views.py`: enviar 5 solicitudes y anotar los ms.
2. Con `USAR_CACHE = True` y el servidor reiniciado: enviar 1 solicitud (`MISS`) y anotar su tiempo.
3. Enviar 5 solicitudes más (`HIT`) y anotar los ms.
4. Actualización: `PUT http://127.0.0.1:8000/api/peliculas/1/` con
   `{"titulo": "Nuevo titulo", "genero": "Animacion", "anio": 1997, "calificacion": 9.0}`
   y luego un GET: sale `MISS` con el cambio, y el siguiente GET sale `HIT`.

## Tiempos (ms)
| Condición | Prueba 1 | Prueba 2 | Prueba 3 | Prueba 4 | Prueba 5 | Promedio |
|-----------|----------|----------|----------|----------|----------|----------|
| Sin caché |       6ms|       3ms|       2ms|       2ms|       2ms|       3ms|
| Con caché |       3ms|       3ms|       2ms|       2ms|       2ms|     2.4ms|


## Conclusión
Sin caché, el promedio de las cinco solicitudes fue de 3 ms. Con caché, la primera solicitud (que consultó la base de datos y llenó el caché) tardó 12 ms, y las cinco siguientes, que reutilizaron el resultado almacenado, promediaron 2.4 ms. Con pocos registros la diferencia es pequeña (0.6 ms), porque SQLite responde muy rápido, pero el caché funcionó: el encabezado `X-Cache` pasó de `MISS` a `HIT`, la consola mostró `[CACHE MISS]` y luego `[CACHE HIT]`, y tras modificar una película con `PUT` la siguiente solicitud volvió a ser `MISS` con el dato actualizado.
