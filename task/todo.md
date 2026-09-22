# Plan: Corrección parser CAESAR II → dashboard (auditoría 2026-07-17)

## Contexto
- Objetivo: El dashboard muestra 6 de 7 líneas como "FAILED" y ratio 0.0 % en la única "PASSED". CAESAR II arrojó **CODE COMPLIANCE EVALUATION PASSED en las 7 líneas**. El error está en `scripts/parse_caesar_md.py` y en el render que trata "sin datos" como "FAILED".
- Cliente / Proyecto DML: Smurfit Westrock — P2603 SW-K60
- Normas aplicables: ASME B31.3-2016

## Verdad CAESAR (extraída de los .md, verificada por grep)
| Línea | Estado | Ratio máx | Nodo | Caso crítico |
|---|---|---|---|---|
| SIM-002 Descarga recirc. 1 DDW | PASSED | 28.8 % | 78 | 6 (SUS) W+P2 |
| SIM-003 Descarga recirc. 2 DDW | PASSED | 13.1 % | 120 | 4 (Alt-SUS) W+P2 |
| SIM-007 Línea bomba vacío | PASSED | 85.7 % | 100 | 8 (EXP) L8=L3-L6 |
| SIM-008 Succión recirc. 1 DDW | PASSED | 12.2 % | 200 | 4 (Alt-SUS) W+P2 |
| SIM-009 Succión recirc. 2 DDW | PASSED | 20.8 % | 60 | 4 (Alt-SUS) W+P2 |
| SIM-010 Succión recirc. 3 DDW | PASSED | 60.9 % | 310 | 6 (SUS) W+P2 |
| SIM-011 Descarga PP30BT03 | PASSED | 56.1 % | 260 | 4 (Alt-SUS) W+P2 |

## Causas raíz identificadas (scripts/parse_caesar_md.py)
- A. Ventana de detección de REPORT de 4 líneas (`min(i + 5, ...)`): los 6 .md antiguos tienen finales mixtos `\r\r\n` (1 307–6 666 CR sueltos por archivo); el modo texto de Python convierte cada `\r` en `\n` → líneas en blanco extra → la línea `REPORT:` queda fuera de la ventana → 0 secciones → JSON vacío. SIM-011 es CRLF puro → único que parseó.
- B. `JOB_PATTERN` exige "SIM" en el nombre → jobs 003 y 007 quedan "UNKNOWN" (colisión de id en linea.html).
- C. Regex de ratio `Ratio\(%\):` sin espacio; el texto real es `Ratio (%):` → SIM-011 quedó con ratio 0.0 % y nodo 0.
- D. Regex de caso `CASE \d+ \((\w+)\)` no acepta guion → "(Alt-SUS)" no matchea → load cases vacíos incluso en SIM-011.
- E. `sections[section_type] = ...` conserva solo el ÚLTIMO reporte de cada tipo → para DISPLACEMENTS el último suele tener "Output disabled" (sin datos); se pierde el caso OPE. En CODE COMPLIANCE el último es el resumen global (correcto por accidente).
- F. HTML (`index.html:164/192`, `linea.html:170`, `tecnico.html:190`): `passed ? PASSED : FAILED` pinta FAILED cuando `passed` es `undefined` (dato faltante ≠ fallido).

## Supuestos clave
- [x] Los .md son la fuente de verdad (verificado por grep directo, no por el JSON)
- [x] El caso de desplazamientos de interés para el dashboard es OPE (CASE 1), presente en todos los .md

## Tareas
- [x] T1. Parser: normalizar contenido (`\r\n`/`\r` → `\n`) y/o ignorar líneas vacías en la ventana de detección de REPORT (corrige A)
- [x] T2. Parser: `JOB_PATTERN = P2603-PR-PL-(?:SIM-)?\d+` e id derivado `SIM-0XX` desde los dígitos (corrige B)
- [x] T3. Parser: regex `Ratio\s*\(%\):` y `\(([\w-]+)\)` para casos (corrige C y D)
- [x] T4. Parser: secciones por tipo como lista; displacements/restraints → caso OPE (fallback: primero con datos); stresses → máximo de bending entre todos los casos (corrige E)
- [x] T5. Regenerar `dashboard/_data/lineas.json` y verificar las 7 líneas contra la tabla Verdad CAESAR (passed=true, ratio, nodo exactos)
- [x] T6. HTML: badge "SIN DATOS" (gris) cuando compliance esté vacío, en vez de FAILED (corrige F; defensivo)
- [x] T7. Imágenes: copiar isométricos a `dashboard/assets/iso/` (parser o workflow) y ajustar ruta en index/linea.html — hoy la ruta `carpeta/isometrico` es 404 porque las carpetas están fuera de `dashboard/`

## Riesgos / Puntos de verificación
- [x] Conteo PASSED en la web = 7/7; ratio máximo global = 85.7 % (SIM-007)
- [x] ratio/nodo de cada tarjeta == tabla Verdad CAESAR
- [x] `linea.html?id=SIM-003` e `id=SIM-007` resuelven (sin UNKNOWN)
- [x] No tocar los .md ni los .C2 (fuente CAESAR intacta)

## Revisión (2026-07-17)

Resumen de cambios:
- `scripts/parse_caesar_md.py` reescrito: normalización de saltos de línea (`newline=''` + reemplazo explícito), filtrado de líneas vacías en `split_into_sections`, secciones como listas por tipo, regex de job/ratio/caso corregidos, id `SIM-XXX` desde dígitos del job, merge de casos con datos (ope/sus/exp), stresses = máximo bending global, copia de isométricos y .md a `dashboard/assets/`.
- `dashboard/_data/lineas.json` regenerado: 7/7 PASSED, ratios y nodos idénticos a la tabla Verdad CAESAR (verificación automatizada OK).
- `dashboard/index.html`, `linea.html`, `tecnico.html`: badge "SIN DATOS" cuando `compliance.passed` no es booleano (ya no se pinta FAILED con datos faltantes); rutas de isométricos y descarga .md apuntan a `dashboard/assets/`.
- `dashboard/assets/css/styles.css` + `linea.html`: estilos `.linea-status.no-data` y `.status-badge.no-data`.

Desviaciones respecto al plan original:
- T7 incluyó también copiar los reportes .md a `dashboard/assets/md/` (el botón "Descargar Reporte Original" tenía el mismo problema de ruta 404 que las imágenes; además el nombre real `P2603-PR-PL-007 .md` contiene un espacio que rompía la reconstrucción del nombre en linea.html).

Limitaciones conocidas y trabajo futuro:
- `compliance.elements` sigue vacío (tabla por elemento no parseada; tecnico.html muestra "Datos no disponibles" en esa tabla).
- stresses.max_stress es el bending máximo entre todos los casos; en EXP puede superar el code stress de compliance (son magnitudes distintas, no un error).
- Pendiente: crear repo GitHub, habilitar Pages y probar CI/CD (bloqueado por cliente).

Archivos entregables:
- `scripts/parse_caesar_md.py`, `dashboard/_data/lineas.json`, `dashboard/index.html`, `dashboard/linea.html`, `dashboard/tecnico.html`, `dashboard/assets/css/styles.css`, `dashboard/assets/iso/` (7 isométricos), `dashboard/assets/md/` (7 reportes).

Verificación ejecutada:
- Script de chequeo: 7/7 líneas passed=True, ratio/nodo exactos vs .md → "VERIFICACION GLOBAL: OK".
- Servidor local (puerto 8123): las 3 páginas, el JSON, las 7 imágenes y los 7 .md responden HTTP 200.


---

# Tarea: Resultados gráficos CAESAR + logo DML (2026-07-17)

## Contexto
- Objetivo: incluir en el dashboard las imágenes `ResultadosGraficos<PCF>.png` exportadas de CAESAR (4 de 7 disponibles) y el logo DML (`logo1.png`)
- Disponibles: SIM-002 (103), SIM-003 (104), SIM-007 (107), SIM-011 (108). Pendientes: SIM-008, SIM-009, SIM-010 → espacio reservado

## Revisión

Resumen de cambios:
- `scripts/parse_caesar_md.py`: la detección de isométrico ahora excluye `ResultadosGraficos*` (riesgo real de confundirlo con el isométrico, glob `*.png` por orden no garantizado); copia gráficos → `dashboard/assets/graficos/SIM-XXX.png` y `logo1.png` → `dashboard/assets/logo.png`; nuevo campo JSON `resultados_graficos` (null si no existe la imagen).
- `dashboard/linea.html`: nueva sección "Resultados Gráficos — CAESAR II" (con lightbox); placeholder punteado "Espacio reservado…" cuando falta; la sección Chart.js se renombró a "Gráfica de Desplazamientos" para no duplicar títulos.
- `dashboard/index.html`, `linea.html`, `tecnico.html` + `styles.css`: logo DML en el header (`.logo-img`, alto 2.25 rem; el PNG tiene canal alfa → se ve bien en fondo oscuro).

Desviaciones: ninguna respecto a lo pedido.

Limitaciones / trabajo futuro:
- Faltan los gráficos de SIM-008, SIM-009, SIM-010: al agregarlos como `ResultadosGraficos*.png` en la carpeta de la línea y correr el parser, aparecen solos (el placeholder desaparece).

Verificación ejecutada:
- Parser regenerado: 7/7 PASSED con ratios/nodos intactos vs tabla Verdad CAESAR; isométricos siguen apuntando a PCF* (no a ResultadosGraficos).
- Servidor local (8123): index, linea.html?id=SIM-011, logo.png, graficos SIM-002/SIM-011 y lineas.json → HTTP 200.


---

# Tarea: Corrección PCF111 — SUCCION TK BLOWTANK (2026-09-02)

## Contexto
- Objetivo: corregir `SUCCION TK BLOWTANK/PCF111.pcf` (original Plant 3D 2027) con `fix_pcf.py` para que CAESAR II 2019 lo importe.
- Estado: PCF nuevo del equipo de dibujo, nunca corregido (sin backup `- ORIGINAL PLANT3D.pcf` previo). Isométrico `PCF111.png` ya disponible.

