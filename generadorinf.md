# Generador de Informes LaTeX — Análisis de Flexibilidad de Tuberías

> Prompt maestro para la generación de informes técnicos de análisis de flexibilidad
> a partir de reportes CAESAR II 2019. Reemplaza a `PropmtGeneracionInformes.txt`
> (borrador original, conservado solo como referencia histórica).

---

## 1. Control del documento

| Campo | Valor |
|---|---|
| Versión | 1.1 |
| Fecha | 2026-09-02 |
| Proyecto | P2603 SW-K60 — Cartón Colombia |
| Cliente | Smurfit Westrock |
| Consultora | DML Ingenieros Consultores |
| Norma de análisis | ASME B31.3-2016 |
| Software de origen | CAESAR II 2019 (Ver.11.00.00.4800) |
| Plantilla LaTeX | `Plantilla latex/` (clase `elsarticle`, corporativa DML) |
| Fuente de verdad numérica | Reportes `.md` de CAESAR II en la carpeta de cada línea |
| Producto | Un informe PDF independiente por línea (9 informes) |
| Codificación de informes | `I24.104-PP30-PP01-P-DOCS-18X` — consecutivo desde 180 (instrucción del cliente) |

Líneas válidas, su verdad CAESAR (ratio/nodo/caso del resumen global CODE COMPLIANCE)
y su código de informe asignado:

| Código informe | ID | Línea | Carpeta | Job CAESAR | Ratio máx | Nodo | Caso crítico |
|---|---|---|---|---|---|---|---|
| I24.104-PP30-PP01-P-DOCS-180 | SIM-002 | Descarga recirculación 1 DDW | `DESCARGA DE BOMBA DE RECIRCULACION 1 DDW` | P2603-PR-PL-SIM-002 | 28.8 % | 78 | 6 (SUS) W+P2 |
| I24.104-PP30-PP01-P-DOCS-181 | SIM-003 | Descarga recirculación 2 DDW | `DESCARGA DE BOMBA DE RECIRCULACION 2 DDW` | P2603-PR-PL-003 | 13.1 % | 120 | 4 (Alt-SUS) W+P2 |
| I24.104-PP30-PP01-P-DOCS-182 | SIM-007 | Línea bomba vacío nueva | `LINEA DE BOMBA DE VACIO NUEVA` | P2603-PR-PL-007 | 85.7 % | 100 | 8 (EXP) L8=L3-L6 |
| I24.104-PP30-PP01-P-DOCS-183 | SIM-008 | Succión recirculación 1 DDW | `SUCCION DE BOMBA DE RECIRCULACION 1 DDW` | P2603-PR-PL-SIM-008 | 12.2 % | 200 | 4 (Alt-SUS) W+P2 |
| I24.104-PP30-PP01-P-DOCS-184 | SIM-009 | Succión recirculación 2 DDW | `SUCCION DE BOMBA DE RECIRCULACION 2 DDW` | P2603-PR-PL-SIM-009 | 20.8 % | 60 | 4 (Alt-SUS) W+P2 |
| I24.104-PP30-PP01-P-DOCS-185 | SIM-010 | Succión recirculación 3 DDW | `SUCCION DE BOMBA DE RECIRCULACION 3 DDW` | P2603-PR-PL-SIM-010 | 60.9 % | 310 | 6 (SUS) W+P2 |
| I24.104-PP30-PP01-P-DOCS-186 | SIM-011 | Descarga bomba PP30BT03 | `DESCARGA BOMBA PP30BT03` | P2603-PR-PL-SIM-011 | 56.1 % | 260 | 4 (Alt-SUS) W+P2 |
| I24.104-PP30-PP01-P-DOCS-187 | SIM-012 | Succión TK Blowtank | `SUCCION TK BLOWTANK` | P2603-PR-PL-SIM-012 | 32.4 % | 130 | 8 (EXP) L8=L3-L6 |
| I24.104-PP30-PP01-P-DOCS-188 | SIM-013 | Descarga tanque de nivelación | `9.0 DESCARGA TANQUE DE NIVELACION` | P2603-PR-SIM-013 | 24.3 % | 100 | 2 (Alt-SUS) W+P2 |

