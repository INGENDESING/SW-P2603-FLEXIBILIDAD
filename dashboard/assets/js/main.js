/**
 * P2603 SW-K60 - Dashboard Flexibilidad
 * JavaScript principal
 */

// Cargar fecha de última actualización desde JSON
async function loadLastUpdate() {
    try {
        const response = await fetch('../_data/lineas.json');
        const data = await response.json();
        const updateElement = document.getElementById('last-update');
        if (updateElement && data.ultima_actualizacion) {
            updateElement.textContent = data.ultima_actualizacion;
        }
    } catch (error) {
        console.log('No se pudo cargar la fecha de actualización');
    }
}

// Formatear números
function formatNumber(num, decimals = 2) {
    if (num === null || num === undefined || isNaN(num)) return 'N/A';
    return num.toFixed(decimals);
}

// Formatear porcentajes
function formatPercent(num, decimals = 1) {
    if (num === null || num === undefined || isNaN(num)) return 'N/A';
    return num.toFixed(decimals) + '%';
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    loadLastUpdate();
});