## Tareas
- [x] T1. Ejecutar `python fix_pcf.py "SUCCION TK BLOWTANK/PCF111.pcf"`
- [x] T2. Verificar stats del script y ausencia de AVISO (stub-ends sin pareja / bridas sin fusionar)
- [x] T3. Confirmar backup `PCF111 - ORIGINAL PLANT3D.pcf` creado

## Riesgos / Puntos de verificación
- [x] Ningún AVISO de fusión; si aparece, revisar el PCF manualmente antes de importar a CAESAR

## Revisión (2026-09-02)

Resumen de cambios:
- `SUCCION TK BLOWTANK/PCF111.pcf` corregido in-place (46 396 → 40 739 bytes); backup `PCF111 - ORIGINAL PLANT3D.pcf` creado por el script.

Estadísticas del script: end_position=4 eliminados, pairs=11 stub-ends fusionados con su brida, tap=1 eliminado; instr_dial/instr_zero/status/mlist/valve_code=0 (no aplicaban a este archivo).

Verificación ejecutada:
- `grep -c` sobre el PCF corregido: 0 END-POSITION, 0 LAPJOINT-STUBEND, 0 TAP-CONNECTION restantes.
- Sin mensajes AVISO (ningún stub-end sin pareja ni brida sin fusionar).
- Encabezado intacto (UNITS-BORE INCH, CO-ORDS MM, WEIGHT KGS).

Limitaciones conocidas:
- Pendiente importación en CAESAR II 2019 y corrida del análisis (fuera de alcance de esta tarea; lo ejecuta el usuario en CAESAR).

## Fuera de alcance (pasos posteriores, otra tarea)
- Importación en CAESAR II, corrida de análisis, generación del .md y agregado al dashboard (SIM-XXX por asignar)


---

# Tarea: Agregar SIM-012 SUCCION TK BLOWTANK al dashboard (2026-09-02)

## Contexto
- Objetivo: incorporar la 8ª línea (succión TK Blowtank, PCF111) al dashboard.
- Análisis CAESAR ya corrido: `PCF111 - copia.TXT` / `PCF111.OUT` con 37 secciones REPORT y `CODE COMPLIANCE EVALUATION PASSED`. Ratio visible 9.3 % @Node 260.
- Bloqueos: (1) no existe `.md` (parser solo busca `P2603-PR-PL-*.md`); (2) job name es `PCF111` y el parser exige `P2603-PR-PL-(SIM-)?\d+`.

## Supuestos clave
- [x] Nueva línea = SIM-012 (anteriores 002–011, sin conflictos)
- [x] `PCF111.OUT` (== `PCF111 - copia.TXT`, verificado con `cmp`) es el reporte completo y final del análisis

## Tareas
- [x] T1. Obtener `P2603-PR-PL-SIM-012.md` en la carpeta — ejecutada Opción B: copia binaria de `PCF111.OUT` con `Job Name: PCF111` → `P2603-PR-PL-SIM-012` (37 reemplazos)
- [x] T2. Ejecutar `python scripts/parse_caesar_md.py` (previo: soporte multi-gráfico + conversión tif→png de los 3 resultados gráficos)
- [x] T3. Verificar JSON: 8/8 PASSED; SIM-012 con ratio/nodo/caso idénticos al TXT; 7 líneas anteriores intactas vs tabla Verdad CAESAR
- [x] T4. Servir dashboard local y verificar index + linea.html?id=SIM-012 (isométrico PCF111.png + 3 gráficos)
- [x] T5. Actualizar `contexto.md` (tabla de resultados, líneas analizadas, estado)

## Riesgos / Puntos de verificación
- [x] Ratio/nodo SIM-012 == resumen global CODE COMPLIANCE del TXT: 32.4 % @Nodo 130, caso 8 (EXP) L8=L3-L6 (el 9.3 % @260 visto al inicio era de una sección parcial por caso, no del resumen global)
- [x] No tocar `PCF111 - ORIGINAL PLANT3D.pcf` ni archivos CAESAR fuente
- [x] Gráficos CAESAR presentes: los `pcf111-N.tif` ERAN los resultados gráficos (Code Stress by Percent); convertidos a `ResultadosGraficosPCF111-N.png`

## Revisión (2026-09-02)

Resumen de cambios:
- `SUCCION TK BLOWTANK/P2603-PR-PL-SIM-012.md` generado desde `PCF111.OUT` (reemplazo binario de Job Name, 37 ocurrencias; resultados numéricos intactos).
- `SUCCION TK BLOWTANK/ResultadosGraficosPCF111-{1,2,3}.png` convertidos desde los `.tif` RGBA de CAESAR (2248×982) con PIL.
- `scripts/parse_caesar_md.py`: soporte de múltiples `ResultadosGraficos*` por línea — `resultados_graficos` ahora es lista (o null); con un solo archivo conserva el nombre histórico `SIM-XXX.png`, con varios numera `SIM-XXX-N.png`.
- `dashboard/linea.html`: sección Resultados Gráficos renderiza galería (un `<img>` por elemento, lightbox vía `ImageUtils.openLightbox`); acepta lista o string legacy; placeholder sin cambios.
- `dashboard/_data/lineas.json` regenerado: 8/8 PASSED.

Resultado SIM-012 (verdad: resumen global del TXT): PASSED, ratio 32.4 % @Nodo 130, caso 8 (EXP) L8=L3-L6; Code Stress 92 844.5 kPa vs Allowable 286 952.5 kPa. Desplazamientos ope/sus/exp, 112 filas de restricciones, bending máx 91 345 kPa @130 (exp).

Desviaciones respecto al plan original:
- Se amplió a soporte multi-imagen en parser + linea.html porque el usuario pidió TODAS las imágenes de la carpeta y los .tif resultaron ser los resultados gráficos (3, no 1). Aprobado en la misma instrucción.

Limitaciones conocidas y trabajo futuro:
- Los 7 gráficos previos (SIM-002/003/007/011) conservan nombre `SIM-XXX.png`; sus JSON ahora llevan lista de un elemento — linea.html lo maneja.
- Siguen faltando `ResultadosGraficos*` de SIM-008, SIM-009, SIM-010 (placeholder).
- Pendiente commit + push del usuario para despliegue automático.

Verificación ejecutada:
- Script de chequeo: 7 líneas previas idénticas a tabla Verdad CAESAR; SIM-012 idéntico al resumen global del TXT (ratio 32.4, nodo 130, caso EXP).
- Servidor local (8124): index, linea.html?id=SIM-012, JSON, isométrico, 3 gráficos y .md de SIM-012 → HTTP 200.

## Pendiente del usuario (post-tarea)
- Commit + push para despliegue automático
- Exportar `ResultadosGraficos*.png` de SIM-008/009/010 cuando se pueda


---

# Plan: `generadorinf.md` — prompt maestro para informes LaTeX de flexibilidad (2026-09-02)

## Contexto
- Objetivo: convertir `PropmtGeneracionInformes.txt` (borrador de una idea, 7 líneas con errores de tipeo) en `generadorinf.md`: un prompt maestro autocontenido y reproducible que gobierne la generación de los informes LaTeX de análisis de flexibilidad, uno por línea, a partir de los reportes CAESAR II `.md`.
- Cliente / Proyecto DML: Smurfit Westrock — P2603 SW-K60
- Normas aplicables: ASME B31.3-2016 (análisis); estilo Elsevier/ScienceDirect y estándares de entregables de `AGENTS.md` (redacción)

## Hallazgos de la auditoría de insumos (hechos verificados)
1. **`Plantilla latex/` YA EXISTE y está completa** (actualizada por el usuario 2026-09-02): clase `elsarticle` A4 12pt, TG Termes, pdfLaTeX, UTF-8; 15 secciones modulares (`sections/00_hojafirmas.tex` … `13_anexos.tex`); datos del proyecto centralizados en `config/datos_proyecto.tex` (título, código doc, firmas, membrete); `compilar_informe.ps1` (doble pasada pdflatex → `build/<job>.pdf`); convenciones documentadas en `Plantilla latex/CLAUDE_plantilla.md` (tablas Elsevier `toprule/midrule/bottomrule`, `siunitx`, sin viñetas, figuras citadas antes de aparecer). `main.pdf`/`build/*.pdf` confirman que compila. Regla de la plantilla: NO editar `main.tex`, `preamble.tex`, `header.tex`; solo `datos_proyecto.tex`, `sections/`, `references/`, `assets/`.
2. **Datos por línea (8 líneas, todas PASSED)**:
   - `.md` CAESAR por línea: 9 casos de carga × (DISPLACEMENTS, RESTRAINTS, B31.3 STRESSES) + 1 CODE COMPLIANCE (resumen global). SIM-012 además RESTRAINTS EXTENDED. Casos: 2 OPE, 2 Alt-SUS, 2 SUS, 3 EXP.
   - `dashboard/_data/lineas.json`: compliance (ratio/nodo/caso/allowable), desplazamientos nodales ope/sus/exp (DX..RZ), cargas en restricciones con tipo de soporte, bending máximo.
   - Tablas de esfuerzos por elemento (SLP, F/A, Bending, Torsion, SIF, Code, Allowable, Ratio por nodo) SOLO están en los `.md`, no en el JSON → el generador debe parsear el `.md` directamente.
   - Imágenes: isométrico `PCF1XX.png` + resultados gráficos CAESAR (5/8 líneas; faltan 008/009/010).
3. **Toolchain disponible**: MiKTeX-pdfTeX 4.27 (compilación LaTeX OK), Python 3.14 + matplotlib 3.11 + PIL (figuras OK).
4. **Bases de diseño congeladas** (de `contexto.md`, no re-derivar): ASME B31.3-2016, TP 304L Sch 10S CA=0, 180 psig = 1241 kPa g, 90 °C (ΔT=65 °C), agua 0.001 kg/cm³, casos OPE/SUS/EXP.

## Decisiones requeridas del usuario (bloquean redacción final de generadorinf.md)
- ~~D1. Plantilla~~ **RESUELTA (2026-09-02)**: el usuario aportó la plantilla corporativa DML en `Plantilla latex/` — se usa tal cual, sin crear nada desde cero.
- D2. **Alcance del documento**: ¿un informe independiente por línea (8 PDF, lo que dice el prompt original) o un informe consolidado con un capítulo por línea?
- D3. **Arquitectura de generación**: ¿híbrida script+LLM (Python extrae tablas/figuras de los `.md` → el LLM redacta la prosa técnica en las `sections/` → `compilar_informe.ps1` compila) o generación íntegra por LLM en una sola pasada? (Recomendada: híbrida — los números no se alucinan, salen del `.md`.)