Las 9 líneas tienen `CODE COMPLIANCE EVALUATION PASSED`.

---

## 2. Rol y alcance del generador

El ejecutor de este prompt actúa como ingeniero de tuberías senior que documenta
resultados ya calculados. Produce: un informe técnico PDF por línea, compilado con
pdfLaTeX sobre la plantilla corporativa DML, con tablas y figuras extraídas
programáticamente de los reportes CAESAR II.

El generador **NO**:

1. Recalcula ni modifica los modelos CAESAR II (los archivos `.C2`, `.pcf` y `.md` son intocables).
2. Cambia las bases de diseño congeladas (sección 3.4): se citan, no se re-derivan.
3. Inventa valores de propiedades, esfuerzos admisibles o coeficientes: todo número del
   informe debe ser trazable al `.md` de la línea o a una norma citada.
4. Edita `main.tex`, `config/preamble.tex` ni `config/header.tex` de la plantilla.

---

## 3. Insumos por línea (contrato de entrada)

### 3.1 Reporte CAESAR II `.md` — fuente de verdad numérica

Ubicación: `<CARPETA>/P2603-PR-PL-*.md` (ver tabla de líneas). Contenido verificado:

- 9 casos de carga × 3 reportes: `DISPLACEMENTS REPORT` (movimientos nodales DX…RZ),
  `RESTRAINTS REPORT` (cargas FX…MZ con `TYPE=` por soporte), `B31.3 STRESSES REPORT`
  (SLP, F/A, Bending, Torsion, SIF, Code, Allowable, Ratio por nodo).
- SIM-012 incluye además `RESTRAINTS EXTENDED REPORT` (ignorar; usar solo `RESTRAINTS REPORT`).
- 1 `CODE COMPLIANCE REPORT` final con el resumen global:
  `*** CODE COMPLIANCE EVALUATION PASSED ***`, `Highest Stresses`, `Ratio (%)`,
  `@Node`, `LOADCASE`, `Code Stress`, `Allowable Stress`.
- Distribución de casos (verificada en SIM-002): 2 OPE, 2 Alt-SUS, 2 SUS, 3 EXP.
  Extraer la tabla de casos de carga del propio `.md` de cada línea, no asumirla.

**Regla de oro**: el ratio, nodo y caso crítico que aparezcan en el informe deben ser
idénticos al resumen global CODE COMPLIANCE del `.md`, nunca a valores parciales de
una sección por caso. Antes de redactar, verificar contra la tabla de la sección 1.

**Precaución de formato**: los `.md` de CAESAR mezclan `\r\n` y `\r` sueltos. Todo
script que los lea debe abrir con `newline=''` y normalizar `\r\n`/`\r` → `\n` antes
de parsear (lección aprendida 2026-07-17; ver `scripts/parse_caesar_md.py`).

### 3.2 JSON del dashboard — apoyo para figuras

`dashboard/_data/lineas.json` contiene por línea: compliance (ratio, nodo, caso,
code/allowable), desplazamientos nodales OPE/SUS/EXP (DX…RZ), cargas en restricciones
con tipo de soporte, bending máximo. Úsese para curvas de desplazamiento y tablas de
restricciones. Las tablas de esfuerzo por nodo NO están en el JSON: salen del `.md`.

### 3.3 Imágenes

- Isométrico: `PCF1XX.png` (o `.jpeg`/`.jpg`) en la carpeta de la línea — figura obligatoria.
- Resultados gráficos CAESAR: `ResultadosGraficos*.png` en la carpeta de la línea.
  Disponibles en SIM-002, 003, 007, 011, 012. En SIM-008, 009 y 010 NO existen:
  insertar párrafo "Resultados gráficos pendientes de exportación desde CAESAR II"
  en lugar de una imagen falsa (ver sección 9).

### 3.4 Bases de diseño congeladas (citar textualmente, fuente: `contexto.md`)

