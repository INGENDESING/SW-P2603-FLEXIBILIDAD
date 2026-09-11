# Pendientes y bloqueos

Estado al 2026-09-10. Marcar `[x]` al completar y registrar en [[50-Sesiones/Log de sesiones]].

## Esperan al usuario

- [ ] **Commit + push de cambios pendientes** (despliegue automático del dashboard con las 11 líneas TP304L).
- [ ] **Re-exportar los 3 tifs de SIM-007 (carpeta 03.0)**: los de `Graficas/` son de la corrida vieja TP304 (los esfuerzos cambiaron al corregir el material). Luego `python scripts/convertir_graficas.py --force` + re-ejecutar parser y `extraer_informe.py --linea SIM-007` + recompilar DOCS-182 (OJO: `tab_esfuerzos_critico.tex` requiere conversión manual a longtable solo en 010/011/012/015 — SIM-007 no).
- [ ] **AnexoResultado: EN ESPERA de instrucciones** — no procesar ni incluir ningún `AnexoResultado.png` en informes/dashboard hasta que el usuario lo indique.
- [ ] Corridas de SIM-016 (12.0, ya tiene `P2603-PR-SIM-016.C2`) y PCF115 (13.0) en CAESAR.
- [ ] Fechas de firma de informes en `datos_proyecto.tex` de las 11 líneas: `\fechaElaboro` = **01/09/2026 YA APLICADA** (2026-09-10, 11 informes + plantilla recompilados); pendientes `\fechaReviso` y `\fechaAprobo` ([DD/MM/AAAA] — documento pendiente de revisión y aprobación; `\fechaRevCero` también queda pendiente porque la emisión R0 es posterior a la aprobación). También placeholder `\ead{[correo@dmlsas.com]}` en frontmatter.
- [ ] Validación con el cliente (Smurfit Westrock) — sitio desplegado pero con datos viejos hasta el commit+push.

- [ ] **Verificar presión real de los modelos en los .C2 (discrepancia 2026-09-08)**: los informes/bases declaran P máx = 1241 kPa g (180 psig), pero el SLP de los .md indica P2 ≈ 150 psi (≈1034 kPa); SIM-012 sin presión (gravedad). OJO: repetir la verificación sobre los .md del 2026-09-09/10 (la tabla de P/T se derivó de los .md viejos).

## Trabajo del agente (con aprobación)

- [ ] Mejora de `scripts/extraer_informe.py`: emitir `longtable` automáticamente cuando `tab_esfuerzos_critico.tex` supere ~50 filas (hoy se convierte a mano en SIM-010/011/012/015 y se pierde al re-ejecutar).
- [ ] Limpieza opcional: huérfanos en `dashboard/assets/graficos/` (`SIM-002.png`, `SIM-003.png`, `SIM-007.png`, `SIM-011.png`, sin referencia en el JSON) y assets viejos sin referencia en `informes/*/assets/` (`NodosSoporte.png`, `Dezplazamiento.png`, `ResultadosGraficos*`).
- [ ] Alinear la tabla de job names de `generadorinf.md` (aún dice `P2603-PR-PL-SIM-XXX`; los jobs reales son `P2603-PR-SIM-XXX`).
- [ ] B16.10 figura en tabla de normas del piloto sin entrada .bib (menor)

## Completado recientemente

- [x] **Plan TP304L ejecutado completo (2026-09-10)**: T0–T5. 9 informes actualizados + DOCS-189/190 nuevos (11 PDF, 0 refs indefinidas, números == .md, verificación visual OK); dashboard `lineas.json` 11 líneas verificado contra tabla verdad (0 refs rotas); `convertir_graficas.py` nuevo + parsers actualizados. Detalle en [[50-Sesiones/Log de sesiones]] y `task/todo.md`.
- [x] **Recorridas con material corregido (2026-09-10)**: SIM-010 (09:03, 46.7 % @430 EXP), SIM-007 (14:42, 70.1 % @100 EXP — resuelve el admisible EXP base TP304), SIM-011 (15:12, 67.2 % @260 Alt-SUS). 11/11 líneas TP304L limpias (0×137895.1), todas PASSED.
- [x] Recorridas TP304L de las 11 líneas entregadas y verificadas (2026-09-09): 2 revisiones de inconsistencias; el usuario corrigió manualmente (StressPercent SIM-003/015, Desplazamiento1 de 2.0/5.0, typo 7.0, `Grafica/`→`Graficas/` 11.0, .md viejos eliminados, SIM-014 sin espacio). Pares 1/2 de gráficas NO son duplicados (md5 distinto — vistas diferentes). Detalle y ratios en [[50-Sesiones/Log de sesiones]] y [[20-Lineas/Resumen de líneas]].

## Completado recientemente