## Estructura propuesta de `generadorinf.md` (el entregable de esta tarea)

1. **Frontmatter de control**: versión, fecha, proyecto P2603 SW-K60, cliente, norma, líneas válidas (SIM-002…012), rutas de entrada/salida.
2. **Rol y alcance del generador**: qué produce (informe PDF por línea), qué NO produce (no recalcula CAESAR, no cambia bases de diseño congeladas).
3. **Insumos por línea (contrato de entrada)**: `.md` CAESAR (fuente de verdad numérica), isométrico, resultados gráficos (opcional con fallback), bases congeladas citadas de `contexto.md`.
4. **Estructura obligatoria del informe = archivos de la plantilla** (mapeo 1:1 con `Plantilla latex/sections/`; el prompt original pedía "resumen ejecutivo integrado" → la plantilla lo separa en abstract + resumen, se adopta la plantilla):
   - `00_portada.tex` + `00_hojafirmas.tex` — portada con control de revisiones y hoja de firmas (se alimentan de `datos_proyecto.tex`: código doc por línea, elaboró/revisó/aprobó)
   - `01_frontmatter.tex` — abstract (≤ 200 palabras: línea, código B31.3, PASSED/FAILED, ratio máximo, nodo y caso crítico) + keywords
   - `02_resumen.tex` — resumen ejecutivo (el informe ES un resumen: 1 página máx, síntesis de resultados y veredicto)
   - `03_nomenclatura.tex` — tabla de abreviaturas (CAESAR II, OPE/SUS/EXP/Alt-SUS, SIF, DDW, TK, SG, CA, Lb/plg²→kPa, etc.) + índices automáticos (`tableofcontents`, `listoftables`, `listoffigures` ya en `main.tex`)
   - `04_introduccion.tex` — marco teórico: qué es CAESAR II, FEM para tuberías, ecuaciones B31.3-2016 (esfuerzo sostenido SL, expansión SE con SIF i), criterio Code ≤ Allowable
   - `05_objetivos.tex` — general + específicos
   - `06_alcance.tex` — línea analizada, límites del modelo (anclas, equipos), exclusiones
   - `07_bases_disenio.tex` — tabla de condiciones (instalación 25 °C → operación 90 °C, 1241 kPa g, agua 0.001 kg/cm³), TP 304L Sch 10S CA=0, casos de carga con combinaciones (2 OPE, 2 Alt-SUS, 2 SUS, 3 EXP según el `.md` de cada línea)
   - `08_metodologia.tex` — flujo Plant 3D → PCF (`fix_pcf.py`) → CAESAR II 2019 → verificación
   - `09_resultados.tex` — (9.1) desplazamientos: tabla de máximos por caso + curvas DX/DY/DZ vs nodo (matplotlib desde JSON); (9.2) esfuerzos: tabla por nodo del caso crítico (desde `.md`) + curva esfuerzo vs nodo; (9.3) restricciones: tabla FX..MZ + tipo de soporte por nodo y caso; figuras: isométrico + resultados gráficos CAESAR
   - `10_analisis.tex` — code compliance: tabla de los N nodos de mayor ratio (cumple/no cumple) + discusión del caso crítico
   - `11_conclusiones.tex` + `12_recomendaciones.tex`
   - `references/bibliografia.bib` — ASME B31.3-2016, CAESAR II 2019 User Guide, ASME B16.5/B16.9
   - `13_anexos.tex` — tablas completas de esfuerzos/desplazamientos de todos los casos (lo que no quepa en resultados)
5. **Reglas de estilo** (de `AGENTS.md` + `Plantilla latex/CLAUDE_plantilla.md`, copiadas al prompt para autocontención): prohibido viñetas, tablas Elsevier `toprule/midrule/bottomrule` con leyenda arriba, figuras con leyenda debajo y citadas antes (`Figura~\ref{...}`), ecuaciones numeradas a la derecha con variables definidas después, `siunitx` con espacio valor-unidad (`25~\si{\celsius}`), voz impersonal, trazabilidad de todo número al `.md`, no editar `main.tex`/`preamble.tex`/`header.tex`.
6. **Mapeo dato → fuente** (tabla en el propio prompt): cada tabla/figura del informe ↔ sección exacta del `.md` o campo del JSON; regla de oro: el ratio/nodo/caso del informe == resumen global CODE COMPLIANCE del `.md` (no valores parciales por caso).
7. **Pipeline de ejecución** (si D3=híbrida): (1) copiar `Plantilla latex/` → `informes/SIM-0XX/`; (2) script Python extrae del `.md`/JSON las tablas (`.tex` Elsevier) y figuras (matplotlib PNG) → `informes/SIM-0XX/assets/`; (3) LLM redacta la prosa en `sections/` y llena `datos_proyecto.tex` (código doc `P2603-PR-INF-0XX`, título de la línea, firmas); (4) copiar isométrico/gráficos a `assets/`; (5) compilar con `compilar_informe.ps1 -jobName "P2603-PR-INF-0XX"`; (6) checklist de verificación.
8. **Lista de verificación final** (checklist que el generador debe cumplir antes de entregar): compila sin errores, números == `.md`, coherencia dimensional, sin viñetas, figuras citadas, abreviaturas usadas están en la tabla.
9. **Manejo de casos borde**: línea sin resultados gráficos (placeholder textual, no imagen falsa), nodos con "N/A" en restricciones, jobs sin "SIM" en nombre, espacio en "P2603-PR-PL-007 .md".

## Tareas
- [x] T1. Resolver D1–D3 — D1: plantilla aportada por el usuario en `Plantilla latex/`; D2: 8 informes independientes (usuario: "continua" → decisión por defecto del plan); D3: arquitectura híbrida script+LLM
- [x] T2. Redactar `generadorinf.md` (v1.0; `PropmtGeneracionInformes.txt` se conserva como referencia histórica)
- [x] T3. Revisión cruzada del prompt: script de verificación automatizado, 52/52 checks OK
- [x] T4. Actualizar `contexto.md` (nuevo componente generador de informes, sección 2b)

## Fuera de alcance de esta tarea (fase posterior, requiere su propio plan)
- Ejecutar el generador: scripts de extracción, redacción de las `sections/` por línea, generación de los informes PDF
- Dato pendiente del usuario para la ejecución: firmas (elaboró/revisó/aprobó) y fechas de emisión de los informes

## Riesgos / Puntos de verificación
- [x] El prompt no pide ningún dato que no exista en los `.md`/JSON (52 checks: tabla sección 1 == JSON == verdad CAESAR, campos JSON citados existen, 15 sections + comandos `datos_proyecto.tex` + `compilar_informe.ps1` existen, isométrico en las 8 carpetas, presencia/ausencia de ResultadosGraficos coincide con lo documentado)
- [x] El prompt cita las bases congeladas sin re-derivarlas (fuente única: `contexto.md`)
- [x] Compatibilidad con las 8 líneas incluyendo casos borde (hallazgo 2 y sección 9 del prompt)

## Revisión (2026-09-02)

Resumen de cambios:
- `generadorinf.md` creado (v1.0, 10 secciones): control de documento + tabla verdad CAESAR de las 8 líneas, rol/alcance del generador, contrato de insumos (.md como fuente de verdad, JSON de apoyo, imágenes, bases congeladas, plantilla), estructura del informe mapeada 1:1 a los 15 archivos `sections/` de la plantilla, reglas de estilo autocontenidas, mapeo dato→fuente, pipeline híbrido de 7 pasos, checklist de verificación, 8 casos borde documentados.
- Corrección en revisión: referencia B31.3 para SL era 304.3.5 → corregida a 302.3.5 (SE en 319.4.4, correcto).
- `contexto.md`: nueva sección 2b (generador de informes) y componente en archivos clave.

Desviaciones respecto al plan original:
- D2 y D3 se resolvieron por decisión por defecto del plan (usuario indicó "continua" sin elegir): D2 = informe por línea (lo que pedía el prompt original), D3 = híbrida (recomendada en el plan).

Limitaciones conocidas y trabajo futuro:
- La distribución de casos de carga (2 OPE, 2 Alt-SUS, 2 SUS, 3 EXP) se verificó solo en SIM-002; el prompt ordena extraerla del `.md` de cada línea, no asumirla.
- Ejecución del generador (scripts de extracción + redacción + compilación de 8 PDF) queda como tarea posterior con su propio plan en `task/todo.md`.
- Firmas y fechas de emisión pendientes de confirmación del usuario.

Archivos entregables:
- `generadorinf.md`, `task/todo.md`, `contexto.md` (actualizados).

Verificación ejecutada:
- Script de revisión cruzada: 52/52 checks OK (ver Riesgos arriba).


### Addendum a la Revisión de generadorinf.md (2026-09-02, v1.1)

El usuario actualizó `PropmtGeneracionInformes.txt` tras la primera lectura (ahora 3 ítems). Cambios incorporados a `generadorinf.md` v1.1:
- Ítem 3 (codificación): `\documentcode` = `I24.104-PP30-PP01-P-DOCS-18X`, consecutivo desde 180 en orden SIM (SIM-002→180 … SIM-012→187); reemplaza el `P2603-PR-INF-0XX` propuesto. Nombre del PDF y `-jobName` de compilación usan el mismo código.
- Ítem 1 (sin resumen ejecutivo): `02_resumen.tex` queda VACÍO (el informe ES el resumen ejecutivo); `main.tex` no se edita, por eso se conserva el archivo con solo comentarios.
- Ítem 1 (investigación web): nuevo paso 3 del pipeline — agentes de investigación en internet para introducción, objetivos y marco teórico; solo fuentes citables (normas, User Guide CAESAR, papers con DOI, NIST); registro en `bibliografia.bib`; se investiga una vez y se reutiliza en las 8 líneas.
- Checklist (sección 8): nuevo punto de verificación de código de documento y resumen vacío.
- Versión del prompt: 1.0 → 1.1. `contexto.md` actualizado.


---

# Plan: Ejecutar generador de informes — piloto SIM-012 (2026-09-02)

