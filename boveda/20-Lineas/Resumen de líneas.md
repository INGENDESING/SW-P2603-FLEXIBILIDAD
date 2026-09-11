# Resumen de líneas — tabla verdad CAESAR

Fuente de verdad: los `.md` de CAESAR en cada carpeta de línea. Tras regenerar el JSON del dashboard, comparar SIEMPRE contra esta tabla.

**Corridas nuevas TP304L (2026-09-09)**: las 11 líneas tienen `.md`/`OUT` nuevos `P2603-PR-SIM-XXX.md` y carpetas `Graficas/` (Desplazamiento/NodosSoporte/StressPercent + AnexoResultado EN ESPERA). Los informes y el dashboard AÚN tienen los datos anteriores — actualización pendiente (plan en `task/todo.md`).

| Carpeta | Línea | Nombre | PCF | Resultado .md (corrida TP304L 2026-09-09) | Ratio máx | Nodo | Caso crítico | Gráficos | Informe |
|---|---|---|---|---|---|---|---|---|---|
| 01.0 | [[SIM-002]] | Descarga recirculación 1 DDW | PCF103 | P2603-PR-SIM-002.md (OJO: archivo con espacio `...002 .md`, renombrar en Fase 0) | 34.5 % | 78 | 6 (SUS) W+P2 | SÍ (Graficas: Desp1, Nodos1, Stress1) | DOCS-180 (pendiente actualizar) |
| 02.0 | [[SIM-003]] | Descarga recirculación 2 DDW | PCF104 | P2603-PR-SIM-003.md | 15.7 % | 120 | 4 (Alt-SUS) W+P2 | SÍ (Desp1, Nodos1/2, Stress1) | DOCS-181 (pendiente actualizar) |
| 03.0 | [[SIM-007]] | Línea bomba vacío nueva | PCF107 | P2603-PR-SIM-007.md (**recorrida 2026-09-10 14:42, material corregido**) | 70.1 % | 100 | 9 (EXP) L9=L1-L3 | SÍ (Desp1, Nodos1, Stress1) ⚠️ tifs del 09-09 = corrida VIEJA (85.8 %, TP304) → re-exportar | DOCS-182 (pendiente actualizar). Admisibles TP304L ✓ (0×137895.1; EXP 273789.8 = 287856 − SL). Histórico: 85.8 % @100 caso 8 con admisible EXP base TP304 |
| 04.0 | [[SIM-008]] | Succión recirculación 1 DDW | PCF106 | P2603-PR-SIM-008.md | 22.5 % | 90 | 4 (Alt-SUS) W+P2 | SÍ (Desp1, Nodos1, Stress1) | DOCS-183 (pendiente actualizar) |
| 05.0 | [[SIM-009]] | Succión recirculación 2 DDW | PCF105 | P2603-PR-SIM-009.md | 26.4 % | 60 | 2 (Alt-SUS) W+P2 | SÍ (Desp1, Nodos1, Stress1) | DOCS-184 (pendiente actualizar) |
| 06.0 | [[SIM-010]] | Succión recirculación 3 DDW | 10.pcf | P2603-PR-SIM-010.md (**recorrida 2026-09-10 09:03**, .C2 09:13) | 46.7 % | 430 | 8 (EXP) L8=L3-L6 | SÍ (2× cada tipo + PCF102.jpeg) | DOCS-185 (pendiente actualizar). Histórico 2026-09-09: 96.8 % @40 EXP — la recorrida del usuario lo resolvió; admisibles TP304L ✓ |
| 07.0 | [[SIM-011]] | Descarga bomba PP30BT03 | PCF108 | P2603-PR-SIM-011.md (**recorrida 2026-09-10 15:12, material corregido**) | 67.2 % | 260 | 4 (Alt-SUS) W+P2 | SÍ (2× cada tipo; tifs del 09-09 siguen VÁLIDOS: los esfuerzos no cambiaron, solo el admisible) | DOCS-186 (pendiente actualizar). Admisibles TP304L ✓ (0×137895.1; EXP 257442.5). Histórico: 56.1 % con admisible TP304 |
| 08.0 | [[SIM-012]] | Succión TK Blowtank | PCF111 | P2603-PR-SIM-012.md | 34.8 % | 130 | 8 (EXP) L8=L3-L6 | SÍ (2× cada tipo) | DOCS-187 (pendiente actualizar) |
| 09.0 | [[SIM-013]] | Descarga tanque de nivelación | PCF113 | P2603-PR-SIM-013.md | 24.3 % | 100 | 2 (Alt-SUS) W+P2 | SÍ (Desp1, Nodos1, Stress1) | DOCS-188 (pendiente actualizar) |
| 10.0 | SIM-014 | Descarga TMS | PCF112 | P2603-PR-SIM-014.md | 55.9 % | 70 | 6 (SUS) W+P2 | SÍ (Desp1, Nodos1, Stress1) | **DOCS-189 por generar** |
| 11.0 | SIM-015 | Tubería filtro de fibras PP1 | PCF114 | P2603-PR-SIM-015.md | 36.3 % | 80 | 2 (Alt-SUS) W+P2 | SÍ (Desp1, Nodos1/2, Stress1/2) | **DOCS-190 por generar** ⚠️ PCF114 trae tramo Sch 40S |
| 12.0 | SIM-016 | Succión bomba PP30SR03 | PCF116 | **Sin corrida** (tiene `P2603-PR-SIM-016.C2`) | — | — | — | NO | — |
| 13.0 | — | Succión bomba PP30BT17 | PCF115 | **Sin corrida** (sin .C2) | — | — | — | NO | — |

