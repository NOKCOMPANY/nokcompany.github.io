// =================================================================
// SWUP - GESTOR DE TRANSICIONES DE PÁGINA
// =================================================================
const swup = new Swup({
    animateHistoryBrowsing: true,
    cache: true,
    preload: true,
});

// Variable para mantener la instancia del mapa y evitar reinicialización
let mapInstance = null;

// =================================================================
// FUNCIONES DE INICIALIZACIÓN PARA CADA PÁGINA
// =================================================================

/**
 * Inicializa el mapa de Leaflet en la página de inicio.
 * Destruye el mapa anterior si existe para evitar errores.
 */
function initLeafletMap() {
    const mapContainer = document.getElementById('map');
    if (!mapContainer) return;

    // Si ya hay un mapa, lo eliminamos antes de crear uno nuevo
    if (mapInstance) {
        mapInstance.remove();
        mapInstance = null;
    }

    mapInstance = L.map('map', { zoomControl: false }).setView([-33.4145, -70.5827], 15);
    L.control.zoom({ position: 'topright' }).addTo(mapInstance);
    L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 19
    }).addTo(mapInstance);

    const redIcon = L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    L.marker([-33.4145, -70.5827], { icon: redIcon })
        .addTo(mapInstance)
        .bindPopup('<strong>NokServices</strong><br>Las Condes');
}

/**
 * Inicializa la lógica del formulario de contacto de EmailJS.
 */
function initContactForm() {
    const contactForm = document.getElementById('form-contact');
    if (!contactForm) return;

    // Sanitización de inputs
    function sanitizeInput(input) {
        return input.replace(/[<>]/g, '');
    }

    let submitAttempts = 0;
    const MAX_ATTEMPTS = 5;
    const COOLDOWN_TIME = 300000; // 5 minutos

    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();

        if (submitAttempts >= MAX_ATTEMPTS) {
            document.querySelector('.form-contact-status').innerHTML =
                "<div class='alert alert-warning mt-3'>Demasiados intentos. Por favor, espere 5 minutos.</div>";
            return;
        }

        const nombre = sanitizeInput(document.getElementById('nombre').value.trim());
        const correo = sanitizeInput(document.getElementById('correo').value.trim());
        const mensaje = sanitizeInput(document.getElementById('mensaje').value.trim());

        if (!nombre || !correo || !mensaje ||
            nombre.length > 100 || correo.length > 100 || mensaje.length > 1000) {
            document.querySelector('.form-contact-status').innerHTML =
                "<div class='alert alert-danger mt-3'>Por favor, verifique los campos del formulario.</div>";
            return;
        }

        const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
        if (!emailRegex.test(correo)) {
            document.querySelector('.form-contact-status').innerHTML =
                "<div class='alert alert-danger mt-3'>Por favor, ingrese un correo electrónico válido.</div>";
            return;
        }

        submitAttempts++;

        emailjs.sendForm('NOKCOMPANY', 'template_jbnt66h', this, '4yv6lNv3D75wM1BVV')
            .then(function(response) {
                document.querySelector('.form-contact-status').innerHTML =
                    "<div class='alert alert-success mt-3'>¡Mensaje enviado con éxito!</div>";
                e.target.reset();

                setTimeout(() => {
                    submitAttempts = Math.max(0, submitAttempts - 1);
                }, COOLDOWN_TIME);
            })
            .catch(function(error) {
                console.error('Error:', error);
                document.querySelector('.form-contact-status').innerHTML =
                    "<div class='alert alert-danger mt-3'>Error al enviar el mensaje. Inténtalo de nuevo.</div>";
            });
    });
}

/**
 * Función principal que se ejecuta en cada carga de página
 * para inicializar los scripts necesarios.
 */
function runPageScripts() {
    // Llama a las funciones de inicialización según la página actual
    if (document.getElementById('map')) {
        initLeafletMap();
    }
    if (document.getElementById('form-contact')) {
        initContactForm();
    }

    // Re-ejecuta el script de tu plantilla si es necesario (custom.js)
    if (window.ts_custom_scripts) {
        window.ts_custom_scripts();
    }
}

// =================================================================
// SWUP HOOKS - GESTIÓN DEL CICLO DE VIDA DE LA PÁGINA
// =================================================================

// Se ejecuta una vez cuando la página carga por primera vez
document.addEventListener('DOMContentLoaded', runPageScripts);

// Se ejecuta cada vez que Swup carga una nueva página
swup.hooks.on('page:view', runPageScripts);

// Clases para las animaciones de Swup
swup.hooks.on('visit:start', () => {
    document.body.classList.add('is-changing');
});

swup.hooks.on('visit:end', () => {
    document.body.classList.remove('is-changing');
});