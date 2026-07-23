# Dashboard Análisis de Flexibilidad - P2603 SW-K60

Dashboard web para visualización de resultados de análisis de flexibilidad de tuberías (CAESAR II 2019) - Proyecto Smurfit Westrock.

## Características

- **Modo oscuro futurista** con efectos glassmorphism y acentos neón
- **Visualización interactiva** con Chart.js
- **Lazy loading** de isométricos para optimizar performance
- **Lightbox** para visualización de imágenes
- **Responsive design** para desktop y móvil
- **CI/CD automatizado** con GitHub Actions
- **Audiencia dual**: páginas públicas (cliente) y técnicas (interno)

## Estructura

```
dashboard/
├── _data/
│   └── lineas.json          # Datos parseados (generado automáticamente)
├── assets/
│   ├── css/
│   │   └── styles.css      # Estilos modo oscuro futurista
│   └── js/
│       ├── main.js          # Funcionalidades base
│       ├── charts.js        # Chart.js utilities
│       └── images.js       # Lazy loading y lightbox
├── index.html               # Página principal (pública)
├── tecnico.html             # Página técnica (interno)
└── linea.html               # Página individual de línea (dinámica)

scripts/
└── parse_caesar_md.py       # Parser CAESAR II .md → JSON

.github/
└── workflows/
    └── update-dashboard.yml # CI/CD pipeline
```

## Instalación y Uso Local

### Requisitos

- Python 3.11+
- Servidor web (opcional, para desarrollo)

### Generar datos

```bash
# Ejecutar parser para generar lineas.json desde archivos .md
python scripts/parse_caesar_md.py
```

### Servir localmente

```bash
# Opción 1: Servidor Python simple
cd dashboard
python -m http.server 8000

# Opción 2: Live Server (VS Code)
# Instalar extensión "Live Server" y clic derecho en index.html
```

Abrir en navegador: `http://localhost:8000`

## Despliegue en GitHub Pages

### 1. Crear repositorio GitHub

```bash
git init
git add .
git commit -m "Initial commit: Flexibilidad Dashboard"
git branch -M main
git remote add origin https://github.com/usuario/p2603-flexibilidad.git
git push -u origin main
```

### 2. Habilitar GitHub Pages

1. Ir a Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main` / `root`
4. Click Save

### 3. Configurar GitHub Actions

El workflow `.github/workflows/update-dashboard.yml` se ejecuta automáticamente:

- **Trigger**: Push a `main` con cambios en archivos `.md`
- **Steps**:
  1. Ejecuta `parse_caesar_md.py`
  2. Commit `lineas.json` si cambió
  3. Deploy a GitHub Pages

### 4. Agregar nuevos análisis

1. Exportar reporte desde CAESAR II como `.md`
2. Guardar en carpeta correspondiente con formato `P2603-PR-PL-SIM-XXX.md`
3. Agregar isométrico como `PCFXXX.png` o `.jpeg`
4. Commit y push:
   ```bash
   git add "SUCCION DE BOMBA DE RECIRCULACION 4 DDW/"
   git commit -m "feat: add SIM-012 analysis"
   git push
   ```
5. GitHub Actions actualiza el dashboard automáticamente

## Formato de Archivos

### Archivos .md de CAESAR II

Los reportes deben seguir el formato estándar de CAESAR II 2019:

```
CAESAR II 2019  Ver.11.00.00.4800,  (Build 190424)   Date: JUL 17, 2026   Time: 9:6
Job Name: P2603-PR-PL-SIM-011
Licensed To: Licensed To: Edit name in <system>\company.txt
CODE COMPLIANCE REPORT: Code Stresses on Elements
CASE 1 (OPE) W+T1+P1
...
```

### Estructura JSON (lineas.json)

```json
{
  "ultima_actualizacion": "2026-07-17",
  "total_lineas": 7,
  "lineas": [
    {
      "id": "SIM-011",
      "job_name": "P2603-PR-PL-SIM-011",
      "nombre": "DESCARGA BOMBA PP30BT03",
      "carpeta": "DESCARGA BOMBA PP30BT03",
      "isometrico": "PCF108.png",
      "fecha_analisis": "2026-07-17",
      "compliance": {
        "passed": true,
        "max_ratio_pct": 45.9,
        "max_node": 40,
        "code_stress_kpa": 120068.1,
        "allowable_kpa": 261844.1
      },
      "displacements": {
        "load_cases": {
          "ope": { "nodes": [...] }
        }
      }
    }
  ]
}
```

## Personalización

### Colores y Estilos

Editar `assets/css/styles.css`:

```css
:root {
    --accent-cyan: #00f5ff;
    --accent-magenta: #ff00ff;
    --bg-primary: #0a0e27;
    /* ... más variables */
}
```

### Gráficas Chart.js

Editar `assets/js/charts.js` para ajustar configuración de gráficas.

## Troubleshooting

### Las imágenes no cargan localmente

- Verificar que `lineas.json` esté generado
- Verificar rutas relativas en el JSON
- Usar servidor HTTP (no `file://`)

### GitHub Actions falla

- Verificar permisos del repo: Settings → Actions → General → Workflow permissions
- Asegurar que el token GitHub tenga permisos de escritura

### El parser no extrae datos

- Verificar formato del archivo `.md` (debe ser CAESAR II 2019)
- Ejecutar parser con debug: `python scripts/parse_caesar_md.py`

## Licencia

Confidencial - Proyecto P2603 SW-K60, Smurfit Westrock

---

**DML Engineering** - 2026
