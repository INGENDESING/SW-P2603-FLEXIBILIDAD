# Decisiones y lecciones

Registro de por qué se hizo cada cosa y errores ya resueltos. **Consultar antes de proponer cambios** para no repetir caminos descartados.

## Decisiones vigentes

- **Dashboard estático sin backend** (HTML + JSON): páginas individuales por URL param `?id=SIM-XXX`. Badge "SIN DATOS" gris cuando falta compliance — NUNCA pintar FAILED por datos faltantes (`typeof passed === 'boolean'`).
- **Assets autocontenidos**: el parser copia isométricos, gráficos, .md y logos dentro de `dashboard/assets/` → rutas relativas, funciona local y en Pages.
- **Informes: 8 PDF independientes** (D2), arquitectura **híbrida script+LLM** (D3): Python extrae números del .md, el LLM redacta prosa. Los números no se alucinan.
- **Codificación de informes**: `I24.104-PP30-PP01-P-DOCS-18X`, consecutivo desde 180 en orden SIM (SIM-002→180 … SIM-012→187). **Renumerado 2026-09-04 por instrucción del usuario** (antes desde 200): se actualizaron `\documentcode` en `datos_proyecto.tex`, el código en `06_alcance.tex`, los jobname y los nombres de PDF (los DOCS-20X fueron eliminados). Sin resumen ejecutivo (el informe ES el resumen); `02_resumen.tex` queda vacío.
- **Membrete de la plantilla**: se conserva el **layout original** (el rediseño geométrico 2026-09-02 fue REVERTIDO por el usuario). Lección: cambios estéticos de layout se proponen con render previo y esperan aprobación explícita.
- **Membrete tipografía uniforme 9pt, código en UNA línea (2026-09-04, aprobado por el usuario)**: TODO el texto del membrete usa `\headerfont` = `\fontsize{9}{10}`; la jerarquía se da solo por negrita (título y etiquetas bold; sublíneas y valores regular). Columnas: logos 2.2 cm (img 2.0×2.2), X central, etiquetas `m{2.1cm}`, **valores `m{4.5cm}`** (ancho necesario para que el código `I24.104-PP30-PP01-P-DOCS-18X`, 28 car., quepa en una sola línea a 9pt — el usuario lo pidió explícitamente; NUNCA debe envolver); arraystretch 0.90, tabcolsep 2pt. Historial: se pidió primero 11pt, luego 9pt, y finalmente código en una línea (valores 3.1→4.5 cm; la columna central X absorbe la diferencia y las sublíneas siguen en 2 líneas sin traslapes). Lección: interlineado ≈ tamaño+1pt + arraystretch 0.90 hace que una celda de 2 líneas ≈ 2 filas de multirow. babel-spanish pone `\uchyph=0`: los textos en MAYÚSCULAS NO se hyphenan, los wraps son solo en espacios/guiones. Propagado a las 9 copias de `header.tex` (idénticas por md5) y recompilados los 8 PDF (0 refs indefinidas, 0 overfull vbox, mismas páginas).
- **Firmas de informes**: ELABORÓ J.ARBOLEDA, REVISÓ F.NAVIA, APROBÓ H.ROSERO. Fechas [DD/MM/AAAA] pendientes del usuario. logo1 = DML, logo2 = Smurfit (verificar tras copiar plantilla: una vez logo2 quedó duplicado con el logo DML).
- **Plantilla LaTeX**: NO editar `main.tex`, `preamble.tex`, `header.tex` (regla de la plantilla); solo `datos_proyecto.tex`, `sections/`, `references/`, `assets/`.
- **Portada y hoja de firmas (instrucción del usuario, 2026-09-03)**: son las ÚNICAS dos páginas del informe cuyas tablas llevan rejilla completa (todas las líneas verticales y horizontales, `{|...|}` + `\hline` por fila + `\rowcolor{green!15}` en encabezados). El resto del informe sigue en formato Elsevier (booktabs, sin bordes verticales). **Aplicado en los 8 informes + `Plantilla latex/` (2026-09-04)**: los archivos `00_portada.tex` (3 tablas) y `00_hojafirmas.tex` (2 tablas) están 100 % parametrizados con macros de `datos_proyecto.tex` → las 8 copias son idénticas (md5 único) y se propagan por copia desde SIM-002.
- **Convención de nombres (2026-09-03)**: carpetas de simulación con prefijo `1.0`–`8.0` en orden SIM; archivos de entrada CAESAR = `P2603-PR-SIM-XXX.C2` (sin "-PL"; 003/007 ya normalizados con "SIM"; SIM-010 no tiene .C2). Los .md/.tif/.wrn conservan el nombre viejo `P2603-PR-PL-...` por decisión del usuario (solo se renombraron .C2) — el regex del parser sigue siendo el de siempre.
- **Reorganización 2026-09-11 (vigente)**: carpetas de línea con prefijo de **dos dígitos** `01.0`–`13.0` (el de un dígito desordenaba: 1.0, 10.0, 11.0, 2.0…); `fix_pcf.py` vive en `scripts/`, el logo fuente en `assets/logo1.png`. Los scripts usan globs de un nivel (`*/P2603-PR-*.md`, `*/Graficas`) agnósticos al prefijo — **no crear una carpeta padre `lineas/`** (rompería los globs). Scratch CAESAR (CONTROLU/OCONTROLU/DBGENBIN/COMNDINP/TEMPMAT*/`*.c2db`/`*.XML`) queda en disco pero fuera de git (`.gitignore`); CAESAR lo regenera junto al .C2.
- **Triggers del workflow agnósticos al nombre de carpeta (2026-09-11)**: `.github/workflows/update-dashboard.yml` usa `'**/P2603-PR-*.md'` + `'**/Graficas/**'`. Lección: los patrones con nombre de carpeta literal quedan obsoletos silenciosamente tras un renombrado → usar siempre patrones por nombre de archivo.