## Contexto
- Objetivo: generar el primer informe PDF de flexibilidad (`I24.104-PP30-PP01-P-DOCS-187`, SIM-012 Succión TK Blowtank) siguiendo `generadorinf.md` v1.1; el piloto valida el pipeline antes de replicar a las otras 7 líneas.
- Cliente / Proyecto DML: Smurfit Westrock — P2603 SW-K60
- Normas aplicables: ASME B31.3-2016
- Especificación: `generadorinf.md` (secciones 4–8); plantilla: `Plantilla latex/`; fuente numérica: `SUCCION TK BLOWTANK/P2603-PR-PL-SIM-012.md`

## Supuestos clave
- [x] `generadorinf.md` v1.1 es la especificación vigente (codificación DOCS-18X, sin resumen ejecutivo, investigación web)
- [ ] Firmas (elaboró/revisó/aprobó) no confirmadas → `datos_proyecto.tex` con `[POR CONFIRMAR]` en el piloto
- [x] La investigación teórica se hace una vez y se reutiliza en las 8 líneas (marco teórico común)

## Tareas
- [x] T1. `scripts/extraer_informe.py`: parsear `.md` (con normalización \r) + JSON → `informes/SIM-012/assets/`: tab_casos.tex, tab_esfuerzos_critico.tex, tab_top5_ratio.tex, tab_desplazamientos_max.tex, tab_restricciones_{ope,sus,exp}.tex (Elsevier, listas para \input), fig_desplazamientos.png, fig_esfuerzos.png (matplotlib 300 dpi), copia de isométrico PCF111.png y ResultadosGraficosPCF111-{1,2,3}.png
- [x] T2. Verificación de extracción: números de tablas/figuras == `.md` (ratio 32.4 % @130 EXP; code 92 844.5 kPa; allowable 286 952.5 kPa; casos del `.md`)
- [x] T3. Investigación web con agentes (una sola vez, reutilizable): CAESAR II y FEM para tuberías, ecuaciones B31.3 (SL 302.3.5, SE 319.4.4, SIF), criterio SA; solo fuentes citables → insumos para `04_introduccion.tex`, `05_objetivos.tex` y `bibliografia.bib`
- [x] T4. Copiar plantilla → `informes/SIM-012/` (sin build/ ni PDFs de prueba) y llenar `config/datos_proyecto.tex` (código I24.104-PP30-PP01-P-DOCS-187, membrete, firmas [POR CONFIRMAR])
- [x] T5. Redactar `sections/` (02_resumen.tex vacío; 09/10 con \input de tablas del paso T1; resto con prosa técnica + material de T3)
- [x] T6. Completar `references/bibliografia.bib` (ASME B31.3-2016, CAESAR II 2019 User Guide, B16.5/B16.9 + fuentes de T3) y citar en el texto
- [x] T7. Compilar: `compilar_informe.ps1 -jobName "I24.104-PP30-PP01-P-DOCS-187"` desde `informes/SIM-012/`; resolver errores hasta PDF limpio
- [x] T8. Checklist sección 8 de `generadorinf.md` (8/8 puntos) + lectura visual del PDF
- [x] T9. Actualizar `contexto.md` (estado informes) — rollout a las 7 líneas restantes queda como tarea posterior con aprobación

## Riesgos / Puntos de verificación
- [x] Ratio/nodo/caso del informe == resumen global del `.md` (32.4 % @130, caso 8 EXP L8=L3-L6) — no valores parciales por caso
- [x] Cero viñetas; tablas con \input de archivos generados (no transcritas)
- [x] `compilar_informe.ps1` es PowerShell: ejecutar desde Git Bash vía `powershell.exe -File` o compilar con pdflatex directo (doble pasada) si falla la invocación
- [x] Código I24.104-PP30-PP01-P-DOCS-187 en portada, membrete y nombre del PDF
- [x] No editar main.tex / preamble.tex / header.tex; no tocar los archivos CAESAR fuente


## Revisión — Ejecución generador piloto SIM-012 (2026-09-02)

Resumen de cambios:
- `scripts/extraer_informe.py` creado: parsea el `.md` CAESAR (tab-separated, con normalización \r y valores N/A) y genera 6 tablas Elsevier `.tex`, 2 figuras matplotlib (300 dpi), copia de isométrico/gráficos y `resumen_extraccion.json` en `informes/<SIM>/assets/`.
- `informes/SIM-012/` = plantilla DML + 15 secciones redactadas (02_resumen.tex vacío por instrucción del cliente) + `datos_proyecto.tex` (código I24.104-PP30-PP01-P-DOCS-187, firmas [POR CONFIRMAR]) + `bibliografia.bib` (10 fuentes verificadas por agente de investigación web).
- PDF compilado: `informes/SIM-012/I24.104-PP30-PP01-P-DOCS-187.pdf` (22 páginas A4, 0 referencias indefinidas).

Decisiones técnicas verificadas contra la salida de CAESAR:
- SE = √(Sb² + 4St²) SIN /2 (B31.3-2016 párr. 319.4.4 ec. 17): confirmado numéricamente — √(91345² + 4×7838.1²) ≈ 92 680 + axial ≈ 92 844.5 = Code de CAESAR @130.
- CAESAR usa la forma liberal SA = f[1.25(Sc+Sh) − SL] (ec. 1b): 1.25×(16.7+16.7) ksi − SL ≈ 41.6 ksi = 286 952.5 kPa = Allowable reportado → Sc = Sh = 16.7 ksi (115.1 MPa) para TP304L (Tabla A-1).
- SA está en 302.3.5(d) (no 302.3.4); SL en 302.3.5(c) evaluado por 320.2; f en Tabla 302.3.5 (1.0 hasta 7000 ciclos).

Desviaciones y correcciones durante la verificación:
- compilar_informe.ps1 NO ejecuta bibtex → compilación manual: pdflatex → bibtex (desde raíz del informe, NO desde build/) → pdflatex ×2. Documentado para el rollout.
- Tabla 6 (tubería): columnas `l` sin ajuste aplastaban la tabla → cambiadas a X raggedright.
- Error de prosa detectado en lectura visual: "desplazamientos < 0.2 mm en todos los casos" era FALSO (casos T2/EXP llegan a 3.8 mm en DY) → corregido en 09, 10 y 11.
- Error `\Bbbk already defined`: preexistente en la plantilla (aparece en sus propios logs), no fatal; preamble.tex no se edita por regla de la plantilla.

Limitaciones conocidas y trabajo futuro:
- Firmas/fechas/autor quedan [POR CONFIRMAR] — pendiente del usuario antes de emitir al cliente.
- B16.10 listado en tabla de normas sin entrada .bib (menor; B16.5/B16.9/A312 sí citados).
- Rollout a las 7 líneas restantes: mismo pipeline; extraer_informe.py --linea SIM-0XX + ajustar prosa de secciones por línea (narrativa de SIM-012 no es genérica).

Verificación ejecutada (checklist generadorinf sección 8, 9/9):
- Compila sin ?? ni undefined refs (0); ratio/nodo/caso == resumen global == tabla sección 1 (32.4 % @130 EXP L8=L3-L6); todas las tablas numéricas vía \input de archivos generados; cero viñetas; figuras citadas antes; siunitx; código de documento en portada/membrete/nombre PDF; 02_resumen vacío; PDF en build/ + raíz.
- Lectura visual de 16/22 páginas renderizadas (portada, firmas, abstract, nomenclatura, TOC, marco teórico, alcance, bases, metodología, resultados, análisis, conclusiones, anexos).

Archivos entregables:
- `informes/SIM-012/I24.104-PP30-PP01-P-DOCS-187.pdf` (+ `build/` con auxiliares)
- `scripts/extraer_informe.py`, `informes/SIM-012/{config,sections,references,assets}/`


### Addendum 2 — Correcciones de formato del membrete (2026-09-02, solicitud del usuario)

Cambios aplicados a `Plantilla latex/` (formato original) y sincronizados a `informes/SIM-012/`:
- Textos del membrete (datos_proyecto.tex del informe): filas 1-2 INGENIERIA DE DETALLE; filas 3-4 EUCALYPTUS PULP PRODUCTION OPTIMIZATION PROJECT; filas 5-6 ANALISIS DE FLEXIBILIDAD TK BLOWTANK; PROYECTO: P2603 (ya no "P2603 SW-K60").
- Firmas: ELABORÓ J.ARBOLEDA, REVISÓ F.NAVIA, APROBÓ H.ROSERO; autores del abstract: J. Arboleda (correspondiente), F. Navia, H. Rosero. Fechas de firma quedan [DD/MM/AAAA] (pendiente usuario).
- `logos/logo2.png` del informe era un duplicado del logo DML → reemplazado por el logo Smurfit Westrock de la plantilla (34 546 bytes). Lección para el rollout: verificar logo2 (Smurfit) ≠ logo1 (DML) tras copiar la plantilla.
- Rediseño de `\empresaheader` (header.tex): columnas 2.6/2.6/X/1.9/3.0 cm, tabcolsep 2pt, arraystretch 1.15; logos 2.6×2.9 cm keepaspectratio en multirow{5} (centrados); letra uniforme \scriptsize en todo el membrete (jerarquía solo por negrita); fila PROYECTO fusionada con \multicolumn{2} centrada.
- Fix estructural: `\setlength{\headheight}{112pt}` en header.tex — el membrete más alto se solapaba con el cuerpo en páginas interiores (warning fancyhdr 85→111 pt).
- Fix de contenido: \noindent en los tabularx sueltos de 03_nomenclatura.tex (el \parindent de 17.6 pt causaba overfull hbox) y \small en tab:planos de 13_anexos.tex.

Verificación: 0 undefined refs, 0 overfull, 0 warnings headheight; renders página 1 y página 8 (interior) sin solapes; línea "ANALISIS DE FLEXIBILIDAD TK BLOWTANK" cabe en una línea tras quitar negrita y ensanchar la columna central.


### Addendum 3 — Reversión del rediseño del membrete (2026-09-02)

