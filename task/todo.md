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