- [x] Recorridas TP304L de las 11 líneas entregadas y verificadas (2026-09-09): 2 revisiones de inconsistencias; el usuario corrigió manualmente (StressPercent SIM-003/015, Desplazamiento1 de 2.0/5.0, typo 7.0, `Grafica/`→`Graficas/` 11.0, .md viejos eliminados, SIM-014 sin espacio). Pares 1/2 de gráficas NO son duplicados (md5 distinto — vistas diferentes). Detalle y ratios en [[50-Sesiones/Log de sesiones]] y [[20-Lineas/Resumen de líneas]].

## Completado recientemente

- [x] Auditoría de corridas TP304L + SIM-003 procesada (2026-09-08): SIM-003 tenía .OUT TP304L desde 09-04 sin procesar → `P2603-PR-SIM-003.md` nuevo, viejo archivado, DOCS-181 recompilado (PASSED 15.7 % @120). Descubiertas: SIM-014 (TMS, 55.9 %) y SIM-015 (filtro fibras, 36.3 %) corridas sin procesar; SIM-007 con .OUT incompleto (re-exportar); solo faltan recorrer SIM-009/010/011
- [x] PCF114, PCF116 y PCF115 corregidos con `fix_pcf.py` (2026-09-08): respaldos `PCF11X - ORIGINAL PLANT3D.pcf`, sin avisos, material TP304L verificado (OJO: PCF114 trae un tramo Sch 40S)
- [x] Informe SIM-013 (Descarga tanque de nivelación) DOCS-188 compilado (2026-09-08): 22 pág., 0 refs indefinidas, PASSED 24.3 % @100 (Alt-SUS) W+P2, admisible TP304L ✓. Peculiaridades en [[20-Lineas/SIM-013]]. Migración `CLAUDE.md` → `AGENTS.md` el mismo día (10 referencias actualizadas en 7 archivos; `CLAUDE_plantilla.md` de la plantilla no se tocó)

- [x] PCF113 y PCF112 corregidos con `fix_pcf.py` (2026-09-07): respaldos `PCF11X - ORIGINAL PLANT3D.pcf`, sin advertencias; listos para importar en CAESAR II 2019
- [x] Rejilla completa en portada y hoja de firmas propagada a los 7 informes restantes + `Plantilla latex/` (2026-09-04): los 7 compartían el mismo `00_portada.tex`/`00_hojafirmas.tex` (md5 idéntico, todo parametrizado con macros) → bastó copiar las versiones de SIM-002. 7 PDF recompilados (0 refs indefinidas, mismas páginas), verificación visual en SIM-011 y SIM-012. También (mismo día): renumeración DOCS-20X→18X y membrete con código en una línea (columna valores 4.5 cm)
- [x] Membrete uniformado a 9pt en los 8 informes + plantilla (2026-09-04): `\headerfont` = `\fontsize{9}{10}` en todo el membrete, jerarquía solo por negrita, columnas ajustadas (logos 2.2 cm, etiquetas `m{2.1cm}`, valores `m{3.1cm}`), arraystretch 0.90. 8 PDF recompilados (0 refs indefinidas, mismas páginas). Incluye corrección de `\headerlinesubdos` de SIM-010 → "SUCCION RECIRCULACION 3 DDW" (reportada al usuario)
- [x] SIM-002 recorrida con TP304L y actualizada de punta a punta (2026-09-03): nuevo `P2603-PR-SIM-002.OUT/.md` (PASSED 34.5 % @78 SUS, admisible 115142.4 kPa), .md viejo archivado en `_corrida_anterior_TP304/`, parser + `extraer_informe.py` actualizados (regex acepta `P2603-PR-(PL-)?(SIM-)?`; isométrico prefiere `PCF*`), dashboard JSON regenerado, informe DOCS-180 recompilado (23 pág., 0 refs indefinidas) con figuras nuevas `NodosSoporte.png` (nodos/soportes) y `Dezplazamiento.png` (OJO: el tif exportado es en realidad mapa "Code Stress by Value" con leyenda cortada — se incluyó como mapa de esfuerzo, Fig. 5)
- [x] Verificación de admisibles Sc/Sh (2026-09-03): hallazgo documentado arriba; 6 modelos con TP304, 2 correctos; impacto calculado línea por línea
- [x] Renombrado de carpetas de simulación: prefijo `1.0`–`8.0` en orden SIM (parser usa glob, verificado OK, JSON idéntico) (2026-09-03)
- [x] Renombrado de .C2 a `P2603-PR-SIM-XXX.C2` (sin "-PL"); 003/007 normalizados con "SIM"; SIM-010 excluida (no tiene .C2); PCF111.C2 → P2603-PR-SIM-012.C2 (2026-09-03)
- [x] SIM-012 agregada y desplegada (2026-09-02, commit `db8d3dc`) — 8/8 PASSED en producción
- [x] Informe piloto SIM-012: `informes/SIM-012/I24.104-PP30-PP01-P-DOCS-187.pdf` (22 pág., checklist 9/9)
- [x] `generadorinf.md` v1.1 (codificación DOCS-18X, sin resumen ejecutivo, investigación web)
- [x] Membrete: reversión al layout original + textos/firmas/logo2 aprobados (Addenda 2-4, 2026-09-02)