El usuario evaluó el rediseño del Addendum 2 ("empeoró mucho") y ordenó volver a la versión anterior. Se revirtió `\empresaheader` al layout original (logos 2.3×2.5 cm, arraystretch 0.80, columnas 2.5/2.5/X/2/3, PROYECTO en celdas separadas, sin override de headheight), conservando del Addendum 2 solo los cambios aprobados: textos del membrete, firmas, autores del abstract y logo2=Smurfit. Lección: los cambios estéticos de layout se proponen con render previo y se espera aprobación explícita antes de aplicarlos al formato. PDF recompilado: 0 undefined, sin solapes (páginas 1 y 8 verificadas).


### Addendum 4 — Tamaño de letra del membrete (2026-09-02, solicitud del usuario)

- Quinta columna (valores) pasó a \small y luego, por observación del usuario, a \tiny: el código I24.104-PP30-PP01-P-DOCS-187 generaba segunda línea en la celda. Regla resultante: NINGUNA celda del membrete debe envolver a segunda línea.
- Ajustes finales: valores col. 5 en \tiny; línea inglesa "EUCALYPTUS PULP PRODUCTION OPTIMIZATION PROJECT" en \tiny (cabe en una línea); título \small bold y línea documento \scriptsize bold (caben en una línea). Aplicado en plantilla e informe, PDF recompilado (0 undefined).
- Warning benigno conocido del layout aprobado: overfull \vbox de 1.8 pt por página (invisible en el PDF; ya existía antes de estos cambios).

---

# Tarea: Rollout informes SIM-002…011 — corrección, compilación y verificación (2026-09-03)

## Contexto
- Objetivo: completar el rollout de los 7 informes restantes (DOCS-180…206) tras descubrir que el swarm de la sesión 2026-09-02 solo había hecho extracción + frontmatter; las secciones 03/04–13 estaban en placeholders de plantilla (SIM-009 era copia íntegra de SIM-012 con job, nodo y ratio erróneos).
- Especificación: `generadorinf.md` v1.1; patrón de redacción: piloto `informes/SIM-012/`.
- Ejecución: swarm de 7 agentes (uno por línea) + consolidación y actualización de memoria por el agente principal.

## Revisión (2026-09-03)

Resumen de cambios:
- Redactadas las secciones faltantes de las 7 líneas con datos reales de cada `.md`/PCF (03_nomenclatura de SIM-002/008/010 tenían nomenclatura de otro dominio; 07–13 eran plantilla cruda; SIM-009 reescrita por completo).
- Defectos del briefing corregidos: SIM-010 `\documentcode` placeholder → DOCS-185 y `datos_proyecto.tex` completo; SIM-008 y SIM-010 `02_resumen.tex` → versión solo-comentarios; `assets/tab_esfuerzos_critico.tex` de SIM-011 convertido a longtable (156 filas, regenerado con `extraer_informe.py` tras incidente de regex, verificado idéntico).
- Compilación manual (pdflatex → bibtex → pdflatex ×2) de los 7 informes; PDF en raíz de cada `informes/SIM-0XX/` y en `build/`.
- Memoria actualizada: `contexto.md`, `boveda/` (resumen de líneas, pendientes, log de sesiones).

Verificación ejecutada (por línea, checklist de generadorinf sección 8):
- 8/8 PDF compilados: DOCS-180 (23 pág.), 201 (21), 202 (22), 203 (20), 204 (22), 205 (23), 206 (25), 207 (22, piloto previo).
- 0 referencias/citas indefinidas en los logs finales; único error benigno preexistente: `\Bbbk already defined`.
- Ratio/nodo/caso de cada informe == resumen global CODE COMPLIANCE de su `.md` (28.8 % @78 SUS; 13.1 % @120 Alt-SUS; 85.7 % @100 EXP; 12.2 % @200 Alt-SUS; 20.8 % @60 Alt-SUS; 60.9 % @310 SUS; 56.1 % @260 Alt-SUS). Cero discrepancias numéricas.
- Cero viñetas; figuras citadas antes de aparecer; lectura visual de páginas clave sin solapes en las 7 líneas.

Desviaciones respecto al plan original:
- El alcance creció de "corregir 3 defectos + compilar" a "redactar la mayoría de las secciones" porque el estado real del trabajo previo era mucho menor al documentado. Aprobado implícitamente por la instrucción "ejecuta el próximo paso".

Limitaciones conocidas y trabajo futuro:
- **Inconsistencia de admisibles pendiente de verificación**: SIM-002/003/008/009/010/011 reportan Allowable SUS 137895.1 kPa (Sc=Sh=20.0 ksi en sus informes); el piloto SIM-012 afirma Sc=Sh=16.7 ksi (su allowable EXP 286952.5 kPa es consistente con 16.7). Revisar la frase del marco teórico de SIM-012 antes de emitir al cliente.
- Pie "CI-ESP-001_R0" hardcodeado en `header.tex` (intocable por regla de plantilla), preexistente.
- SIM-003: extremos del tramo modelados con desplazamientos impuestos (5.0 mm), no anclas — descrito así en su informe.
- Placeholders heredados en las 8 líneas: fechas de firma [DD/MM/AAAA] y `\ead{[correo@dmlsas.com]}`.
- Pendiente del usuario: gráficos SIM-008/009/010, fechas de firma, validación cliente, commit + push.

Archivos entregables:
- `informes/SIM-002…SIM-011/I24.104-PP30-PP01-P-DOCS-20X.pdf` (7 PDF nuevos) + `sections/`, `config/`, `references/` redactados.

---

# Tarea: Verificación de admisibles + renombrado de carpetas y .C2 (2026-09-03, tarde)

## Contexto
- Origen: pendiente del backlog "verificar inconsistencia de admisibles Sc=Sh" + instrucciones de orden del usuario.
- Resultado verificación: 6 modelos (SIM-002/003/007/009/010/011) corridos en CAESAR con admisible TP304 (20.0 ksi = 137895.1 kPa); SIM-008/012 correctos con TP304L (16.7 ksi = 115142.4 kPa). Los 8 PCF declaran A312 TP304L / A403 WP304L en toda tubería y accesorio BW (el "304 sin L" solo aparece en sockolets/bridas forjadas, elementos rígidos que no gobiernan el admisible). Recalculado con 16.7 ksi (SA = 1.25(Sc+Sh) − SL, f=1): SIM-002 34.4/28.0 %, SIM-003 15.7/~0 %, SIM-009 25.0/~0 %, SIM-010 73.0/58.6 %, SIM-011 67.2/37.7 % (SUS/EXP) — PASSED; SIM-007 EXP 279365.7/268976 = **103.9 % → FAILED**. Decisión del usuario pendiente.

## Renombrados ejecutados
- Carpetas de simulación: prefijo `1.0`–`8.0` en orden SIM (parser usa glob `*/patrón` → sin rutas fijas; verificado: JSON regenerado idéntico, 8/8).
- .C2 → `P2603-PR-SIM-XXX.C2` (sin "-PL"; 003/007 normalizados con "SIM"; SIM-010 excluida por instrucción y no tiene .C2; PCF111.C2 → P2603-PR-SIM-012.C2). .md/.tif/.wrn intactos por decisión del usuario.
- OJO: el campo `nombre` del JSON ahora incluye el prefijo de carpeta ("1.0 DESCARGA…") — pendiente decidir si se muestra así en el dashboard o se limpia en el parser.

## Trabajo futuro derivado
- Esperar decisión sobre admisibles y los .OUT recorridos → regenerar .md, parser, dashboard, informes (SIM-007 pasaría a FAILED).
- Job Name interno de CAESAR sigue siendo el viejo en cada modelo (SIM-012 = PCF111); cambiarlo dentro de CAESAR si se quieren .OUT con nombre nuevo.
- Instrucción registrada: hoja de firmas de informes = única excepción al formato de tablas (bordes completos); no tocarla.

---

# Tarea: SIM-002 recorrida con TP304L + rejilla completa en portada/firmas (2026-09-03, cierre)

## Pipeline ejecutado (repetir para cada línea recorrida)
1. Usuario entrega `.OUT` nuevo en la carpeta N.N (Job Name ya renombrado `P2603-PR-SIM-XXX` dentro de CAESAR).
2. Verificar admisible SUS = 115142.4 kPa en el .OUT.
3. `cp .OUT → P2603-PR-SIM-XXX.md`; mover el .md viejo a `_corrida_anterior_TP304/`.
4. `python scripts/parse_caesar_md.py` → verificar JSON contra .OUT (ratio/nodo/caso/admisible).
5. `python scripts/extraer_informe.py --linea SIM-XXX` → regenera tablas/figuras del informe.
6. Actualizar secciones: job name (sed `P2603-PR-PL-…` → `P2603-PR-…`), fecha de análisis, ratios, admisibles, frase Sc=Sh=16.7 ksi en 04_introduccion, conclusiones; incorporar imágenes nuevas si las hay.
7. Compilar: pdflatex → bibtex → pdflatex ×2 → copiar PDF a la raíz del informe. Verificar 0 refs indefinidas + lectura visual.

## Resultado SIM-002
- PASSED 34.5 % @78 SUS (antes 28.8 % con TP304); admisible 115142.4 kPa; EXP 28.0 % @90 (admisible 254505.3). Esfuerzos/desplazamientos idénticos a la corrida anterior (solo cambió el admisible).
- DOCS-180 recompilado: 23 pág., 0 refs indefinidas; figuras nuevas Fig. 2 (NodosSoporte) y Fig. 5 (mapa Code Stress by Value — el `Dezplazamiento.tif` exportado por el usuario NO es de desplazamientos y trae la leyenda cortada; se le pidió re-exportar si quiere corregirla).
- Scripts modificados: `parse_caesar_md.py` y `extraer_informe.py` (regex `P2603-PR-(PL-)?(SIM-)?`; isométrico prefiere `PCF*`).

## Rejilla completa en portada y hoja de firmas (regla del usuario)
- Únicas dos páginas con tablas de rejilla completa (`{|...|}` + `\hline` por fila + `\rowcolor{green!15}` en encabezados). **COMPLETADO 2026-09-04**: aplicado en los 8 informes + `Plantilla latex/` (los 7 restantes tenían archivos idénticos parametrizados → copia desde SIM-002; 7 PDF recompilados, 0 refs indefinidas, verificación visual SIM-011/012).

---

# Tarea: Renumeración DOCS-18X + membrete 9pt con código en una línea (2026-09-04)

