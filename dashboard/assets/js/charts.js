/**
 * P2603 SW-K60 - Dashboard Flexibilidad
 * Chart.js Configuration y Helpers
 */

// Configuración global de Chart.js
Chart.defaults.color = '#475569';
Chart.defaults.borderColor = 'rgba(0, 0, 0, 0.08)';
Chart.defaults.font.family = "'Inter', system-ui, sans-serif";

/**
 * Colores para gráficas de compliance
 */
const ComplianceColors = {
    good: '#10b981',
    warning: '#f59e0b',
    critical: '#ef4444',
    blue: '#2563eb',
    cyan: '#0891b2',
    magenta: '#9333ea'
};

/**
 * Obtener color según ratio de compliance
 */
function getComplianceColor(ratio) {
    if (ratio < 80) return ComplianceColors.good;
    if (ratio < 95) return ComplianceColors.warning;
    return ComplianceColors.critical;
}

/**
 * Crear gráfica de barras: Ratios de compliance por línea
 */
function createComplianceBarChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const labels = data.map(l => l.id);
    const ratios = data.map(l => l.compliance?.max_ratio_pct || 0);
    const colors = ratios.map(r => getComplianceColor(ratio));

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Ratio de Compliance (%)',
                data: ratios,
                backgroundColor: colors,
                borderColor: colors,
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: 'Ratio de Compliance por Línea',
                    color: '#475569',
                    font: { size: 16, weight: 500 }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Ratio: ${context.raw.toFixed(1)}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(0, 0, 0, 0.06)' },
                    ticks: {
                        color: '#64748b',
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#64748b' }
                }
            }
        }
    });
}

/**
 * Crear gráfica de doughnut: Distribución de estados
 */
function createStatusDoughnutChart(canvasId, passedCount, failedCount) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['PASSED', 'FAILED'],
            datasets: [{
                data: [passedCount, failedCount],
                backgroundColor: [ComplianceColors.good, ComplianceColors.critical],
                borderColor: [ComplianceColors.good, ComplianceColors.critical],
                borderWidth: 2,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#475569',
                        padding: 16,
                        font: { size: 12 }
                    }
                },
                title: {
                    display: true,
                    text: 'Distribución de Estados',
                    color: '#475569',
                    font: { size: 16, weight: 500 }
                }
            }
        }
    });
}

/**
 * Crear gráfica de líneas: Desplazamientos nodales
 */
function createDisplacementLineChart(canvasId, nodes, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !nodes || nodes.length === 0) return null;

    const opts = {
        showDX: true,
        showDY: true,
        showDZ: true,
        showResultant: true,
        ...options
    };

    const datasets = [];

    if (opts.showDX) {
        datasets.push({
            label: 'DX (mm)',
            data: nodes.map(n => n.dx),
            borderColor: ComplianceColors.cyan,
            backgroundColor: 'rgba(8, 145, 178, 0.12)',
            tension: 0.1,
            pointRadius: 2,
            pointHoverRadius: 6
        });
    }

    if (opts.showDY) {
        datasets.push({
            label: 'DY (mm)',
            data: nodes.map(n => n.dy),
            borderColor: ComplianceColors.magenta,
            backgroundColor: 'rgba(147, 51, 234, 0.12)',
            tension: 0.1,
            pointRadius: 2,
            pointHoverRadius: 6
        });
    }

    if (opts.showDZ) {
        datasets.push({
            label: 'DZ (mm)',
            data: nodes.map(n => n.dz),
            borderColor: ComplianceColors.good,
            backgroundColor: 'rgba(16, 185, 129, 0.12)',
            tension: 0.1,
            pointRadius: 2,
            pointHoverRadius: 6
        });
    }

    if (opts.showResultant) {
        datasets.push({
            label: 'Resultante (mm)',
            data: nodes.map(n => Math.sqrt(Math.pow(n.dx || 0, 2) + Math.pow(n.dy || 0, 2) + Math.pow(n.dz || 0, 2))),
            borderColor: ComplianceColors.warning,
            backgroundColor: 'rgba(245, 158, 11, 0.12)',
            tension: 0.1,
            pointRadius: 2,
            pointHoverRadius: 6,
            borderDash: [5, 5]
        });
    }

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: nodes.map(n => n.node),
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#475569',
                        padding: 12,
                        font: { size: 11 }
                    }
                },
                title: {
                    display: true,
                    text: 'Desplazamientos Nodales',
                    color: '#475569',
                    font: { size: 16, weight: 500 }
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return `Nodo: ${context[0].label}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    grid: { color: 'rgba(0, 0, 0, 0.06)' },
                    ticks: { color: '#64748b' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#64748b' },
                    title: {
                        display: true,
                        text: 'Nodo',
                        color: '#64748b'
                    }
                }
            }
        }
    });
}

/**
 * Crear gráfica polar: Direcciones de desplazamiento
 */
function createDisplacementPolarChart(canvasId, nodes) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !nodes || nodes.length === 0) return null;

    // Calcular magnitudes promedio por dirección
    let avgX = 0, avgY = 0, avgZ = 0;
    nodes.forEach(n => {
        avgX += Math.abs(n.dx || 0);
        avgY += Math.abs(n.dy || 0);
        avgZ += Math.abs(n.dz || 0);
    });
    avgX /= nodes.length;
    avgY /= nodes.length;
    avgZ /= nodes.length;

    return new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: ['DX (X)', 'DY (Y)', 'DZ (Z)'],
            datasets: [{
                data: [avgX, avgY, avgZ],
                backgroundColor: [
                    'rgba(8, 145, 178, 0.55)',
                    'rgba(147, 51, 234, 0.55)',
                    'rgba(16, 185, 129, 0.55)'
                ],
                borderColor: [
                    ComplianceColors.cyan,
                    ComplianceColors.magenta,
                    ComplianceColors.good
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#475569' }
                },
                title: {
                    display: true,
                    text: 'Dirección de Desplazamientos (Promedio)',
                    color: '#475569'
                }
            },
            scales: {
                r: {
                    grid: { color: 'rgba(0, 0, 0, 0.06)' },
                    ticks: { color: '#64748b', backdropColor: 'transparent' }
                }
            }
        }
    });
}

/**
 * Crear histograma de esfuerzos
 */
function createStressHistogram(canvasId, stresses) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !stresses || stresses.length === 0) return null;

    // Crear bins
    const min = Math.min(...stresses);
    const max = Math.max(...stresses);
    const binCount = 10;
    const binSize = (max - min) / binCount;

    const bins = new Array(binCount).fill(0);
    const labels = [];

    for (let i = 0; i < binCount; i++) {
        const binStart = min + i * binSize;
        const binEnd = min + (i + 1) * binSize;
        labels.push(`${binStart.toFixed(0)}`);
        stresses.forEach(s => {
            if (s >= binStart && s < binEnd) bins[i]++;
        });
    }

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Frecuencia',
                data: bins,
                backgroundColor: 'rgba(37, 99, 235, 0.55)',
                borderColor: ComplianceColors.blue,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: 'Distribución de Esfuerzos',
                    color: '#475569'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(0, 0, 0, 0.06)' },
                    ticks: { color: '#64748b' },
                    title: { display: true, text: 'Frecuencia', color: '#64748b' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#64748b' },
                    title: { display: true, text: 'Esfuerzo (kPa)', color: '#64748b' }
                }
            }
        }
    });
}

// Exportar funciones para uso global
window.ChartUtils = {
    createComplianceBarChart,
    createStatusDoughnutChart,
    createDisplacementLineChart,
    createDisplacementPolarChart,
    createStressHistogram,
    getComplianceColor,
    ComplianceColors
};
