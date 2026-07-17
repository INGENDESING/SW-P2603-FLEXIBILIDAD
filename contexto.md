# Contexto del proyecto — ISOS ANÁLISIS FLEXIBILIDAD (P2603 SW-K60)

Análisis de flexibilidad de tuberías con CAESAR II 2019. Flujo de trabajo: isométricos desde AutoCAD Plant 3D 2027 → PCF → CAESAR II 2019 → dashboard web.

## Estado actual

- **Última tarea completada**: Despliegue del dashboard en GitHub Pages (2026-07-17). Sitio en vivo: https://ingendesing.github.io/SW-P2603-FLEXIBILIDAD/ — 7/7 líneas PASSED, JSON, isométricos y .md con HTTP 200. Workflow CI/CD probado con push real (run success).
- **Próxima tarea pendiente**: Validación con el cliente (Cartón Colombia)
- **Repo**: https://github.com/INGENDESING/SW-P2603-FLEXIBILIDAD (público; Pages en repos privados exige GitHub Pro)
- **Fecha de última actualización**: 2026-07-17

## Bases de diseño congeladas

- **Normativa**: ASME B31.3-2016 para análisis de esfuerzos
- **Material**: ASTM A312 TP 304L, Sch 10S, sin corrosión (CA = 0)
- **Datos de diseño**:
  - Presión máxima: 180 psig = 12.41 bar g
  - Temperatura operación: 90 °C (ΔT = 65 °C vs instalación 25 °C)
  - Fluido: agua (SG = 1.0, densidad 1000 kg/m³)
- **Casos de carga**: OPE = W+T1+P1, SUS = W+P1, EXP = OPE−SUS

## Resultados CAESAR II (verdad fuente: los .md — todos PASSED)

| Línea | Ratio máx | Nodo | Caso crítico |
|---|---|---|---|
| SIM-002 Descarga recirc. 1 DDW | 28.8 % | 78 | 6 (SUS) W+P2 |
| SIM-003 Descarga recirc. 2 DDW | 13.1 % | 120 | 4 (Alt-SUS) W+P2 |
| SIM-007 Línea bomba vacío | 85.7 % | 100 | 8 (EXP) L8=L3-L6 |
| SIM-008 Succión recirc. 1 DDW | 12.2 % | 200 | 4 (Alt-SUS) W+P2 |
| SIM-009 Succión recirc. 2 DDW | 20.8 % | 60 | 4 (Alt-SUS) W+P2 |
| SIM-010 Succión recirc. 3 DDW | 60.9 % | 310 | 6 (SUS) W+P2 |
| SIM-011 Descarga PP30BT03 | 56.1 % | 260 | 4 (Alt-SUS) W+P2 |

## Componentes del Proyecto

### 1. Corrección PCF (existente)
- `fix_pcf.py` — Corrige PCF exportados de Plant 3D 2027 para CAESAR II 2019
- Validado: `10.pcf` importó OK en CAESAR II 2019 (2026-07-08)

### 2. Dashboard Web
- **Ubicación**: `dashboard/` (autocontenido: datos, imágenes y reportes dentro)
- **Propósito**: Visualización de resultados para cliente (Cartón Colombia) e interno DML
- Modo oscuro (glassmorphism + neón), Chart.js vía CDN, lazy loading, lightbox, responsive
- Badge "SIN DATOS" gris cuando una línea no tiene compliance (nunca más FAILED por datos faltantes)

### 3. Archivos clave

| Archivo | Propósito |
|---------|-----------|
| `fix_pcf.py` | Corrección PCF Plant 3D → CAESAR II |
| `scripts/parse_caesar_md.py` | Parser CAESAR II .md → JSON + copia assets al dashboard |
| `dashboard/index.html` | Página principal (pública cliente) |
| `dashboard/tecnico.html` | Página técnica (interno DML) |
| `dashboard/linea.html` | Página individual de línea (`?id=SIM-011`) |
| `dashboard/_data/lineas.json` | Datos estructurados (generado por el parser) |
| `dashboard/assets/iso/` | Isométricos copiados por el parser (PCF102–108) |
| `dashboard/assets/graficos/` | Resultados gráficos CAESAR por línea (`SIM-XXX.png`; faltan 008/009/010) |
| `dashboard/assets/logo.png` | Logo DML (copia de `logo1.png` de la raíz) |
| `dashboard/assets/md/` | Reportes .md copiados por el parser (descarga desde linea.html) |
| `.github/workflows/update-dashboard.yml` | CI/CD pipeline |
| `task/todo.md` | Plan y revisión de la auditoría 2026-07-17 |

### 4. Líneas analizadas (7 total, todas PASSED)