## Cambios ejecutados
- **Membrete uniforme**: `\headerfont` = `\fontsize{9}{10}` en TODO el texto del membrete (antes mezclaba 11/8/5pt); jerarquía solo por negrita. Layout final: logos 2.2 cm (img 2.0×2.2), X central, etiquetas `m{2.1cm}`, **valores `m{4.5cm}`** (el código `I24.104-PP30-PP01-P-DOCS-18X` queda en UNA línea — pedido explícito), arraystretch 0.90. Propagado por copia a las 9 copias de `config/header.tex` (md5 único).
- **Renumeración de informes**: DOCS-20X → DOCS-18X, mismo orden SIM (SIM-002→180 … SIM-012→187). Editados `\documentcode` (datos_proyecto.tex) y código citado en `06_alcance.tex` de los 8; recompilados con jobname nuevo; PDF viejos DOCS-20X eliminados (en `build/` quedan logs viejos inofensivos). Referencias actualizadas en bóveda, `contexto.md`, `task/todo.md`, `generadorinf.md`.
- **Corrección reportada al usuario**: `\headerlinesubdos` de SIM-010 → "ANALISIS DE FLEXIBILIDAD SUCCION RECIRCULACION 3 DDW" (era "SUCCION BOMBAS DE RECIRCULACION DDW", inconsistente y desbordaba).
- Verificación de los 8 PDF tras cada cambio: 0 refs indefinidas, 0 overfull vbox, mismas páginas (23/21/22/20/22/23/25/22), renders visuales OK.

## Lecciones (membrete)
- Interlineado ≈ tamaño+1pt + arraystretch 0.90 → una celda de 2 líneas ≈ 2 filas de multirow (sin traslapes).
- babel-spanish pone `\uchyph=0`: textos en MAYÚSCULAS no se hyphenan; wraps solo en espacios/guiones.
- A 9pt el código de 28 car. necesita ~42 mm → columna de valores 4.5 cm; si el código cambia de formato, re-verificar.

## Pendiente al cierre (2026-09-04)
- Recorridas CAESAR restantes con TP304L: SIM-003, SIM-007 (saldrá FAILED ~103.9 % EXP → redactar hallazgo; dejar de última), SIM-009, SIM-010, SIM-011. Ratios esperados (estimado ×1.198): 003 ~15.7 %, 009 ~24.9 %, 010 ~72.9 %, 011 ~67.2 %. Pipeline de arriba (pasos 1-7) por cada .OUT entregado.
- Usuario: gráficos SIM-008/009/010, fechas de firma [DD/MM/AAAA], validación cliente.
- Commit + push de todo lo acumulado (renombrados, SIM-002 TP304L, scripts, membrete, renumeración DOCS-18X, rejilla ×8 + plantilla).

---

# Tarea: Informe SIM-013 Descarga tanque de nivelación (2026-09-08) — FASE 1: PLAN (esperando aprobación)

## Datos verificados del .md (fuente de verdad)
- Job: `P2603-PR-SIM-013` (corrida 2026-09-08, ya con admisible TP304L 115142.4 kPa ✓)
- **CODE COMPLIANCE EVALUATION PASSED**: ratio 24.3 % @Nodo 100, LOADCASE 2 (Alt-SUS) W+P2, Code 27937.0 kPa
- Casos vistos: 2 (Alt-SUS) W+P2, 4 (Alt-SUS) W+P2, 5 (SUS) W, 6 (SUS) W+P2, 7/8/9 (EXP) — ratios EXP ~0 %. Extraer tabla de casos del .md.
- Warnings CAESAR (a declarar en el informe): reductor 130→140 sin espesor 2 ni ángulo alpha → defaults 3.759 mm / 22.617°.
- Imágenes disponibles: isométrico `PCF113.png` ✓; `NodosSoporte.tif` y `Dezplazamiento.tif` → convertir a PNG (PIL) y VERIFICAR VISUALMENTE (trampa conocida: el "Dezplazamiento.tif" puede ser mapa Code Stress, como en SIM-002).

## Pipeline (generadorinf.md v1.1, sección 7)
1. `python scripts/parse_caesar_md.py` → verificar que SIM-013 entra al JSON (9 líneas) con ratio/nodo/caso idénticos al .md.
2. Copiar `Plantilla latex/` → `informes/SIM-013/` (sin build/ ni PDFs).
3. `python scripts/extraer_informe.py --linea SIM-013` → tablas .tex + figuras matplotlib + imágenes en `informes/SIM-013/assets/`.
4. Redactar sections/ reutilizando el marco teórico ya investigado (común a los 8 informes; adaptar de un informe de descarga, p. ej. SIM-011); `02_resumen.tex` vacío.
5. `config/datos_proyecto.tex`: código `I24.104-PP30-PP01-P-DOCS-188`, título "ANALISIS DE FLEXIBILIDAD DESCARGA TANQUE DE NIVELACION", firmas J.ARBOLEDA/F.NAVIA/H.ROSERO, fechas [DD/MM/AAAA].
6. Compilar: pdflatex → bibtex → pdflatex ×2 → copiar PDF a `informes/SIM-013/`.
7. Checklist sección 8 de generadorinf.md (0 ??, números == .md, sin viñetas, verificación visual con renders).

## Decisiones pendientes del usuario
- Aprobar código DOCS-188 para SIM-013.
- ¿Incluir actualización del dashboard (JSON 9 líneas) en esta tarea o dejarla para el commit+push acumulado?

## Revisión (SIM-013 DOCS-188, 2026-09-08)

- Resumen: informe `informes/SIM-013/I24.104-PP30-PP01-P-DOCS-188.pdf` compilado (22 pág., 0 refs indefinidas); plantilla copiada sin build/PDFs; assets por `extraer_informe.py --linea SIM-013` sin ajustes al script; prosa adaptada de SIM-002; tifs convertidos a PNG con PIL.
- Verificación: ratio/nodo/caso del informe == .md (24.3 % @100, caso 2 Alt-SUS W+P2, Code 27937.0 / Allowable 115142.4 kPa); renders visuales OK (portada, firmas, isométrico, tabla de esfuerzos).
- Desviaciones del plan: ninguna de alcance; salvedades declaradas en el informe (desplazamientos OPE/SUS no tabulables por salida N/A y desbordamiento de formato; "Dezplazamiento.tif" es mapa Code Stress; warnings del reductor 130→140; material default de la importación PCF).
- Limitaciones / trabajo futuro: SIM-013 aún NO está en el dashboard (parser diferido por decisión del usuario); fechas de firma [DD/MM/AAAA] pendientes; recomendado habilitar reporte de cargas en extremos (nodos 10/160) en CAESAR.
- Entregable: `informes/SIM-013/I24.104-PP30-PP01-P-DOCS-188.pdf` (+ `build/` con la misma compilación).
- Nota de proceso: primera tarea ejecutada con la excepción de fase 1 de `AGENTS.md` (pipeline maestro `generadorinf.md` ya aprobado).

## Revisión — complemento (2026-09-08, limpieza de lenguaje cliente en DOCS-188)

- Tras feedback del usuario: eliminados de DOCS-188 los textos con jerga interna (nombre de archivo en caption Fig. 5; "salida deshabilitada"/"N/A"/"desbordamiento de formato" en §6.1 y §7; "material por defecto del archivo de mapeo" en §3). Barrido de los 9 informes: solo SIM-013 afectado. Recompilado: 22 pág., 0 refs indefinidas, verificación visual OK.
- Regla registrada en bóveda (log 2026-09-08): en documentos cliente no van nombres de archivos internos ni salvedades de herramienta.

---

# Tarea: Auditoría de corridas TP304L + procesamiento SIM-003 (2026-09-08, tarde)

## Contexto
- El usuario perdió la noción de qué líneas estaban recorridas con TP304L. Se barrió el admisible (115142.4 = TP304L vs 137895.1 = TP304) en todos los .md/.OUT del proyecto.

## Hallazgos de la auditoría (verificados en archivos)
- SIM-003: `.OUT` TP304L existía desde 2026-09-04 sin procesar (el .md seguía siendo el viejo TP304).
- SIM-007: `.OUT` nuevo (2026-09-04) INCOMPLETO — solo DISPLACEMENTS + RESTRAINTS, sin B31.3 STRESSES ni CODE COMPLIANCE → usuario debe re-exportar con reporte completo.
- SIM-014 (10.0 TMS, PASSED 55.9 % @70 SUS) y SIM-015 (11.0 filtro fibras PP1, PASSED 36.3 % @80 Alt-SUS): corridas nuevas del 2026-09-08 con .md/.C2/imágenes, sin procesar (parser + informes DOCS-189/190 pendientes).
- Sin recorrer: SIM-009, SIM-010, SIM-011. Sin corrida: PCF116 (12.0), PCF115 (13.0).

## Pipeline SIM-003 ejecutado
1. `P2603-PR-SIM-003.OUT` → `P2603-PR-SIM-003.md`; viejo `P2603-PR-PL-003.md` archivado en `_corrida_anterior_TP304/`.
2. `extraer_informe.py --linea SIM-003` — PASSED 15.7 % @N120 caso 4 (Alt-SUS) W+P2, Code 18089.2 / Allowable 115142.4 kPa, 9 casos, 22 nodos; overflow de desplazamientos en casos 2 y 4 (excluidos por el script, nota neutral en la prosa).
3. Secciones de `informes/SIM-003/` actualizadas (job name, ratios 13.1→15.7 %, admisibles 137895.1→115142.4 kPa, Sc=Sh=16.7 ksi, fecha de análisis 04/09/2026, márgenes 87→84 %).
4. DOCS-181 recompilado: 21 pág., 0 refs indefinidas, bibtex limpio, verificación visual OK (abstract, tabla del caso crítico).

## Revisión
- Resumen: auditoría completa + SIM-003 actualizada de punta a punta. Verdad nueva idéntica a la estimada (15.7 % vs ~15.7 % estimado).
- Desviaciones: ninguna; parser/dashboard diferido por decisión del usuario (se hará con SIM-014/015).
- Limitaciones: SIM-007 requiere re-exportación del usuario; SIM-009/010/011 pendientes de corrida.
- Entregables: `2.0 .../P2603-PR-SIM-003.md`, `informes/SIM-003/I24.104-PP30-PP01-P-DOCS-181.pdf`.