| Parámetro | Valor |
|---|---|
| Norma | ASME B31.3-2016 |
| Material | ASTM A312 TP 304L, Sch 10S, sin tolerancia de corrosión (CA = 0) |
| Presión de diseño | 180 psig = 1241 kPa g (12.41 bar g) |
| Temperatura de operación | 90 °C (ΔT = 65 °C respecto a instalación a 25 °C) |
| Fluido | Agua (SG = 1.0; densidad 1000 kg/m³ = 0.001 kg/cm³) |
| Casos de carga | OPE = W+T1+P1, SUS = W+P1, EXP = OPE−SUS (combinaciones exactas por línea, del `.md`) |

### 3.5 Plantilla LaTeX

`Plantilla latex/`: clase `elsarticle` A4 12pt, TG Termes, pdfLaTeX, UTF-8.
Convenciones obligatorias documentadas en `Plantilla latex/CLAUDE_plantilla.md`.
Solo se editan: `config/datos_proyecto.tex`, `sections/*.tex`,
`references/bibliografia.bib`, `assets/`.

---

## 4. Estructura obligatoria del informe

Mapeo 1:1 con los archivos de la plantilla. El informe ES un resumen ejecutivo:
extensión objetivo 10–15 páginas sin contar anexos.

| Archivo `sections/` | Contenido requerido |
|---|---|
| `00_portada.tex` | Sin cambios estructurales; toma título, código y revisión de `datos_proyecto.tex` |
| `00_hojafirmas.tex` | Firmas elaboró/revisó/aprobó desde `datos_proyecto.tex` (datos que debe confirmar el usuario) |
| `01_frontmatter.tex` | Abstract ≤ 200 palabras: línea, norma B31.3, veredicto PASSED/FAILED, ratio máximo, nodo y caso crítico. Keywords: flexibilidad de tuberías, CAESAR II, ASME B31.3, esfuerzos, desplazamientos |
| `02_resumen.tex` | **VACÍO (solo comentarios LaTeX)**: NO se genera resumen ejecutivo — el informe en sí ES el resumen ejecutivo (instrucción explícita del cliente). El archivo se conserva vacío porque `main.tex` lo incluye y `main.tex` no se edita |
| `03_nomenclatura.tex` | Abreviaturas del proyecto: CAESAR II, OPE, SUS, Alt-SUS, EXP, SIF, DDW, TK, SG, CA, PCF, NPS, Sch; símbolos: SL, SE, SA, i, W, T1, P1. Los índices (contenido, tablas, figuras) los genera `main.tex` automáticamente |
| `04_introduccion.tex` | Marco teórico: propósito del análisis de flexibilidad; CAESAR II y el método de elementos finitos para sistemas de tuberías; ecuaciones de ASME B31.3-2016 para esfuerzo sostenido SL (302.3.5) y esfuerzo de expansión SE con factor de intensificación i (319.4.4); criterio de aceptación Code ≤ Allowable. Ecuaciones numeradas con variables definidas inmediatamente después. **Contenido teórico investigado en internet con agentes** (ver paso 3 del pipeline, sección 7): solo fuentes citables |
| `05_objetivos.tex` | Objetivo general (verificar el cumplimiento de la línea según ASME B31.3-2016) y específicos (evaluar esfuerzos por caso, desplazamientos, cargas en soportes y equipos). Redacción apoyada en la misma investigación web del marco teórico |
| `06_alcance.tex` | Línea analizada con su job CAESAR; límites del modelo (anclas, boquillas de equipo); exclusiones (no incluye cargas de viento/sismo salvo que el `.md` las reporte) |
| `07_bases_disenio.tex` | Tabla de condiciones de la sección 3.4 (instalación → operación), material y código, tabla de casos de carga extraída del `.md` de la línea |
| `08_metodologia.tex` | Flujo: AutoCAD Plant 3D 2027 → PCF → corrección con `fix_pcf.py` → CAESAR II 2019 → reporte `.md` → verificación contra resumen global |
| `09_resultados.tex` | 9.1 Desplazamientos: tabla de máximos |DX|,|DY|,|DZ| por caso (OPE/SUS/EXP) + figura de curvas DX/DY/DZ vs nodo (matplotlib, desde JSON). 9.2 Esfuerzos: tabla por nodo del caso crítico (Node, Bending, Code, Allowable, Ratio; desde `.md`) + figura esfuerzo vs nodo. 9.3 Restricciones: tabla de cargas FX…MZ y tipo de soporte por nodo para los casos OPE/SUS/EXP. 9.4 Figuras: isométrico y resultados gráficos CAESAR (si existen) |
| `10_analisis.tex` | Code compliance: tabla de los 5 nodos de mayor ratio del caso crítico con columna cumple/no cumple; discusión del caso crítico (por qué gobierna, magnitud vs admisible); comparación con el resto de casos |
| `11_conclusiones.tex` | Una conclusión por hallazgo, en párrafos numerados (no viñetas) |
| `12_recomendaciones.tex` | Recomendaciones operativas/constructivas derivadas de los resultados; si no aplica, justificarlo |
| `13_anexos.tex` | Tablas completas de esfuerzos y desplazamientos de todos los casos (lo que exceda la sección 9); resto de resultados gráficos CAESAR |
| `references/bibliografia.bib` | ASME B31.3-2016; CAESAR II 2019 User Guide (Hexagon/Intergraph); ASME B16.5 y B16.9 (componentes); citar con `~\cite{...}` |

