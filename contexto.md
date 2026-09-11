# Contexto del proyecto — ISOS ANÁLISIS FLEXIBILIDAD (P2603 SW-K60)

Análisis de flexibilidad de tuberías con CAESAR II 2019. Flujo de trabajo: isométricos desde AutoCAD Plant 3D 2027 → PCF → CAESAR II 2019 → dashboard web.

## Estado actual

- **Última tarea completada**: reorganización de archivos y carpetas (2026-09-11): carpetas de línea con prefijo de dos dígitos `01.0`–`13.0` (orden alfabético correcto; el JSON del dashboard queda en orden SIM), `fix_pcf.py`→`scripts/`, `logo1.png`→`assets/` (parser ajustado), artefactos SIM-015 movidos de 10.0→11.0, `.tmp-playwright/` eliminado, `.gitignore` con scratch CAESAR (CONTROLU/DBGENBIN/COMNDINP/OCONTROLU/TEMPMAT*/c2db/XML), triggers del workflow robustos (`**/P2603-PR-*.md` + `**/Graficas/**`). Antes: transmittal HTML `transmittal/transmittal_DOCS-180_a_DOCS-190.html` para el Ing. Cristian Muriel (revisión de calidad; N.° `[TR-001]` placeholder por confirmar)
- **Recorridas con material corregido (2026-09-10)**: SIM-010 (46.7 % @430 EXP), SIM-007 (70.1 % @100 EXP caso 9 — era FAILED ~103.9 % con admisible TP304), SIM-011 (67.2 % @260 Alt-SUS). Ratio máximo del proyecto: 70.1 % (SIM-007)
- **AnexoResultado: EN ESPERA** — no procesar ningún `AnexoResultado.png` hasta instrucción del usuario
- **Sitio en vivo**: https://ingendesing.github.io/SW-P2603-FLEXIBILIDAD/ (desactualizado hasta commit+push: el JSON local ya tiene las 11 líneas TP304L)
- **Próxima tarea pendiente**: commit+push (con confirmación explícita); usuario re-exporta tifs de SIM-007 (los actuales son de la corrida vieja TP304) → luego `convertir_graficas.py --force` + parser + `extraer_informe.py --linea SIM-007` + recompilar DOCS-182. Esperan al usuario: número de transmittal, envío del transmittal a C. Muriel, fechas de revisión/aprobación y correo `\ead{}`, instrucción AnexoResultado, corridas SIM-016 (12.0)/PCF115 (13.0), validación cliente
- **Repo**: https://github.com/INGENDESING/SW-P2603-FLEXIBILIDAD (público; Pages en repos privados exige GitHub Pro)
- **Fecha de última actualización**: 2026-09-11
- **Memoria persistente (2026-09-03)**: bóveda Obsidian en `boveda/` + skills `inicializar`/`memoria` en `.kimi-code/skills/`. En cada sesión nueva: «ejecuta inicializa» (ver `inicializar.md`)

## Bases de diseño congeladas

- **Normativa**: ASME B31.3-2016 para análisis de esfuerzos
- **Material**: ASTM A312 TP 304L, Sch 10S, sin corrosión (CA = 0)
- **Datos de diseño**:
  - Presión máxima: 180 psig = 12.41 bar g
  - Temperatura operación: 90 °C (ΔT = 65 °C vs instalación 25 °C)
  - Fluido: agua (SG = 1.0, densidad 1000 kg/m³)
- **Casos de carga**: OPE = W+T1+P1, SUS = W+P1, EXP = OPE−SUS

## Resultados CAESAR II (verdad fuente: los .md — corridas TP304L 2026-09-09/10, todas PASSED, 0×137895.1)

Informes (DOCS-180→190) y dashboard (`lineas.json`) YA actualizados a estos números (2026-09-10). AnexoResultado en espera de instrucciones.

