# Plan: Corrección parser CAESAR II → dashboard (auditoría 2026-07-17)

## Contexto
- Objetivo: El dashboard muestra 6 de 7 líneas como "FAILED" y ratio 0.0 % en la única "PASSED". CAESAR II arrojó **CODE COMPLIANCE EVALUATION PASSED en las 7 líneas**. El error está en `scripts/parse_caesar_md.py` y en el render que trata "sin datos" como "FAILED".
- Cliente / Proyecto DML: Cartón Colombia — P2603 SW-K60
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