`config/datos_proyecto.tex` por línea: `\projecttitle` = "Análisis de flexibilidad —
<NOMBRE LÍNEA>"; `\documentcode` = código asignado en la tabla de la sección 1
(`I24.104-PP30-PP01-P-DOCS-18X`);
`\documenttype` = INFORME TÉCNICO — ANÁLISIS DE FLEXIBILIDAD; `\targetcompany` =
Smurfit Westrock; `\projectnumber` = P2603 SW-K60; membrete: `\headerlinetitulo` =
ANÁLISIS DE FLEXIBILIDAD DE TUBERÍAS, `\headerlinesubuno` = <NOMBRE LÍNEA>,
`\headerlinesubdos` = ASME B31.3-2016. Firmas y fechas: confirmar con el usuario
antes de emitir (no inventar nombres).

---

## 5. Reglas de estilo (obligatorias, autocontenidas)

1. **Prohibido el uso de viñetas** en el cuerpo del informe. Usar tablas estilo
   Elsevier (`\toprule`, `\midrule`, `\bottomrule`; sin bordes verticales; leyenda
   arriba con `\caption{} \label{tab:...}`) o párrafos numerados.
2. Figuras con leyenda debajo, referenciadas en el texto antes de aparecer
   (`Figura~\ref{fig:...}`), ancho preferido `width=0.85\textwidth`.
3. Ecuaciones numeradas a la derecha con `\label{eq:...}`; variables definidas
   inmediatamente después de cada ecuación.
4. Unidades con `siunitx` y espacio entre valor y unidad: `1241~\si{kPa}`,
   `90~\si{\celsius}`. SI por defecto; valores imperiales solo entre paréntesis
   cuando la norma o el dato de origen lo exija (p. ej. 180 psig).
5. Voz técnica impersonal; presente para método, pasado para resultados. Párrafos
   densos, una idea por párrafo, sin relleno.
6. Trazabilidad: todo número del informe proviene del `.md` de la línea, del JSON
   del dashboard, de la sección 3.4 o de una norma citada. Ningún otro origen.
7. Tablas generadas por script: el script produce el cuerpo de la tabla en formato
   LaTeX Elsevier listo para `\input{}`; la prosa nunca transcribe números a mano.
8. No editar `main.tex`, `config/preamble.tex`, `config/header.tex`.

---

## 6. Mapeo dato → fuente (contrato de trazabilidad)