| ID | Línea | PCF | Resultado .md |
|----|-------|-----|---------------|
| SIM-002 | Descarga recirculación 1 DDW | PCF103 | P2603-PR-PL-SIM-002.md |
| SIM-003 | Descarga recirculación 2 DDW | PCF104 | P2603-PR-PL-003.md (sin "SIM" en job) |
| SIM-007 | Línea bomba vacío nueva | PCF107 | "P2603-PR-PL-007 .md" (nombre con espacio) |
| SIM-008 | Succión recirculación 1 DDW | PCF106 | P2603-PR-PL-SIM-008.md |
| SIM-009 | Succión recirculación 2 DDW | PCF105 | P2603-PR-PL-SIM-009.md |
| SIM-010 | Succión recirculación 3 DDW | 10.pcf | P2603-PR-PL-SIM-010.md |
| SIM-011 | Descarga bomba PP30BT03 | PCF108 | P2603-PR-PL-SIM-011.md |

## Decisiones de diseño clave

### Parser CAESAR II (corregido 2026-07-17)
- **Normalización de saltos**: lectura con `newline=''` y reemplazo explícito `\r\n`/`\r` → `\n`; los .md antiguos mezclan `\r\r\n` (miles de CR sueltos) y eso destruía la detección de secciones
- **Secciones como listas**: cada página/caso genera una sección; compliance usa el ÚLTIMO CODE COMPLIANCE (resumen global); displacements/restraints hacen merge de casos CON datos (ope/sus/exp); stresses = máximo bending global
- **Regex clave**: job `P2603-PR-PL-(?:SIM-)?\d+` (003 y 007 no llevan "SIM"), ratio `Ratio\s*\(%\):` (CAESAR pone espacio), caso `CASE \d+ \(([\w-]+)\)` (acepta "Alt-SUS")
- **Assets autocontenidos**: el parser copia isométricos a `dashboard/assets/iso/`, resultados gráficos a `dashboard/assets/graficos/` (desde `ResultadosGraficos*.png` de cada carpeta; ese prefijo se EXCLUYE de la detección de isométrico), .md a `dashboard/assets/md/` y el logo `logo1.png` → `dashboard/assets/logo.png` → rutas relativas a `dashboard/`, funciona local y en Pages

### Dashboard
- HTML estático + JSON dinámico → sin backend; páginas individuales por URL param `?id=SIM-XXX`
- HTML nunca asume FAILED ante datos faltantes: exige `typeof passed === 'boolean'`

## Problemas recurrentes y soluciones

### PCF Plant 3D → CAESAR II
- Palabras clave nuevas no reconocidas por CAESAR II 2019 → `fix_pcf.py` con 6 transformaciones (resuelto 2026-07-08)

### Parser: 6 líneas "FAILED" falsas (resuelto 2026-07-17)
- **Causa**: `\r\r\n` mixtos → líneas vacías extra → REPORT fuera de la ventana de detección → JSON vacío; HTML pintaba `undefined` como FAILED
- **Lección**: los .md de CAESAR no tienen saltos de línea consistentes; SIEMPRE normalizar antes de parsear. SIM-011 era CRLF puro → único que parseaba
- **Verificación obligatoria**: tras regenerar el JSON, comparar ratio/nodo de las 7 líneas contra los .md (tabla de este archivo)

### GitHub Pages: despliegue fallaba con "repository not found" (resuelto 2026-07-17)
- **Causa 1**: repo privado en cuenta Free → Pages exige repo público o GitHub Pro. Se hizo público
- **Causa 2**: `permissions` a nivel job en `deploy-pages` anulaban `contents` → checkout sin acceso. Todo job con `permissions` propios debe incluir `contents: read` si usa `actions/checkout`
- **Causa 3**: Pages Source debe ser "GitHub Actions" (el workflow usa `actions/deploy-pages`); "Deploy from a branch" publica la raíz con Jekyll y excluye `_data/`

## Comandos / workflows útiles

### Corregir nuevo PCF
```bash
python fix_pcf.py "RUTA/NUEVA LINEA/archivo.pcf"
```

### Generar datos del dashboard (incluye copiar imágenes y .md)
```bash
python scripts/parse_caesar_md.py
# Genera dashboard/_data/lineas.json + dashboard/assets/{iso,md}/
```

### Servir dashboard localmente
```bash
cd dashboard
python -m http.server 8000
# Abrir http://localhost:8000
```

### Agregar nuevo análisis al dashboard
1. Exportar desde CAESAR II como `P2603-PR-PL-SIM-XXX.md` en la carpeta de la línea
2. Agregar isométrico como `PCFXXX.png` (o .jpeg/.jpg) en la misma carpeta
3. Ejecutar `python scripts/parse_caesar_md.py`
4. Verificar ratio/nodo contra el .md antes de publicar
5. Commit y push → GitHub Actions deploy automático

## Preguntas abiertas / bloqueos

- [x] GitHub repo creado (2026-07-17, público)
- [x] GitHub Pages habilitado — Source: GitHub Actions (2026-07-17)
- [x] Prueba de integración CI/CD — run success tras fix de permisos (2026-07-17)
- [ ] Validación con cliente (pendiente, sitio ya desplegado)

## Referencias externas

- Normativa: ASME B31.3-2016, Jan 31, 2017
- Software: CAESAR II 2019 (Ver.11.00.00.4800), Intergraph CADWorx
- Cliente: Cartón Colombia - Proyecto P2603 SW-K60