---

# Plan: Actualización TP304L de informes y dashboard con gráficas nuevas, 11 líneas (2026-09-09)

## Contexto
- Objetivo: actualizar los 9 informes (DOCS-180→188) con las corridas TP304L del 2026-09-09 y las gráficas nuevas de `Graficas/`; generar DOCS-189 (SIM-014) y DOCS-190 (SIM-015); actualizar dashboard a 11 líneas.
- Normas: ASME B31.3-2016; pipeline `generadorinf.md` v1.1 (excepción fase 1).
- Estado: plan redactado en modo plan (2 revisiones con el usuario), **pendiente de aprobación**. Próxima sesión arranca **revisando la carpeta 6.0 (SIM-010)**.

## Supuestos clave
- [ ] Los `.md` del 2026-09-09 son la fuente de verdad (11 líneas TP304L, todas PASSED; ratios en `boveda/20-Lineas/Resumen de líneas.md`).
- [ ] Semántica de gráficas (instrucción del usuario): DesplazamientoN→§9.1 (tabla desplaz. máx); StressPercentN→§9.2 (tabla esfuerzos crítico); NodosSoporteN→§9.3 (tabla restricciones/soportes); AnexoResultado→anexos (**EN ESPERA de instrucciones, no procesar**).
- [ ] Pares 1/2 de gráficas NO son duplicados (md5 distinto): usar todas las vistas.

## Tareas
- [x] T0. Higiene: renombrar `1.0 .../P2603-PR-SIM-002 .md` (espacio) — lo hizo el usuario; validada la conversión del tif de 400 KB de 5.0 (LZW, vista recortada, convierte OK); artefactos SIM-015 en carpeta 10.0 registrados (`.c2db`/`.XML`/`-x.wrn`, inofensivos).
- [x] T1. Herramientas: `scripts/convertir_graficas.py` (tif→png, PIL, fondo blanco, excluye AnexoResultado; 45 PNG); `extraer_informe.py` (lee `Graficas/`, excluye `_corrida_anterior*/`, assets `graf_desplazamiento[_N]`/`graf_stress_percent[_N]`/`graf_nodos_soporte[_N]`); `parse_caesar_md.py` (excluye `_corrida_anterior`, `resultados_graficos` desde `Graficas/`, isométrico también desde `Graficas/PCF*`).
- [x] T2. Verificación numérica por línea: JSON 11/11 contra tabla verdad (ratio/nodo/caso/admisible). SIM-007 y SIM-011 tenían material TP304 residual → el usuario las recorrió (2026-09-10): SIM-007 70.1 % @100 EXP c.9, SIM-011 67.2 % @260 Alt-SUS, SIM-010 46.7 % @430 EXP; 0×137895.1 en los 11 .md.
- [x] T3. Informes: 9 actualizados (DOCS-180→188) + 2 nuevos (DOCS-189 SIM-014, DOCS-190 SIM-015 con tramo Sch 40S declarado); 11 PDF recompilados (pdflatex→bibtex→pdflatex×2), 0 refs indefinidas + verificación visual (swarm de 11 agentes). Páginas: 23/22/23/23/22/27/28/24/22/24/28.
- [x] T4. Dashboard: parser → `lineas.json` 11 líneas + assets; verificación 11/11 contra tabla verdad; 0 referencias rotas.
- [x] T5. Memoria + reporte final (2026-09-10); commit+push PENDIENTE (solo con confirmación explícita).

## Revisión (ejecución del plan, 2026-09-10)

- Resumen: plan ejecutado completo con swarm (1 agente T1 + 11 agentes T3). 11 informes compilados y verificados; dashboard con 11 líneas; todas las corridas limpias con TP304L.
- Desviaciones respecto al plan original: (1) el renombrado del .md con espacio lo hizo el usuario antes de T0; (2) antes de T3 se detectó y corrigió material TP304 residual en SIM-007/011 (el plan solo contemplaba "verificar") — el usuario recorrió ambas + SIM-010, lo que cambió los números de SIM-007 (85.8→70.1 %) y SIM-011 (56.1→67.2 %) y resolvió el 96.8 % de SIM-010 (→46.7 %); (3) `tab_esfuerzos_critico.tex` de SIM-010/011/012/015 convertida a `longtable` a mano (el script no lo emite; pendiente automatizar).
- Limitaciones conocidas / trabajo futuro: tifs de SIM-007 en `Graficas/` son de la corrida vieja (usuario re-exporta); huérfanos sin referencia en `dashboard/assets/graficos/` (4 PNG) y en `informes/*/assets/` (figuras viejas); tabla de job names de `generadorinf.md` desactualizada (`P2603-PR-PL-SIM-XXX`); warning benigno `\Bbbk already defined` en todos los builds.
- Entregables: `informes/SIM-0XX/I24.104-PP30-PP01-P-DOCS-18X.pdf` (11, códigos 180→190); `dashboard/_data/lineas.json` + `dashboard/assets/graficos/SIM-0XX-N.png`; `scripts/convertir_graficas.py`; `scripts/parse_caesar_md.py` y `scripts/extraer_informe.py` actualizados.

## Riesgos / puntos de verificación
- [ ] `.md` con espacio en 1.0 → doble parseo si no se renombra antes.
- [ ] SIM-007 con un caso a 20 ksi: si persiste, el informe no puede declarar "todo TP304L" sin salvedad.
- [ ] SIM-010 96.8 %: revisión cruzada vs corrida anterior (60.9 % SUS @310).
- [ ] Tif de 12–18 MB: conversión razonable para LaTeX y web (300 dpi).
- [ ] Coherencia de unidades (kPa, mm) en tablas regeneradas.

---

# Plan: Ordenamiento de archivos y carpetas del proyecto (2026-09-11)

## Contexto
- Objetivo: dar orden al proyecto — prefijos de dos dígitos en carpetas de línea (01.0–09.0), raíz sin archivos sueltos (`fix_pcf.py`→`scripts/`, `logo1.png`→`assets/`), artefactos SIM-015 de 10.0→11.0, `.gitignore` con scratch CAESAR, triggers del workflow robustos (`**/P2603-PR-*.md`), eliminar `.tmp-playwright/`.
- Restricciones verificadas: globs de un nivel en los 3 scripts (agnósticos al prefijo); informes .tex no referencian carpetas de línea; no se toca ningún `.md`/`.OUT`/`.C2`/`.pcf`/`.dwg` ni `Graficas/`; scratch CAESAR solo se excluye de git, no se mueve del disco.
- Plan detallado en archivo de sesión; aprobado (modo auto).

## Tareas
- [x] T1. Renombrar `1.0`→`01.0` … `9.0`→`09.0` (mv directo; cambios aún sin commitear).
- [x] T2. Mover `P2603-PR-SIM-015.c2db/.XML/-x.wrn` de 10.0 → 11.0.
- [x] T3. `fix_pcf.py`→`scripts/`; `logo1.png`→`assets/logo1.png` + ajuste `parse_caesar_md.py` (copy_logo lee `assets/logo1.png`).
- [x] T4. Eliminar `.tmp-playwright/` + gitignore.
- [x] T5. `.gitignore`: CONTROLU, OCONTROLU, DBGENBIN, COMNDINP, TEMPMAT*, *.c2db, *.XML.
- [x] T6. Workflow: `'**/P2603-PR-*.md'` + `'**/Graficas/**'`.
- [x] T7. Referencias vivas: `contexto.md`, `boveda/20-Lineas/Resumen de líneas.md` (columna Carpeta 01.0–13.0), `boveda/40-Workflows/Comandos y pipelines.md`, `boveda/60-Pendientes/Pendientes y bloqueos.md` (carpeta 03.0).
- [x] T8. Verificación: parser → contenido por línea idéntico; convertir_graficas idempotente; git status coherente; Revisión abajo.

## Riesgos
- [ ] No commitear sin confirmación explícita (queda acumulado con TP304L).
- [x] OneDrive puede tardar con los renombrados; verificar que los mv completen → los 9 mv completaron sin error.

## Revisión (2026-09-11)

- Resumen: reorganización ejecutada completa (T1–T8). Carpetas de línea 01.0–13.0 ordenan alfabéticamente; raíz sin scripts/assets sueltos; scratch CAESAR fuera de git; workflow con triggers agnósticos al prefijo.
- Verificación: (a) parser regeneró `lineas.json` — comparación por `id` de línea: contenido IDÉNTICO en las 11 líneas (solo cambian `nombre`/`carpeta` por el prefijo y el orden de la lista, que mejora: queda en orden SIM-002→015); (b) `convertir_graficas.py` idempotente: 0 conversiones, 45 al día; (c) `git check-ignore` confirma CONTROLU/DBGENBIN/c2db/XML/TEMPMAT* ignorados y `git add -n` no incluiría scratch; (d) `git status`: 82 ?? (carpetas nuevas), 67 D (nombres viejos rastreados), 9 M — coherente con el renombrado acumulado sin commitear.
- Desviaciones respecto al plan: ninguna.
- Limitaciones / trabajo futuro: commit pendiente (acumula TP304L + reorganización — requiere confirmación explícita del usuario); notas históricas del log de sesiones conservan nombres de carpeta de su época (decisión deliberada).
- Archivos tocados: 9 carpetas renombradas; `scripts/fix_pcf.py` (movido), `assets/logo1.png` (movido), `scripts/parse_caesar_md.py`, `.gitignore`, `.github/workflows/update-dashboard.yml`, `contexto.md`, `task/todo.md`, `boveda/20-Lineas/Resumen de líneas.md`, `boveda/40-Workflows/Comandos y pipelines.md`, `boveda/60-Pendientes/Pendientes y bloqueos.md`; 3 archivos SIM-015 movidos a 11.0; `.tmp-playwright/` eliminado.

---

# Plan: Rescate de componentes en coordenada basura — PCF120 (carpeta 15.0)