| Elemento del informe | Fuente exacta |
|---|---|
| Veredicto PASSED/FAILED | Línea `*** CODE COMPLIANCE EVALUATION … ***` del `.md` |
| Ratio máx, nodo, caso crítico | Resumen global CODE COMPLIANCE del `.md` (validar contra tabla sección 1) |
| Code Stress / Allowable | `Code Stress:` / `Allowable Stress:` del resumen global del `.md` |
| Tabla de casos de carga | Líneas `CASE n (TIPO) combinación` del `.md` de la línea |
| Tabla esfuerzos por nodo (caso crítico) | `B31.3 STRESSES REPORT` del caso crítico en el `.md` |
| Tabla top-5 nodos por ratio | Columna `Ratio` del `B31.3 STRESSES REPORT` del caso crítico |
| Tabla máximos de desplazamiento | `displacements.load_cases.*.max_dx/dy/dz` del JSON (o DISPLACEMENTS REPORT del `.md`) |
| Curvas DX/DY/DZ vs nodo | `displacements.load_cases.ope.nodes` del JSON (matplotlib) |
| Tabla cargas en soportes | `restraints.load_cases.*.nodes` del JSON (campos fx…mz, type) o RESTRAINTS REPORT del `.md` |
| Curva esfuerzo vs nodo | Columna `Bending` vs `Node` del `B31.3 STRESSES REPORT` (caso crítico) |
| Isométrico | `PCF1XX.png/.jpeg` de la carpeta de la línea |
| Resultados gráficos CAESAR | `ResultadosGraficos*.png` de la carpeta de la línea (si existe) |
| Bases de diseño | Sección 3.4 de este documento (fuente única: `contexto.md`) |

---

## 7. Pipeline de ejecución (arquitectura híbrida)

Ejecutar por línea, en orden:

1. **Copiar plantilla**: `Plantilla latex/` → `informes/SIM-0XX/` (sin `build/` ni PDFs de prueba).
2. **Extracción programática** (script Python, p. ej. `scripts/extraer_informe.py --linea SIM-0XX`):
   lee el `.md` (con normalización de saltos de línea) y el JSON; genera en
   `informes/SIM-0XX/assets/`:
   - `tab_casos.tex`, `tab_esfuerzos_critico.tex`, `tab_top5_ratio.tex`,
     `tab_desplazamientos_max.tex`, `tab_restricciones_{ope,sus,exp}.tex` — cuerpos de
     tabla Elsevier listos para `\input{}`.
   - `fig_desplazamientos.png`, `fig_esfuerzos.png` — curvas matplotlib (300 dpi, fondo blanco).
   - Copia del isométrico y de los `ResultadosGraficos*.png` (si existen).
3. **Investigación teórica con agentes web** (instrucción explícita del cliente):
   lanzar agentes de investigación en internet para los aspectos teóricos de la
   introducción, los objetivos y el marco teórico (qué es CAESAR II, modelos y
   principios matemáticos y físicos que usa, formulación B31.3). Reglas: solo fuentes
   citables (ASME B31.3-2016, CAESAR II 2019 User Guide, papers con DOI, NIST,
   documentación oficial Hexagon); cada afirmación teórica queda registrada con su
   fuente en `references/bibliografia.bib`; prohibido inventar valores de propiedades
   o coeficientes (si no hay fuente, se omite o se pide al usuario). Esta investigación
   se hace UNA vez para el proyecto y su material se reutiliza en las 8 líneas
   (el marco teórico es común; solo cambian los datos de la línea).
4. **Redacción**: llenar `config/datos_proyecto.tex` y las `sections/` con la prosa
   técnica; las tablas se insertan con `\input{assets/tab_*.tex}`; la prosa cita los
   números del resumen global ya verificados (sección 6), nunca transcribe tablas.
   `02_resumen.tex` queda vacío (sección 4).
5. **Bibliografía**: completar `references/bibliografia.bib` con las fuentes del paso 3
   y las normas; citar en el texto con `~\cite{...}`.
6. **Compilación**: `compilar_informe.ps1 -jobName "<CODIGO_INFORME>"` desde
   `informes/SIM-0XX/` (doble pasada pdflatex → `build/I24.104-PP30-PP01-P-DOCS-18X.pdf`).
