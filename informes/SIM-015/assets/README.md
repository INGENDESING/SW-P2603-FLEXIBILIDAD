# Directorio de Figuras del Proyecto

Coloque en esta carpeta todas las figuras, graficos, diagramas y planos
referenciados en el documento LaTeX.

## Convenciones de Nombrado

- Use nombres descriptivos en minusculas: `fig01_curva_bomba.png`, `fig02_perfil_presion.png`
- Prefijo `fig` para figuras generales, `tab` para tablas exportadas como imagen
- Formato preferido: PNG (raster) o PDF (vectorial)
- Resolucion minima: 300 DPI para figuras tecnicas

## Referenciacion en LaTeX

```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.85\textwidth]{assets/fig01_ejemplo.png}
    \caption{Leyenda descriptiva de la figura.}
    \label{fig:ejemplo}
\end{figure}
```

## Nota

Este directorio se ignora en el control de versiones si se configura `.gitignore`.
No incluya figuras con informacion sensible de cliente sin autorizacion.
