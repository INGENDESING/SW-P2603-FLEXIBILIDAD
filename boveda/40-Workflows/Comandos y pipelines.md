# Comandos y pipelines

Workflows no triviales del proyecto. Detalle completo en `contexto.md` y `generadorinf.md`.

## Corregir un PCF nuevo (Plant 3D → CAESAR II)

```bash
python scripts/fix_pcf.py "RUTA/NUEVA LINEA/archivo.pcf"
```
Crea backup `archivo - ORIGINAL PLANT3D.pcf`. Vigilar AVISOS de stub-ends sin pareja.

## Regenerar datos del dashboard

```bash
python scripts/parse_caesar_md.py
```
Genera `dashboard/_data/lineas.json` + copia assets (iso, graficos, md, logo). **Verificación obligatoria**: comparar ratio/nodo de las 8 líneas contra [[20-Lineas/Resumen de líneas|la tabla verdad]].

## Servir dashboard local

```bash
cd dashboard && python -m http.server 8000   # http://localhost:8000
```

## Agregar nueva línea al dashboard

1. Exportar de CAESAR como `P2603-PR-PL-SIM-XXX.md` en la carpeta de la línea
2. Isométrico `PCFXXX.png` en la misma carpeta
3. Correr el parser y verificar contra tabla verdad
4. Commit + push → deploy automático (triggers: `dashboard/**`, `scripts/**`, `.github/workflows/**`, `.md` de líneas, `**/ResultadosGraficos*`)

## Informe LaTeX de una línea (pipeline generadorinf.md v1.1)

```bash
python scripts/extraer_informe.py --linea SIM-0XX   # tablas .tex + figuras + imágenes → informes/SIM-0XX/assets/
# Redactar sections/ + config/datos_proyecto.tex + references/bibliografia.bib
cd informes/SIM-0XX
JOB="I24.104-PP30-PP01-P-DOCS-18X"
mkdir -p build
pdflatex -jobname="$JOB" -interaction=nonstopmode -output-directory=build main.tex
bibtex "build/$JOB"   # desde la raíz del informe, NO desde build/
pdflatex -jobname="$JOB" -interaction=nonstopmode -output-directory=build main.tex
pdflatex -jobname="$JOB" -interaction=nonstopmode -output-directory=build main.tex
cp "build/$JOB.pdf" "$JOB.pdf"
```

- `compilar_informe.ps1` NO ejecuta bibtex → usar la secuencia manual si el informe cita bibliografía.
- Preview del PDF: `pdftoppm -f N -l N -r 60 -png archivo.pdf salida` (poppler de MiKTeX).
- Tras copiar la plantilla: verificar que `logos/logo2.png` sea Smurfit (≠ logo1 DML).
