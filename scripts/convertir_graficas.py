#!/usr/bin/env python3
"""
Conversor de gráficas CAESAR II .tif → .png
Recorre las subcarpetas */Graficas/ de las líneas y convierte cada .tif
exportado de CAESAR (RGBA, 12-18 MB) a .png con el mismo basename, para
uso en el dashboard (navegador) y en los informes LaTeX.

- Los RGBA se aplanan sobre fondo blanco (CAESAR exporta fondo transparente).
- Preserva los dpi del .tif en los metadatos del .png.
- Excluye AnexoResultado* (en espera de instrucciones) y no toca los PCF*.
- Idempotente: omite el .png si existe y es más reciente que el .tif
  (salvo --force).

Uso: python scripts/convertir_graficas.py [--force]
"""

import argparse
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None  # tif de 12-18 MB superan el límite por defecto

EXCLUIR_PREFIJOS = ('AnexoResultado', 'PCF')


def convertir_tif(tif_path: Path) -> str:
    """Convierte un .tif a .png (mismo basename, misma carpeta). Devuelve nota."""
    im = Image.open(tif_path)
    nota = f'{im.format} {im.mode} {im.size[0]}x{im.size[1]}'
    dpi = im.info.get('dpi')

    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
        rgba = im.convert('RGBA')
        fondo = Image.new('RGB', rgba.size, (255, 255, 255))
        fondo.paste(rgba, mask=rgba.split()[-1])
        im = fondo
    else:
        im = im.convert('RGB')

    save_kwargs = {}
    if dpi:
        save_kwargs['dpi'] = dpi

    im.save(tif_path.with_suffix('.png'), 'PNG', **save_kwargs)
    return nota


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--force', action='store_true',
                    help='reconvierte aunque el .png sea más reciente que el .tif')
    args = ap.parse_args()

    root_dir = Path(__file__).parent.parent

    total, omitidos = 0, 0
    for graf_dir in sorted(root_dir.glob('*/Graficas')):
        if '_corrida_anterior' in str(graf_dir):
            continue
        tifs = [t for t in sorted(graf_dir.glob('*.tif'))
                if not t.name.startswith(EXCLUIR_PREFIJOS)]
        if not tifs:
            continue

        convertidos = []
        for tif_path in tifs:
            png_path = tif_path.with_suffix('.png')
            if (not args.force and png_path.exists()
                    and png_path.stat().st_mtime >= tif_path.stat().st_mtime):
                omitidos += 1
                continue
            nota = convertir_tif(tif_path)
            convertidos.append(f'{tif_path.name} ({nota})')

        if convertidos:
            print(f'{graf_dir.parent.name}: {len(convertidos)} PNG')
            for c in convertidos:
                print(f'  {c}')
            total += len(convertidos)

    print(f"\n{'='*50}")
    print(f'Total convertidos: {total} | omitidos (al día): {omitidos}')
    print(f"{'='*50}")


if __name__ == '__main__':
    main()
