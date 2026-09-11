# Contexto P2603 SW-K60

Análisis de flexibilidad de tuberías para **Smurfit Westrock**, proyecto P2603 SW-K60 (Eucalyptus Pulp Production Optimization Project). Consultora: DML Ingenieros Consultores.

## Flujo de trabajo

Isométricos desde AutoCAD Plant 3D 2027 → PCF → corrección con `fix_pcf.py` → CAESAR II 2019 → reporte `.md` → parser `scripts/parse_caesar_md.py` → dashboard web + informes LaTeX.

## Componentes

1. **Dashboard web** (`dashboard/`) — visualización para cliente e interno DML. Estático (HTML + JSON), sin backend. En vivo: https://ingendesing.github.io/SW-P2603-FLEXIBILIDAD/ (8/8 PASSED). Repo: https://github.com/INGENDESING/SW-P2603-FLEXIBILIDAD (público; Pages en privado exige Pro).
2. **Generador de informes LaTeX** — `generadorinf.md` (prompt maestro v1.1) + `Plantilla latex/` (corporativa DML, elsarticle). 8 informes independientes, códigos `I24.104-PP30-PP01-P-DOCS-18X` (180→187 en orden SIM). Piloto SIM-012 ya generado.
3. **Corrección PCF** — `fix_pcf.py` (6 transformaciones Plant 3D 2027 → CAESAR II 2019).

## Estado global (2026-09-02)

- 8/8 líneas analizadas, todas **PASSED** (ver [[20-Lineas/Resumen de líneas]]).
- Dashboard desplegado y verificado en producción.
- Informe piloto SIM-012 compilado: `informes/SIM-012/I24.104-PP30-PP01-P-DOCS-187.pdf` (22 pág.).
- Próximo paso: rollout de informes SIM-002…011 y gráficos CAESAR de SIM-008/009/010 (ver [[60-Pendientes/Pendientes y bloqueos]]).

## Herramientas del entorno

- CAESAR II 2019 (Ver.11.00.00.4800), AutoCAD Plant 3D 2027
- MiKTeX-pdfTeX 4.27, Python 3.14 + matplotlib + PIL
- Git Bash en Windows; `compilar_informe.ps1` se invoca vía `powershell.exe -File` (y NO ejecuta bibtex: usar secuencia manual documentada en [[40-Workflows/Comandos y pipelines]])