## Contexto
- Objetivo: dejar `15.0 DESCARGA BOMBA PP30BT17/PCF120.pcf` importable en CAESAR II 2019 recuperando los 57 bloques que Plant 3D exportó en la coordenada centinela (-9776646, -9840066, -102887) con bore 0.0000. Se reconstruye lo recuperable desde el hardware de unión vecino en coordenadas reales (24 bridas LJ + 11 válvulas) y se elimina documentando lo irrecuperable (18 soportes + 3 bloques SUPPORT vacíos; 2 sockolets + 2 codos 45° SW solo si no se ubican).
- Cliente / Proyecto DML: Smurfit Westrock — P2603 SW-K60
- Normas aplicables: ASME B31.3-2016 (análisis posterior); ASME B16.5 / B16.9 / B16.10 para la geometría de las uniones reconstruidas.

## Hallazgos base (investigación 2026-09-23, sesión anterior)
- La coordenada basura es centinela de Plant 3D para componentes sin geometría resuelta; ya venía en el original (99 ocurrencias). NO es defecto de `fix_pcf.py`.
- 57 bloques afectados; 39 son el primer componente de su sección `PIPELINE-REFERENCE` (44 de 58 secciones afectadas).
- Los 24 stub-ends sin pareja y las 24 bridas LJ basura son las MISMAS uniones lap-joint: stub-end + gasket + pernos están en coordenadas reales (verificado por coincidencia de caras, ej. línea 11456 ↔ 1381); solo la brida perdió su geometría. En el original los stub-ends tampoco traen sufijo LAP ni bore (0.0000), por eso `merge_stubend` no pudo emparejarlos y los degradó a PIPE.
- Bores: recuperables del tubo real que comparte nodo con el componente (ej. stub-end bore 0.0 ↔ tubo vecino bore 6.0 en el mismo nodo).
- `fix_pcf.py` NO se modifica; el rescate es un script one-off nuevo.

## Hallazgos T1 (2026-09-23) — refinamiento que INVALIDA dos pautas anteriores
- **Gaskets y pernos duplicados 58×**: 1336 gaskets (25 únicos) y 1162 pernos (22 únicos); cada posición única aparece en las 58 secciones. La pauta "hardware al final de la sección anterior" era FALSA (era la duplicación). PCF118 sano NO la tiene (45/45). Limpieza opcional propuesta.
- **Emparejamiento de stub-ends (determinista)**: 11 pares colineales enfrentados con bore concordante en AMBOS lados de cada par + stub que une con la knife gate REAL PMVAL1-102 + 1 boquilla de equipo (0.76, 0.12, 0.66 = descarga bomba). FF = gap − 2×3.175 mm.
- **Asignación por FF y bore**: knife 3" (FF 50.96, idéntico a la real) → PMVAL1-084; V-port 3" (FF 165.1) → I30RF01K01-V1; MAGNETIC FLOW METER 4" (FF 248.0, bore 4") → INSTRUMENT sin geometría que `fix_pcf.py` eliminó (TAG FIT-I30BT09F01-F1, recuperable); check 3" ×2 (FF 73.0) y check 6" (FF 98.4); butterfly 3" ×3 (FF 42.0/46.9), 4" (52.0), 6" (57.3). TAGs de butterflies y checks a confirmar por el usuario con el isométrico.
- **Ramal 2"**: huecos reales verificados (sin componente que los puentee): bola THD 2" en hueco de 91.8 mm; 2× ELL 45 SW en huecos de 46.9 mm; sockolet 1 en el arranque del ramal sobre el riser 6" (centro (0.76, 0.12, 586.44), BRANCH1 (-74.45, -75.09, 586.44), 106.4 mm = radio 6" + altura olet ✓). Sockolet 2 y artefacto 1" (0.76, -528.48, 5356.57, con 58 WELD duplicados) → MANUAL con isométrico.
- **Donantes brida LJ**: 24 con pesos 4.08/5.44/8.16 kg (3"/4"/6") + outliers "9" y "18" (corruptos); catálogo MATERIALS tiene 3 códigos LJ (12517/12521/12525) — mapear por bore, no por donante.

## Supuestos clave
- [x] S1. (INVALIDADO en T1) La pauta "hardware al final de la sección anterior" era la duplicación 58× de gaskets/pernos; se reemplazó por emparejamiento determinista de stub-ends (colineales, enfrentados, bore concordante).
- [x] S2. Bore de cada componente reconstruido tomado del tubo real que comparte su nodo (verificado en las 24 uniones: bore concordante en ambos lados de cada par).
- [ ] S3. Los soportes (18, incl. 3 vacíos) no son reconstruibles desde el PCF: se eliminan y se entrega lista (sección, tipo) para reposición manual en CAESAR II. (usuario confirmó en la aprobación del plan)
- [ ] S4. Sockolet 1, bola THD y 2 codos 45 SW: ubicación inequívoca → reconstruir. Sockolet 2 y artefacto 1" → MANUAL (eliminar del PCF y reportar).

## Tareas
- [x] T1. Script de análisis read-only `scripts/fix_pcf120_basura.py --proponer` ejecutado: 11 pares de stub-ends + 1 unión con knife real + 1 boquilla equipo; asignación tipo↔unión por FF/bore; ramal 2" con 4 huecos reales + sockolet; 18 soportes; conteo de duplicados (gasket 1336→25, bolt 1162→22, weld 148→91).
- [x] T2. CHECKPOINT usuario (2026-09-22): aprobado con criterio "geometría y diámetros correctos; TAGs y detalles los ajusta el usuario en CAESAR II". Decisiones delegadas al agente: asignación por tamaño en orden de documento, dedupe 58×, sockolet 2 eliminado + reportado.
- [x] T3. Parche aplicado (2026-09-22): respaldo `PCF120 - ANTES RESCATE.pcf`. 24 stub-ends → FLANGE LJ C/W STUB-END (SKEY FLWN, código 12517/12521/12525 y peso por bore, attr2 SCHClass_150); 24 bridas basura eliminadas; 10 válvulas bridadas reubicadas (EPs = cara LAP + 3.175 mm, sufijo FL); MAGNETIC FLOW METER 4" recuperado como INSTRUMENT (TAG FIT-I30BT09F01-F1); bola THD 2" en hueco 91.8; 2× ELL 45 SW en huecos 46.9 (CENTRE-POINT = intersección de tangentes, ANGLE corregido 9000→4500); sockolet 1 en riser 6" (2º eliminado); 18 soportes eliminados (lista en `PCF120 - SOPORTES ELIMINADOS.txt`); dedupe 2508 bloques GASKET/BOLT/WELD. Archivo 1.13 MB → 126 KB. Probado primero en copia.
- [x] T4. Verificación post-parche OK: 0 coordenadas basura; conteos FLANGE=24, VALVE=12, INSTRUMENT=1, ELBOW=30, OLET=1, SUPPORT=11, GASKET=25, BOLT=22, WELD=91; 0 nodos con bore incoherente; 24 FLWN con bore>0; 5 extremos sueltos = extremos de línea preexistentes (idénticos en el respaldo pre-parche).
- [x] T5. Registro completado (2026-09-22): tabla verdad 15.0, pendientes, log de sesiones y sección Revisión aquí. El usuario importa en CAESAR II como prueba final.

## Riesgos / Puntos de verificación
- [x] Bores concordantes en los 11 pares (3"/4"/6" verificados en ambos lados de cada par en T1).
- [x] Knife gate: 2 en el archivo (real línea 12450 = PMVAL1-102; basura línea 19735 = PMVAL1-084) — son válvulas distintas; la basura va a la unión con FF idéntico (50.96 mm) al de la real.
- [x] Asignación TAG↔unión de butterflies (5) y checks (3): el usuario la ajusta en CAESAR II (decisión T2) — la geometría y el bore de cada unión son los correctos independientemente del TAG.
- [x] Pesos de brida: 2 donantes con peso corrupto ("9" y "18") — se usó el peso por bore (4.082/5.443/8.165 kg); salvedad registrada.
- [x] Soportes eliminados = restricciones que el modelo CAESAR no tendrá: el usuario los repone manualmente (lista en `PCF120 - SOPORTES ELIMINADOS.txt`).
- [x] ELL 45 SW: PCF usa CENTRE-POINT = intersección de tangentes (verificado contra el ELL 90 SW real), NO centro de arco; ANGLE corregido a 4500.
- [ ] Validación final de importación en CAESAR II 2019 la hace el usuario (el agente no tiene CAESAR).

## Revisión (2026-09-22)

- Resumen: rescate completo de PCF120 (15.0). La exportación Plant 3D tenía 57 bloques en coordenada centinela y gaskets/pernos/welds duplicados 58×. Se reconstruyó toda la geometría desde los 24 stub-ends reales (11 pares gemelos enfrentados + unión con knife real + boquilla de equipo), se recuperaron 11 válvulas/instrumento, el ramal de 2" completo, y se eliminaron 18 soportes irrecuperables + 2508 bloques duplicados.
- Verificación: 5/5 chequeos automáticos OK (0 basura, conteos, 0 bores incoherentes, 24 FLWN, sueltos = preexistentes). Inspección visual de bloques reescritos (FLANGE/VALVE/INSTRUMENT/ELBOW/OLET) conforme al formato PCF de los bloques reales.
- Desviaciones respecto al plan: (1) la pauta "hardware al final de la sección anterior" resultó ser la duplicación 58× — se reemplazó por emparejamiento determinista de stub-ends (más robusto); (2) se descubrió el MAGNETIC FLOW METER 4" (fix_pcf lo había eliminado por no tener END-POINTs) y se recuperó; (3) dedupe de gaskets/pernos/welds aprobado por el usuario en T2 (no estaba en el plan original como acción segura).
- Limitaciones / trabajo futuro: TAGs de las 5 butterflies y 3 checks asignados por tamaño en orden de documento — el usuario los confirma en CAESAR II; sockolet 2 y artefacto 1" (0.76, -528.48, 5356.57) quedaron fuera (revisar en Plant 3D/isométrico); 18 soportes por reponer manualmente (lista entregada); validación de importación en CAESAR pendiente (usuario).
- Archivos entregables: `15.0 DESCARGA BOMBA PP30BT17/PCF120.pcf` (rescatado), `.../PCF120 - ANTES RESCATE.pcf` (respaldo), `.../PCF120 - SOPORTES ELIMINADOS.txt` (lista), `scripts/fix_pcf120_basura.py` (--proponer/--aplicar/--verificar).