## Errores resueltos (no repetir)

### Parser CAESAR II (2026-07-17)
- Los .md de CAESAR mezclan `\r\r\n` (miles de CR sueltos) → SIEMPRE normalizar saltos (`newline=''` + reemplazo explícito) antes de parsear.
- Regex vigentes: job `P2603-PR-PL-(?:SIM-)?\d+`, ratio `Ratio\s*\(%\):` (CAESAR pone espacio), caso `CASE \d+ \(([\w-]+)\)` (acepta "Alt-SUS").
- Compliance usa el ÚLTIMO CODE COMPLIANCE (resumen global), nunca valores parciales por caso.
- Verificación obligatoria tras regenerar JSON: comparar ratio/nodo contra [[20-Lineas/Resumen de líneas|la tabla verdad]].

### GitHub Pages (2026-07-17)
- Repo debe ser público (cuenta Free). Pages Source = "GitHub Actions" (no "Deploy from a branch": eso publica la raíz con Jekyll y excluye `_data/`).
- Todo job con `permissions` propios debe incluir `contents: read` si usa `actions/checkout`.

### SIM-012 (2026-09-02)
- Los `.tif` RGBA de CAESAR no los muestra el navegador → convertir a PNG con PIL.
- `compilar_informe.ps1` NO ejecuta bibtex → secuencia manual pdflatex→bibtex→pdflatex×2 (bibtex desde la raíz del informe, NO desde `build/`).
- B31.3: SL en 302.3.5 (no 304.3.5 — error corregido en generadorinf v1.0).

### Material TP304 residual en modelos CAESAR (2026-09-10)
- Síntoma: tras la recorrida "TP304L", SIM-007 y SIM-011 seguían con elementos en TP304. Detección robusta sin abrir el .C2: contar `137895.1` en el .md y, sobre todo, **comparar el admisible EXP contra el techo TP304L**: SA máx = 1.25×(115142.4+115142.4) = 287856 kPa; cualquier admisible EXP mayor (SIM-007: 325881.3; SIM-011: 314324.3/318970.1) solo se explica con Sc=Sh=137895.1 (20 ksi). Con SL del propio reporte se recalcula el ratio real: SA(TP304L) = 287856 − SL.
- Al corregir el material, los ESFUERZOS pueden cambiar (SIM-007: 279.6→191.8 MPa; el material trae E y propiedades) → las gráficas de la corrida vieja quedan obsoletas. En SIM-011 solo cambió el admisible (esfuerzos idénticos) → sus tifs siguieron válidos. Regla: tras una recorrida, comparar Code stresses antes de reusar gráficas.
- CAESAR no siempre guarda el cambio de material en la primera recorrida: la del 13:58 de SIM-007 salió idéntica a la anterior; la del 14:42 (con el .C2 modificado, 61 523 vs 61 168 bytes) sí reflejó el cambio.

