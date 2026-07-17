/**
 * P2603 SW-K60 - Dashboard Flexibilidad
 * Image Utils: Lazy Loading, Lightbox, Placeholders
 */

/**
 * Placeholder SVG para isométricos faltantes
 */
const PLACEHOLDER_SVG = `data:image/svg+xml,
${encodeURIComponent(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
    <rect width="400" height="300" fill="#121836"/>
    <rect x="20" y="20" width="360" height="260" fill="none" stroke="#3a4060" stroke-width="2" stroke-dasharray="10,5"/>
    <text x="200" y="130" font-family="monospace" font-size="24" fill="#6a7088" text-anchor="middle">
        Isométrico no disponible
    </text>
    <text x="200" y="160" font-family="monospace" font-size="14" fill="#4a5070" text-anchor="middle">
        [Archivo no encontrado]
    </text>
    <circle cx="200" cy="80" r="30" fill="none" stroke="#4a5070" stroke-width="2"/>
    <path d="M190 80 L200 70 L210 80 M200 70 L200 90" stroke="#4a5070" stroke-width="2" fill="none"/>
</svg>
`)}`;

/**
 * Inicializar lazy loading para imágenes
 */
function initLazyLoading() {
    // Usar Intersection Observer para lazy loading
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    loadImage(img);
                    observer.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px 0px',
            threshold: 0.01
        });

        // Observar todas las imágenes con data-src
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    } else {
        // Fallback para navegadores sin Intersection Observer
        document.querySelectorAll('img[data-src]').forEach(img => {
            loadImage(img);
        });
    }
}

/**
 * Cargar imagen individual
 */
function loadImage(img) {
    const src = img.getAttribute('data-src') || img.src;
    const tempImg = new Image();

    tempImg.onload = function() {
        img.src = src;
        img.classList.add('loaded');
        img.classList.remove('loading');
    };

    tempImg.onerror = function() {
        img.src = PLACEHOLDER_SVG;
        img.classList.add('error');
        img.classList.remove('loading');
    };

    tempImg.src = src;
    img.classList.add('loading');
}

/**
 * Inicializar lightbox para imágenes
 */
function initLightbox() {
    const lightbox = createLightbox();

    // Agregar click listeners a imágenes ampliables
    document.querySelectorAll('img.lightbox-enabled').forEach(img => {
        img.style.cursor = 'pointer';
        img.addEventListener('click', () => {
            openLightbox(img.src, img.alt || 'Isométrico');
        });
    });
}

/**
 * Crear elemento lightbox
 */
function createLightbox() {
    let lightbox = document.getElementById('image-lightbox');

    if (!lightbox) {
        lightbox = document.createElement('div');
        lightbox.id = 'image-lightbox';
        lightbox.className = 'lightbox';
        lightbox.innerHTML = `
            <div class="lightbox-content">
                <button class="lightbox-close">&times;</button>
                <img class="lightbox-image" src="" alt="">
                <div class="lightbox-caption"></div>
            </div>
        `;

        document.body.appendChild(lightbox);

        // Event listeners
        lightbox.querySelector('.lightbox-close').addEventListener('click', closeLightbox);
        lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox) closeLightbox();
        });

        // Cerrar con ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeLightbox();
        });
    }

    return lightbox;
}

/**
 * Abrir lightbox
 */
function openLightbox(src, caption) {
    const lightbox = document.getElementById('image-lightbox');
    const img = lightbox.querySelector('.lightbox-image');
    const captionEl = lightbox.querySelector('.lightbox-caption');

    img.src = src;
    captionEl.textContent = caption;
    lightbox.classList.add('active');
    document.body.style.overflow = 'hidden';
}

/**
 * Cerrar lightbox
 */
function closeLightbox() {
    const lightbox = document.getElementById('image-lightbox');
    lightbox.classList.remove('active');
    document.body.style.overflow = '';
}

/**
 * Inicializar todas las utilidades de imágenes
 */
function initImageUtils() {
    initLazyLoading();
    initLightbox();
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initImageUtils);
} else {
    initImageUtils();
}

// Exportar funciones
window.ImageUtils = {
    initLazyLoading,
    initLightbox,
    openLightbox,
    closeLightbox,
    PLACEHOLDER_SVG
};