| Línea | Ratio máx | Nodo | Caso crítico |
|---|---|---|---|
| SIM-002 Descarga recirc. 1 DDW | 34.5 % | 78 | 6 (SUS) W+P2 |
| SIM-003 Descarga recirc. 2 DDW | 15.7 % | 120 | 4 (Alt-SUS) W+P2 |
| SIM-007 Línea bomba vacío | 70.1 % (recorrida 09-10 14:42) | 100 | 9 (EXP) L9=L1-L3 |
| SIM-008 Succión recirc. 1 DDW | 22.5 % | 90 | 4 (Alt-SUS) W+P2 |
| SIM-009 Succión recirc. 2 DDW | 26.4 % | 60 | 2 (Alt-SUS) W+P2 |
| SIM-010 Succión recirc. 3 DDW | 46.7 % (recorrida 09-10 09:03) | 430 | 8 (EXP) L8=L3-L6 |
| SIM-011 Descarga PP30BT03 | 67.2 % (recorrida 09-10 15:12) | 260 | 4 (Alt-SUS) W+P2 |
| SIM-012 Succión TK Blowtank | 34.8 % | 130 | 8 (EXP) L8=L3-L6 |
| SIM-013 Descarga tanque nivelación | 24.3 % | 100 | 2 (Alt-SUS) W+P2 |
| SIM-014 Descarga TMS | 55.9 % | 70 | 6 (SUS) W+P2 |
| SIM-015 Tubería filtro fibras PP1 | 36.3 % | 80 | 2 (Alt-SUS) W+P2 |

## Componentes del Proyecto

### 1. Corrección PCF (existente)
- `scripts/fix_pcf.py` — Corrige PCF exportados de Plant 3D 2027 para CAESAR II 2019
- Validado: `10.pcf` importó OK en CAESAR II 2019 (2026-07-08)

### 2. Dashboard Web
- **Ubicación**: `dashboard/` (autocontenido: datos, imágenes y reportes dentro)
- **Propósito**: Visualización de resultados para cliente (Smurfit Westrock) e interno DML
- Modo claro profesional (glassmorphism suave), Chart.js vía CDN, lazy loading, lightbox, responsive
- Badge "SIN DATOS" gris cuando una línea no tiene compliance (nunca más FAILED por datos faltantes)
- Header con logos de Smurfit Westrock (cliente) y DML Ingenieros Consultores (consultora)

### 2b. Generador de informes LaTeX
- `generadorinf.md` — Prompt maestro (v1.1, 2026-09-02) para generar un informe PDF por línea desde los `.md` CAESAR; reemplaza `PropmtGeneracionInformes.txt`. Decisiones: 8 informes independientes (D2), arquitectura híbrida script+LLM (D3). Codificación de informes: `I24.104-PP30-PP01-P-DOCS-18X` (180→187 en orden SIM); sin resumen ejecutivo (el informe ES el resumen); investigación web con agentes para marco teórico/objetivos
- `Plantilla latex/` — Plantilla corporativa DML (elsarticle, 15 secciones modulares, `config/datos_proyecto.tex`, `compilar_informe.ps1`); convenciones en `Plantilla latex/CLAUDE_plantilla.md`. Membrete 2026-09-02: textos proyecto en `datos_proyecto.tex` (INGENIERIA DE DETALLE / EUCALYPTUS PULP PRODUCTION OPTIMIZATION PROJECT / ANALISIS DE FLEXIBILIDAD TK BLOWTANK, PROYECTO: P2603), firmas J.ARBOLEDA/F.NAVIA/H.ROSERO, logo1=DML logo2=Smurfit. El rediseño geométrico (logos grandes, letra uniforme) fue REVERTIDO por decisión del usuario — se conserva el layout original (logos 2.3×2.5 cm, arraystretch 0.80)
- Salida: `informes/SIM-0XX/I24.104-PP30-PP01-P-DOCS-18X.pdf` — **11/11 compilados** (180→190: 23/22/23/23/22/27/28/24/22/24/28 pág., 2026-09-10; números == corridas TP304L). OJO: `tab_esfuerzos_critico.tex` de SIM-010/011/012/015 lleva conversión manual a `longtable` (se pierde al re-ejecutar `extraer_informe.py`)

### 3. Archivos clave