## Condiciones de operación (levantamiento 2026-09-08, sobre corridas ANTERIORES)

⚠️ Esta tabla se derivó de los .md viejos; **repetir la verificación sobre los .md del 2026-09-09 al procesarlos** (los .C2 nuevos ya están en cada carpeta).

Los `.md` de CAESAR NO traen input echo con T/P explícitas (son solo reportes de salida). Presión derivada del esfuerzo longitudinal SLP impreso (P = 4·SLP/(OD/t), convergencia ±2 % en 5 diámetros); temperatura de las bases de diseño (común a las 8). **No repetir este análisis: la tabla es la referencia.**

| Línea | T operación | P crítica (P2) en modelo | P1 en modelo |
|---|---|---|---|
| SIM-002 | 90 °C | ≈1034 kPa (~150 psi) | ≈95 kPa |
| SIM-003 | 90 °C | ≈1034 kPa (~150 psi) | ≈95 kPa |
| SIM-007 | 90 °C | ≈1044 kPa (~151 psi) | ≈96 kPa |
| SIM-008 | 90 °C | ≈1034–1061 kPa | ≈95–97 kPa |
| SIM-009 | 90 °C | ≈1044 kPa (~151 psi) | ≈96 kPa |
| SIM-010 | 90 °C | ≈1034 kPa (~150 psi) | ≈94 kPa |
| SIM-011 | 90 °C | ≈1054 kPa (~153 psi) | ≈97 kPa |
| SIM-012 | 90 °C | **0** (gravedad, sin SLP) | 0 |

- Valor único crítico del proyecto: T = 90 °C; P ≈ 1034 kPa ≈ 150 psi (caso gobernante SUS W+P2).
- ⚠️ **Discrepancia**: bases de diseño e informes declaran 1241 kPa g (180 psig), pero los modelos se corrieron con ~150 psi → verificar en los .C2 (pendiente).
- No hay presión de prueba hidrostática en ningún modelo ni informe.

## Notas

- **Recorrida TP304L COMPLETA (2026-09-10)**: las 11 líneas tienen corridas con admisible TP304L (115142.4 kPa), 0 ocurrencias de 137895.1 en ningún .md. Resueltas hoy: **SIM-010** (09:03, 46.7 % @430 EXP — resuelve el 96.8 % del 09-09), **SIM-007** (14:42, 70.1 % @100 EXP caso 9 — resuelve el EXP con admisible base TP304; OJO: sus tifs de `Graficas/` son de la corrida vieja, los esfuerzos SÍ cambiaron → re-exportar) y **SIM-011** (15:12, 67.2 % @260 Alt-SUS — sus tifs siguen válidos: solo cambió el admisible, los esfuerzos son idénticos). Las corridas viejas TP304 quedaron en `_corrida_anterior_TP304/`.
- Ratio máximo global del proyecto: **70.1 % (SIM-007, EXP @100)**; segunda más exigida: SIM-011 (67.2 % Alt-SUS @260).
- Semántica de `Graficas/` (instrucción del usuario 2026-09-09): DesplazamientoN→§9.1 (tabla desplaz. máx); StressPercentN→§9.2 (tabla esfuerzos caso crítico); NodosSoporteN→§9.3 (tabla restricciones/soportes); AnexoResultado→anexos (**EN ESPERA**). Pares 1/2 verificados por md5: son vistas distintas, usar todas.
- Casos borde del parser: `P2603-PR-SIM-002 .md` (01.0) aún tiene espacio antes de la extensión (renombrar en Fase 0 — resueltos los de SIM-014 y los `.md` viejos PL-*). Regex vigente acepta `P2603-PR-(PL-)?(SIM-)?\d+`; isométrico prefiere archivos `PCF*`.
- Gráficas: tif de 12–18 MB (RGBA) → conversión a PNG con PIL pendiente (script `scripts/convertir_graficas.py` del plan); el `Desplazamiento1.tif` de 05.0 pesa solo 400 KB (formato distinto — validar en conversión).
- Codificación de informes: DOCS-180→190 en orden SIM; nombre del PDF = código.