### Informes: tablas largas de esfuerzos (2026-09-10)
- `extraer_informe.py` emite `tab_esfuerzos_critico.tex` como float `table`; con >~50 filas desborda la página ("Float too large"). Se convirtió a mano a `longtable` en SIM-010 (178 filas), SIM-011 (156), SIM-012 (58) y SIM-015 (136). **La conversión se pierde al re-ejecutar el script** → pendiente emitir longtable automático.
- Esquema de assets de gráficas CAESAR (2026-09-10): `graf_desplazamiento[_N].png` → §9.1, `graf_stress_percent[_N].png` → §9.2, `graf_nodos_soporte[_N].png` → §9.3 (sufijo `_N` solo si hay más de una vista). Los `.tex` de los 11 informes ya usan este esquema; los assets viejos (`NodosSoporte.png`, `Dezplazamiento.png`, `ResultadosGraficos*`) quedaron sin referencia.
- El warning `\Bbbk already defined` (MiKTeX + plantilla) es benigno y aparece en todos los informes; no es falla de compilación.

### PCF corrupto de Plant 3D: coordenada centinela y duplicación 58× (2026-09-22, PCF120)
- Plant 3D vuelca los componentes sin geometría resuelta en la coordenada centinela **(-9776646, -9840066, -102887) con bore 0.0000**, como PRIMER bloque de cada sección `PIPELINE-REFERENCE`. En PCF120: 57 bloques (24 FLANGE LJ, 11 VALVE, 18 SUPPORT, 2 OLET, 2 ELBOW 45 SW). No es defecto de `fix_pcf.py` (ya venía en el original).
- El mismo defecto **duplica gaskets/pernos/welds en TODAS las secciones** (PCF120: 1336 gaskets → 25 únicos, 1162 pernos → 22, 148 welds → 91; factor ≈58 = n.º de secciones). CAESAR los ignora, pero la duplicación invalida cualquier heurística de "hardware vecino" para ubicar componentes. PCF118 sano no la tiene (45/45).
- **Rescate determinista**: los stub-ends quedan en coordenadas reales aunque sus bridas se pierdan → emparejarlos (colineales, enfrentados, mismo bore) reconstruye cada unión: FF = gap − 2×3.175 mm; el FF identifica el tipo de válvula (knife 3"=50.96, check 3"=73.0, butterfly 3"≈42-47, mag meter 4"=248). El bore se toma del tubo vecino en el nodo compartido.
- `fix_pcf.py` degrada los stub-ends sin pareja a PIPE **sin SKEY**: al fusionarlos a FLANGE hay que reponer `SKEY FLWN` explícitamente.
- **PCF: `CENTRE-POINT` de un ELBOW es la intersección de las tangentes**, no el centro del arco (verificado con un ELL 90 SW real). Plant 3D puede dejar `ANGLE` corrupto en bloques basura (9000 en unos ELL 45 → corregir a 4500).
- Script: `scripts/fix_pcf120_basura.py` (`--proponer`/`--aplicar`/`--verificar`). Reusable si otro PCF llega con el mismo defecto.

## Estilo de entregables (de `AGENTS.md`)

- Prohibido viñetas en informes cliente; tablas Elsevier (`toprule/midrule/bottomrule`, sin bordes verticales, leyenda arriba).
- Figuras con leyenda debajo, citadas antes de aparecer; ecuaciones numeradas con variables definidas después.
- `siunitx` con espacio valor-unidad (`25 °C`); voz impersonal; trazabilidad de todo número al `.md`.
