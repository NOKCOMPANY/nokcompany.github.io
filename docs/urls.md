# Rutas sin extensión

Las páginas del sitio se organizan como directorios que contienen un archivo `index.html` (por ejemplo, `producto/index.html`). Esto permite publicar URLs limpias como `/producto` en lugar de `/producto/index.html` o `/producto.html`. La librería [swup](https://swup.js.org/) maneja las transiciones entre rutas manteniendo la sensación de aplicación de una sola página.

## Configuración

1. **Estructura de archivos**: cada ruta es un directorio con su propio `index.html`.
2. **Reglas de servidor**:
   - En servidores Apache utilice `.htaccess` para redirigir `/ruta/` a `/ruta/index.html` y establecer un *fallback* a `index.html` para rutas desconocidas.
   - En Nginx configure `try_files $uri $uri/ /index.html;` para lograr el mismo comportamiento.
3. **Dependencias**: cargue `swup` desde un CDN o instálelo con un gestor de paquetes, y asegúrese de servir los archivos estáticos correspondientes.

## Advertencias

- La navegación directa a una URL sin extensión fallará si el servidor no cuenta con reglas de reescritura. Configure el *fallback* a `index.html` o defina una página `404.html` que redirija a la página principal.
- Algunos servicios de hosting requieren configuraciones propias para habilitar estas reescrituras (por ejemplo, Netlify, Vercel o GitHub Pages).

## Reproducir en otros entornos

1. Copie la estructura de directorios con `index.html` en cada ruta.
2. Incluya la librería `swup` y su inicialización en el código JavaScript.
3. Añada las reglas de reescritura apropiadas para el servidor o servicio de hosting elegido.
4. Verifique que las rutas funcionen accediendo directamente a ellas en el navegador.
