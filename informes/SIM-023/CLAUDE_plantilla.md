# Plantilla LaTeX para Informes Tecnicos de Ingenieria --- DML

## Descripcion

Esta es una **plantilla de formato reutilizable** para la elaboracion de informes tecnicos, memorias descriptivas, memorias de calculo y documentacion de ingenieria bajo estandares profesionales. La plantilla esta construida sobre la clase `elsarticle` con personalizaciones corporativas DML.

**No contiene contenido de proyecto alguno.** Toda la informacion especifica se centraliza en `config/datos_proyecto.tex` y las secciones modulares se entregan con texto guia que debe reemplazarse por el contenido tecnico del proyecto.

---

## Estructura de Archivos

```
.
├── main.tex                          # Documento maestro (no editar)
├── config/
│   ├── preamble.tex                  # Paquetes y configuracion LaTeX (no editar)
│   ├── header.tex                    # Membrete corporativo (no editar)
│   └── datos_proyecto.tex            # <-- EDITAR: datos del proyecto
├── sections/
│   ├── 00_hojafirmas.tex             # Hoja de firmas (usa datos_proyecto.tex)
│   ├── 00_portada.tex                # Portada con control de revisiones
│   ├── 01_frontmatter.tex            # Abstract y keywords <-- EDITAR
│   ├── 02_resumen.tex                # Resumen ejecutivo <-- EDITAR
│   ├── 03_nomenclatura.tex           # Nomenclatura (conservar/ampliar)
│   ├── 04_introduccion.tex           # <-- EDITAR
│   ├── 05_objetivos.tex              # <-- EDITAR
│   ├── 06_alcance.tex                # <-- EDITAR
│   ├── 07_bases_disenio.tex          # <-- EDITAR
│   ├── 08_metodologia.tex            # <-- EDITAR
│   ├── 09_resultados.tex             # <-- EDITAR
│   ├── 10_analisis.tex               # <-- EDITAR
│   ├── 11_conclusiones.tex           # <-- EDITAR
│   ├── 12_recomendaciones.tex        # <-- EDITAR
│   └── 13_anexos.tex                 # <-- EDITAR
├── references/
│   └── bibliografia.bib              # <-- EDITAR: referencias del proyecto
├── assets/                           # <-- AGREGAR: figuras del proyecto
├── logos/
│   ├── logo1.png                     # Logo DML (no cambiar)
│   └── logo2.png                     # Logo DML alterno (no cambiar)
└── compilar_informe.ps1              # Script de compilacion
```

---

## Instrucciones de Uso

### 1. Configurar datos del proyecto

Edite unicamente `config/datos_proyecto.tex` con la informacion del nuevo proyecto.

**Datos basicos del proyecto:**

```latex
\newcommand{\projecttitle}{Titulo del proyecto}
\newcommand{\documentcode}{PXXXX-PR-INF-001}
\newcommand{\documenttype}{MEMORIA DESCRIPTIVA}
\newcommand{\targetcompany}{Nombre del cliente}
\newcommand{\projectnumber}{PXXXX}
\newcommand{\firmaElaboro}{J. Perez}
\newcommand{\firmaReviso}{A. Lopez}
\newcommand{\firmaAprobo}{C. Gomez}
```

**Textos del membrete (encabezado):**

El membrete corporativo se configura completamente desde `datos_proyecto.tex`. Modifique las lineas del titulo que aparecen en la columna central:

```latex
\newcommand{\headerlinetitulo}{DISEÑO DE INGENIERIA}
\newcommand{\headerlineuno}{DIAGNOSTICO DE SISTEMAS EN OPERACION}
\newcommand{\headerlinedos}{MEMORIA DESCRIPTIVA}
```

Y las etiquetas de la columna derecha (si necesita traduccion o ajuste):

```latex
\newcommand{\headerlabelcode}{CODIGO:}
\newcommand{\headerlabelrevision}{REVISION:}
\newcommand{\headerlabeldate}{FECHA:}
\newcommand{\headerlabelelaboro}{ELABORO:}
\newcommand{\headerlabelreviso}{REVISO:}
\newcommand{\headerlabelaprobo}{APROBO:}
\newcommand{\headerlabelproject}{PROYECTO:}
```

### 2. Escribir contenido tecnico

Edite cada archivo en `sections/` reemplazando:
- Los **comentarios de guia** entre corchetes `[...]` por parrafos tecnicos
- Los **placeholders de tablas** entre angulos `<...>` por datos reales del proyecto
- Los **placeholders de figuras** comentados (lineas que empiezan con `%`) por entornos `figure` activos