7. **Verificación**: checklist de la sección 8. Si algo falla, corregir y recompilar.
8. Repetir para las 8 líneas. Al final, actualizar `contexto.md` con el estado de
   los informes generados.

---

## 8. Lista de verificación final (obligatoria antes de entregar cada PDF)

1. Compila sin errores ni `??` (referencias cruzadas resueltas tras doble pasada).
2. Ratio, nodo y caso crítico del informe == resumen global CODE COMPLIANCE del `.md`
   == tabla de la sección 1 de este prompt.
3. Toda tabla de la sección 9/10 del informe proviene de `\input{assets/tab_*.tex}`
   generado por script (no transcrita a mano).
4. Cero viñetas en el cuerpo; tablas Elsevier con leyenda arriba; figuras con leyenda
   debajo y citadas antes de aparecer; unidades `siunitx` con espacio valor-unidad.
5. Coherencia interna: mismas bases de diseño, unidades y nomenclatura en todas las
   secciones; abreviaturas usadas están en `03_nomenclatura.tex`.
6. Líneas sin resultados gráficos (SIM-008/009/010): placeholder textual presente,
   sin imagen falsa ni espacio roto.
7. Órdenes de magnitud razonables: ratio < 100 % en líneas PASSED; desplazamientos
   en mm coherentes con el `.md`; esfuerzos en kPa.
8. El código del documento en portada, membrete y nombre del PDF == asignación de la
   tabla de la sección 1 (`I24.104-PP30-PP01-P-DOCS-18X`); `02_resumen.tex` vacío
   (sin resumen ejecutivo).
9. PDF final en `informes/SIM-0XX/build/I24.104-PP30-PP01-P-DOCS-18X.pdf` y copia en la raíz de
   `informes/SIM-0XX/` (comportamiento del script de compilación).

---

## 9. Casos borde y trampas conocidas

1. **Sin resultados gráficos** (SIM-008/009/010): párrafo textual "Los resultados
   gráficos de CAESAR II se encuentran pendientes de exportación." Nunca generar
   imagen sustituta.
2. **Valores `N/A` en restricciones**: tratar como 0.0 en tablas numéricas y notar
   "N/A" en la celda si se reporta el valor textual (criterio ya usado en
   `scripts/parse_caesar_md.py`).
3. **Jobs sin "SIM" en el nombre**: SIM-003 (`P2603-PR-PL-003`) y SIM-007
   (`P2603-PR-PL-007`); además el archivo de SIM-007 tiene un espacio en el nombre
   (`P2603-PR-PL-007 .md`). Referenciar siempre por la tabla de la sección 1.
4. **Saltos de línea mixtos** en los `.md` (`\r\r\n`): normalizar antes de parsear
   (sección 3.1). Ignorar líneas vacías al detectar secciones.
5. **RESTRAINTS EXTENDED** (SIM-012): ignorar; usar solo `RESTRAINTS REPORT`.
6. **Bending máximo global vs code stress**: el bending del caso EXP puede superar el
   code stress del compliance (magnitudes distintas: esfuerzo de expansión vs
   sostenido); no reportarlo como inconsistencia.
7. **Alt-SUS vs SUS**: el caso crítico puede ser Alt-SUS (W+P2) en varias líneas;
   transcribir la designación exacta del `.md`, no "corregirla".
8. **Firmas y fechas de emisión**: deben confirmarlas el usuario; dejar
   `[POR CONFIRMAR]` en `datos_proyecto.tex` si no se tienen, nunca inventarlas.

---

## 10. Ejecución de este prompt

Este documento es la especificación completa. Para ejecutarlo en una sesión futura:
leer este archivo, `contexto.md` y `Plantilla latex/CLAUDE_plantilla.md`; registrar
el plan de la línea en `task/todo.md` siguiendo `AGENTS.md` (fase 1) y esperar
aprobación; luego ejecutar el pipeline de la sección 7 línea por línea.
