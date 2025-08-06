# Backend

## Desarrollo

Ejecutar el servidor con el modo de depuración activado:

```bash
FLASK_ENV=development python server.py
```

## Producción

Usar un servidor WSGI como Gunicorn:

```bash
gunicorn -w 4 server:app
```