**Importante:** Mantenga la estructura de tablas, figuras y ecuaciones como referencia de formato. Las tablas usan estilo Elsevier con `toprule`, `midrule`, `bottomrule`.

### 3. Agregar figuras

1. Coloque las figuras del proyecto en `assets/` (formato PNG o PDF)
2. En las secciones correspondientes, **descomente** el bloque `figure` (elimine los `%` al inicio de linea)
3. Actualice la ruta y la leyenda:

```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.85\textwidth]{assets/mi_figura_real.png}
    \caption{Curva caracteristica de la bomba de alimentacion.}
    \label{fig:bomba}
\end{figure}
```

### 4. Actualizar bibliografia

Agregue las referencias bibliograficas del proyecto en `references/bibliografia.bib`. Use las plantillas de ejemplo incluidas al final del archivo:

```bibtex
@manual{mi_ficha_tecnica,
  author       = {{Fabricante}},
  title        = {Titulo de la ficha tecnica},
  organization = {Organizacion},
  year         = {2024},
  note         = {Notas adicionales}
}
```

Cite en el texto con `~\cite{mi_ficha_tecnica}`.

### 5. Compilar

**Opcion A -- Usar el script (recomendado):**

```powershell
# Con nombre de proyecto explicito (recomendado):
.\compilar_informe.ps1 -jobName "P2613-PR-INF-001"

# Con nombre por defecto (genera DOCUMENTO.pdf):
.\compilar_informe.ps1
```

El script:
- Compila dos veces para resolver referencias cruzadas
- Guarda el PDF en `build/<nombre>.pdf`
- Copia el PDF a la raiz del proyecto
- Oculta los archivos auxiliares en `build/`

**Opcion B -- Compilacion manual:**

```powershell
pdflatex -jobname="P2613-PR-INF-001" -interaction=nonstopmode -output-directory=build main.tex
pdflatex -jobname="P2613-PR-INF-001" -interaction=nonstopmode -output-directory=build main.tex
```

---

## Convenciones de Formato Obligatorias

### Tablas
- Estilo Elsevier: `toprule`, `midrule`, `bottomrule`
- Sin bordes verticales
- Numeracion automatica con `\setcounter{itemcount}{0}` y columna `N`
- Leyenda arriba de la tabla: `\caption{...} \label{tab:...}`

### Figuras
- Leyenda debajo de la figura
- Referenciadas en texto antes de aparecer: `Figura~\ref{fig:...}`
- Ancho preferido: `width=0.85\textwidth`

### Ecuaciones
- Numeradas a la derecha con `\label{eq:...}`
- Variables definidas inmediatamente despues de la ecuacion

### Unidades
- Usar paquete `siunitx`: `\si{\celsius}`, `\si{bar}`, `\si{m/s}`
- Espacio entre valor y unidad: `25~\si{\celsius}`, no `25\si{\celsius}`

### Prohibiciones
- No usar viñetas en informes formales (usar tablas o parrafos numerados)
- No inventar valores de propiedades fisicas sin fuente
- No transcribir contexto innecesario: referenciar archivos en lugar de copiar contenido

---

## Estandares y Normas Soportados

La plantilla esta preparada para documentacion bajo:
- ASME (VIII, B31.1, B31.3, BPE)
- API (650, 610, 620)
- NFPA (13, 15, 20, 72, 400)
- TEMA, HI
- Normativa colombiana (RETIE, Resolucion 0312)

---

## Personalizacion Avanzada

### Cambiar logos
Reemplace los archivos en `logos/` manteniendo los nombres `logo1.png` y `logo2.png`, o modifique las rutas en `config/header.tex`.

### Modificar membrete (encabezado corporativo)
**No edite `config/header.tex`.** Todos los textos del membrete (titulo, etiquetas CÓDIGO/REVISIÓN/FECHA/etc.) se configuran desde `config/datos_proyecto.tex` mediante los comandos `\headerlinetitulo`, `\headerlabelcode`, etc.

Solo edite `header.tex` si necesita cambiar proporciones de columnas, numero de filas o el diseño estructural del membrete.

### Modificar estilo de tablas de firma
Edite `sections/00_hojafirmas.tex` para ajustar el formato de control de elaboracion/revision.

### Agregar paquetes LaTeX
Anada paquetes en `config/preamble.tex` (verificar compatibilidad con `elsarticle` y `fancyhdr`).

---

## Version de la Plantilla

- **Formato base**: LaTeX, clase `elsarticle`
- **Tamano de papel**: A4, 12pt
- **Tipografia**: TeX Gyre Termes (TG Termes)
- **Motor de compilacion**: pdfLaTeX
- **Codificacion**: UTF-8