| Archivo | Propósito |
|---------|-----------|
| `scripts/fix_pcf.py` | Corrección PCF Plant 3D → CAESAR II |
| `scripts/parse_caesar_md.py` | Parser CAESAR II .md → JSON + copia assets al dashboard (2026-09-10: lee `Graficas/`, excluye `_corrida_anterior`, isométrico desde `Graficas/PCF*`) |
| `scripts/convertir_graficas.py` | tif→png de `Graficas/` (PIL, fondo blanco, excluye AnexoResultado; idempotente, `--force`) (2026-09-10) |
| `scripts/extraer_informe.py` | Genera tablas .tex + figuras + imágenes para informes (2026-09-10: assets `graf_desplazamiento[_N]`/`graf_stress_percent[_N]`/`graf_nodos_soporte[_N]`) |
| `dashboard/index.html` | Página principal (pública cliente) |
| `dashboard/tecnico.html` | Página técnica (interno DML) |
| `dashboard/linea.html` | Página individual de línea (`?id=SIM-011`) |
| `dashboard/_data/lineas.json` | Datos estructurados (generado por el parser) |
| `dashboard/assets/iso/` | Isométricos copiados por el parser (PCF102–108) |
| `dashboard/assets/graficos/` | Resultados gráficos CAESAR por línea (`SIM-XXX-N.png`, desde `Graficas/` convertidas; 11/11 líneas; 4 huérfanos viejos sin referencia: SIM-002/003/007/011.png) |
| `dashboard/assets/logo.png` | Logo Smurfit Westrock (cliente) |
| `dashboard/assets/logo-dml.png` | Logo DML Ingenieros Consultores (consultora) |
| `dashboard/assets/md/` | Reportes .md copiados por el parser (descarga desde linea.html) |
| `inicializar.md` | Punto de entrada de cada sesión nueva («ejecuta inicializa» → carga la bóveda) |
| `transmittal/transmittal_DOCS-180_a_DOCS-190.html` | Correo HTML de envío de los 11 informes a C. Muriel (revisión de calidad; logos base64, paleta DML #117341; N.° [TR-001] placeholder) |
| `boveda/` | Bóveda Obsidian: memoria persistente entre sesiones (notas por línea, decisiones, pendientes, log de sesiones) |
| `.kimi-code/skills/` | Skills del proyecto: `inicializar` (cargar contexto) y `memoria` (actualizar bóveda al cerrar/avanzar) |
| `.github/workflows/update-dashboard.yml` | CI/CD pipeline |
| `task/todo.md` | Plan y revisión de la auditoría 2026-07-17 |

### 4. Líneas analizadas (11 corridas TP304L 2026-09-09/10, todas PASSED; informes y dashboard ACTUALIZADOS 2026-09-10)

| ID | Línea | PCF | Resultado .md |
|----|-------|-----|---------------|
| SIM-002 | Descarga recirculación 1 DDW | PCF103 | P2603-PR-SIM-002.md |
| SIM-003 | Descarga recirculación 2 DDW | PCF104 | P2603-PR-SIM-003.md |
| SIM-007 | Línea bomba vacío nueva | PCF107 | P2603-PR-SIM-007.md |
| SIM-008 | Succión recirculación 1 DDW | PCF106 | P2603-PR-SIM-008.md |
| SIM-009 | Succión recirculación 2 DDW | PCF105 | P2603-PR-SIM-009.md |
| SIM-010 | Succión recirculación 3 DDW | 10.pcf | P2603-PR-SIM-010.md |
| SIM-011 | Descarga bomba PP30BT03 | PCF108 | P2603-PR-SIM-011.md |
| SIM-012 | Succión TK Blowtank | PCF111 | P2603-PR-SIM-012.md |
| SIM-013 | Descarga tanque de nivelación | PCF113 | P2603-PR-SIM-013.md |
| SIM-014 | Descarga TMS | PCF112 | P2603-PR-SIM-014.md |
| SIM-015 | Tubería filtro de fibras PP1 | PCF114 | P2603-PR-SIM-015.md |

Cada carpeta 01.0–11.0 tiene `Graficas/` con Desplazamiento/NodosSoporte/StressPercent (tif + png convertidos) + AnexoResultado.png (EN ESPERA). OJO: los tifs de 03.0 (SIM-007) son de la corrida vieja TP304 → re-exportar. SIM-016 (12.0) tiene .C2 sin corrida; 13.0 sin corrida.

## Decisiones de diseño clave

### Parser CAESAR II (corregido 2026-07-17)
- **Normalización de saltos**: lectura con `newline=''` y reemplazo explícito `\r\n`/`\r` → `\n`; los .md antiguos mezclan `\r\r\n` (miles de CR sueltos) y eso destruía la detección de secciones
- **Secciones como listas**: cada página/caso genera una sección; compliance usa el ÚLTIMO CODE COMPLIANCE (resumen global); displacements/restraints hacen merge de casos CON datos (ope/sus/exp); stresses = máximo bending global
- **Regex clave**: job `P2603-PR-(?:PL-)?(?:SIM-)?\d+` (2026-09-03: PL opcional — las corridas nuevas se llaman `P2603-PR-SIM-XXX`; 003/007 viejos no llevan "SIM"), ratio `Ratio\s*\(%\):` (CAESAR pone espacio), caso `CASE \d+ \(([\w-]+)\)` (acepta "Alt-SUS"). Detección de isométrico: prefiere archivos `PCF*` (evita que `Dezplazamiento.png`/`NodosSoporte.png` se cuelen como isométrico)
- **Assets autocontenidos**: el parser copia isométricos a `dashboard/assets/iso/`, resultados gráficos a `dashboard/assets/graficos/` (desde `ResultadosGraficos*` de cada carpeta; ese prefijo se EXCLUYE de la detección de isométrico), .md a `dashboard/assets/md/` y el logo `assets/logo1.png` → `dashboard/assets/logo.png` → rutas relativas a `dashboard/`, funciona local y en Pages
- **Multi-gráfico (2026-09-02)**: `resultados_graficos` es LISTA de rutas (o null); un solo archivo conserva `SIM-XXX.png`, varios se numeran `SIM-XXX-N.png`. `linea.html` renderiza galería (acepta lista o string legacy). SIM-012: los `.tif` RGBA de CAESAR se convirtieron a `ResultadosGraficosPCF111-N.png` con PIL (los tif no los muestra el navegador)
- **Gráficas desde `Graficas/` (2026-09-10)**: `resultados_graficos` se alimenta de los PNG convertidos por `scripts/convertir_graficas.py` en cada `N.0/Graficas/` (excluye `AnexoResultado*` y `PCF*`); el isométrico se busca también en `Graficas/PCF*` (los PCF*.png ya no están en la raíz de las carpetas). Exclusión defensiva de `_corrida_anterior` en parser y `extraer_informe.py`

### Dashboard
- HTML estático + JSON dinámico → sin backend; páginas individuales por URL param `?id=SIM-XXX`
- HTML nunca asume FAILED ante datos faltantes: exige `typeof passed === 'boolean'`
- `linea.html` tiene sección "Resultados Gráficos — CAESAR II" (lightbox) alimentada por el campo JSON `resultados_graficos`; cuando es null muestra placeholder punteado "Espacio reservado…" que desaparece solo al correr el parser con la imagen presente
- Logos de Smurfit Westrock y DML Ingenieros Consultores en header de las 3 páginas (`assets/logo.png` y `assets/logo-dml.png`)

## Problemas recurrentes y soluciones

### PCF Plant 3D → CAESAR II
- Palabras clave nuevas no reconocidas por CAESAR II 2019 → `scripts/fix_pcf.py` con 6 transformaciones (resuelto 2026-07-08)

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
python scripts/fix_pcf.py "RUTA/NUEVA LINEA/archivo.pcf"
```

### Generar datos del dashboard (incluye copiar imágenes, gráficos, logo y .md)
```bash
python scripts/parse_caesar_md.py
# Genera dashboard/_data/lineas.json + dashboard/assets/{iso,graficos,md}/ + assets/logo.png
```

### Agregar resultados gráficos de una línea (SIM-008/009/010 pendientes)
1. Exportar desde CAESAR como `ResultadosGraficos*.png` en la carpeta de la línea
2. Ejecutar `python scripts/parse_caesar_md.py` y commitear PNG fuente + assets generados
3. El workflow se dispara automáticamente con cambios en `dashboard/**`, `scripts/**`, `.github/workflows/**`, archivos `.md` de las carpetas de línea y `**/ResultadosGraficos*`

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

### Generar informe LaTeX de una línea (pipeline generadorinf.md v1.1)
```bash
python scripts/extraer_informe.py --linea SIM-012   # tablas .tex + figuras + imágenes → informes/SIM-012/assets/
# Redactar sections/ + config/datos_proyecto.tex + references/bibliografia.bib (ver generadorinf.md secciones 4-6)
cd informes/SIM-012
JOB="I24.104-PP30-PP01-P-DOCS-187"
mkdir -p build
pdflatex -jobname="$JOB" -interaction=nonstopmode -output-directory=build main.tex
bibtex "build/$JOB"   # desde la raíz del informe, NO desde build/ (ruta relativa del .bib)
pdflatex -jobname="$JOB" -interaction=nonstopmode -output-directory=build main.tex
pdflatex -jobname="$JOB" -interaction=nonstopmode -output-directory=build main.tex
cp "build/$JOB.pdf" "$JOB.pdf"
```
- **OJO**: `compilar_informe.ps1` de la plantilla NO ejecuta bibtex → usar la secuencia manual de arriba si el informe cita bibliografía
- Piloto completado: SIM-012 → `informes/SIM-012/I24.104-PP30-PP01-P-DOCS-187.pdf` (22 pág., PASSED 32.4 % @130 EXP)
- Verificación numérica B31.3 hecha en el piloto: SE = √(Sb²+4St²) sin /2 (ec. 17, 319.4.4); CAESAR usa SA liberal (ec. 1b, 302.3.5(d)); Sc = Sh = 16.7 ksi TP304L
- Preview del PDF: `pdftoppm -f N -l N -r 60 -png archivo.pdf salida` (MiKTeX incluye poppler)

## Preguntas abiertas / bloqueos

- [x] GitHub repo creado (2026-07-17, público)
- [x] GitHub Pages habilitado — Source: GitHub Actions (2026-07-17)
- [x] Prueba de integración CI/CD — run success tras fix de permisos (2026-07-17)
- [x] Resultados gráficos CAESAR + logo DML en dashboard (2026-07-17, 4/7 líneas)
- [x] SIM-012 Succión TK Blowtank agregada: PCF corregido, análisis CAESAR PASSED (32.4 % @130 EXP), .md generado desde .OUT, 3 gráficos tif→png, JSON verificado 8/8 (2026-09-02)
- [x] Gráficos de las 11 líneas en dashboard (2026-09-10): tifs de `Graficas/` convertidos con `convertir_graficas.py`; JSON con 3–6 gráficas por línea
- [ ] Validación con cliente (pendiente, sitio ya desplegado)
- [x] Informe piloto SIM-012 generado: `informes/SIM-012/I24.104-PP30-PP01-P-DOCS-187.pdf` (2026-09-02)
- [ ] Firmas/autor/fechas de informes — datos del usuario ([POR CONFIRMAR] en datos_proyecto.tex de las 11 líneas)
- [x] Rollout informes COMPLETO (2026-09-10): 11/11 PDF DOCS-180→190 con números TP304L, 0 refs indefinidas, verificación visual OK
- [ ] **Discrepancia de presión (2026-09-08)**: informes/bases declaran 180 psig (1241 kPa g), pero el SLP de los .md indica que los modelos se corrieron con P2 ≈ 150 psi (≈1034 kPa); SIM-012 sin presión. Verificar en los .C2. OJO: la tabla de P/T se derivó de los .md VIEJOS — repetir sobre los .md del 2026-09-09/10. Tabla por línea en `boveda/20-Lineas/Resumen de líneas.md` (sección "Condiciones de operación")

## Referencias externas

- Normativa: ASME B31.3-2016, Jan 31, 2017
- Software: CAESAR II 2019 (Ver.11.00.00.4800), Intergraph CADWorx
- Cliente: Smurfit Westrock - Proyecto P2603 SW-K60
