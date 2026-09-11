#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extraer_informe.py — Extracción de tablas y figuras para informes LaTeX de
flexibilidad (generadorinf.md v1.1, pipeline paso 2).

Lee el reporte CAESAR II .md de una línea (fuente de verdad numérica) y genera
en informes/<SIM-XXX>/assets/:
  - tab_casos.tex                 Casos de carga (número, tipo, combinación)
  - tab_esfuerzos_critico.tex     Esfuerzos por nodo del caso crítico
  - tab_top5_ratio.tex            Top 5 nodos por ratio (cumplimiento B31.3)
  - tab_desplazamientos_max.tex   Máximos |DX|,|DY|,|DZ| por caso
  - tab_restricciones_{ope,sus,exp}.tex  Cargas en soportes (OPE=caso 1,
                                  SUS=primer caso SUS con presión, EXP=caso crítico)
  - fig_desplazamientos.png       DX/DY/DZ vs nodo (caso 1 OPE)
  - fig_esfuerzos.png             Bending vs nodo (caso crítico)
  - isometrico PCF* (copia) y gráficas CAESAR desde Graficas/ renombradas:
      graf_desplazamiento[_N].png   §9.1 desplazamientos
      graf_stress_percent[_N].png   §9.2 porcentaje de esfuerzo
      graf_nodos_soporte[_N].png    §9.3 nodos de soporte
    (excluye AnexoResultado* — en espera de instrucciones — y PCF*)
  - resumen_extraccion.json       Valores del resumen global CODE COMPLIANCE
                                  (para verificación T2 y uso en la prosa)

Uso: python scripts/extraer_informe.py --linea SIM-012
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ---------------------------------------------------------------- utilidades

def read_caesar_md(path: Path) -> list:
    """Lee un .md de CAESAR normalizando saltos de línea mixtos (\r\r\n)."""
    raw = path.read_bytes().decode('latin-1')
    raw = raw.replace('\r\n', '\n').replace('\r', '\n')
    return [x for x in raw.split('\n') if x.strip()]


REPORT_RE = re.compile(r'([A-Z][A-Z\.0-9 ]+) REPORT: (.+)')
CASE_RE = re.compile(r'CASE\s+(\d+)\s*\(([\w-]+)\)\s*(.*)$')


def split_reports(lines):
    """Agrupa líneas por sección REPORT, con su caso de carga."""
    sections = []
    cur = None
    for ln in lines:
        m = REPORT_RE.search(ln)
        if m:
            cur = {'report': m.group(1).strip(), 'desc': m.group(2).strip(),
                   'case': None, 'type': '', 'comb': '', 'lines': []}
            sections.append(cur)
            continue
        if cur is None:
            continue
        c = CASE_RE.search(ln)
        if c and cur['case'] is None:
            cur['case'] = int(c.group(1))
            cur['type'] = c.group(2)
            cur['comb'] = c.group(3).strip()
        cur['lines'].append(ln)
    return sections


def fnum(s):
    """float o None ('' / N/A)."""
    s = s.strip()
    if not s or s == 'N/A':
        return None
    try:
        return float(s)
    except ValueError:
        return None


def parse_tab_rows(sec_lines, nmin):
    """Filas tab-separadas que empiezan con número de nodo."""
    rows = []
    for ln in sec_lines:
        if re.match(r'^\s*\d+\t', ln):
            fields = [f.strip() for f in ln.split('\t')]
            if len(fields) >= nmin and fields[0].isdigit():
                rows.append(fields)
    return rows


def latex_num(x, dec=1):
    """Número para celda LaTeX con \\num{} (agrupación de miles vía siunitx)."""
    if x is None:
        return '--'
    return r'\num{' + f'{x:.{dec}f}' + '}'


def table_float(label, caption, cols, header, body_rows, size=r'\small'):
    """Tabla Elsevier completa (booktabs), lista para \\input{}."""
    out = [r'\begin{table}[htbp]', r'  \centering', f'  {size}',
           f'  \\caption{{{caption}}}', f'  \\label{{{label}}}',
           f'  \\begin{{tabular}}{{{cols}}}', r'    \toprule']
    out.append('    ' + ' & '.join(header) + r' \\')
    out.append(r'    \midrule')
    for r in body_rows:
        out.append('    ' + ' & '.join(r) + r' \\')
    out += [r'    \bottomrule', r'  \end{tabular}', r'\end{table}', '']
    return '\n'.join(out)


def esc(s):
    return s.replace('%', r'\%').replace('&', r'\&').replace('_', r'\_')


# ---------------------------------------------------------------- extracción

def find_md(root: Path, linea: str) -> Path:
    digits = linea.split('-')[1]
    for md in sorted(root.glob('*/P2603-PR-*.md')):
        if '_corrida_anterior' in str(md):
            continue
        raw = md.read_bytes()[:4000].decode('latin-1', errors='ignore')
        m = re.search(r'Job Name: (P2603-PR-(?:PL-)?(?:SIM-)?(\d+))', raw)
        if m and m.group(2) == digits:
            return md
    sys.exit(f'ERROR: no se encontró .md para {linea}')


def extract(root: Path, linea: str):
    md_path = find_md(root, linea)
    carpeta = md_path.parent
    lines = read_caesar_md(md_path)
    sections = split_reports(lines)

    # ---- casos de carga (únicos, ordenados por número) ----
    casos, seen = [], set()
    for ln in lines:
        c = CASE_RE.search(ln)
        if c and int(c.group(1)) not in seen:
            seen.add(int(c.group(1)))
            casos.append({'n': int(c.group(1)), 'type': c.group(2),
                          'comb': c.group(3).strip()})
    casos.sort(key=lambda c: c['n'])

    # ---- resumen global CODE COMPLIANCE (última sección) ----
    comp_secs = [s for s in sections if 'CODE COMPLIANCE' in s['report']]
    if not comp_secs:
        sys.exit('ERROR: sin CODE COMPLIANCE REPORT')
    txt = '\n'.join(comp_secs[-1]['lines'])
    passed = 'EVALUATION PASSED' in txt
    m = re.search(r'Ratio\s*\(%\):\s*([\d.]+)\s+@Node\s+(\d+)\s+LOADCASE:\s*(.+?)\s*$',
                  txt, re.M)
    ratio, node_crit, loadcase = float(m.group(1)), int(m.group(2)), m.group(3)
    code = float(re.search(r'Code Stress:\s+([\d.]+)', txt).group(1))
    allow = float(re.search(r'Allowable Stress:\s+([\d.]+)', txt).group(1))
    case_crit = int(re.match(r'(\d+)', loadcase).group(1))

    # ---- esfuerzos del caso crítico ----
    stress = [s for s in sections if 'STRESSES' in s['report']]
    sec_crit = next(s for s in stress if s['case'] == case_crit)
    esf = []
    for f in parse_tab_rows(sec_crit['lines'], 12):
        esf.append({'node': int(f[0]), 'slp': fnum(f[1]), 'fa': fnum(f[2]),
                    'bending': fnum(f[3]), 'torsion': fnum(f[4]),
                    'code': fnum(f[9]), 'allow': fnum(f[10]),
                    'ratio': fnum(f[11])})
    evaluados = [e for e in esf if e['ratio'] is not None]
    top5 = sorted(evaluados, key=lambda e: -e['ratio'])[:5]

    # ---- desplazamientos por caso ----
    # Secciones con campos de desbordamiento de formato ('**********') o con
    # salida deshabilitada (todos los campos N/A): el modo de cuerpo rígido
    # libre contamina los desplazamientos absolutos del caso; se excluyen de
    # tablas y figuras y se reportan en resumen_extraccion.json.
    displ = {}
    displ_overflow = set()
    for s in sections:
        if 'DISPLACEMENTS' in s['report'] and s['case']:
            raw_rows = parse_tab_rows(s['lines'], 4)
            vals = [fnum(v) for f in raw_rows for v in f[1:4]]
            if (any('*' in v for f in raw_rows for v in f[1:4])
                    or not any(v is not None for v in vals)):
                displ_overflow.add(s['case'])
                continue
            rows = [{'node': int(f[0]), 'dx': fnum(f[1]) or 0.0,
                     'dy': fnum(f[2]) or 0.0, 'dz': fnum(f[3]) or 0.0}
                    for f in raw_rows]
            if rows:
                displ[s['case']] = rows

    # ---- restricciones por caso ----
    restr = {}
    for s in sections:
        if s['report'] == 'RESTRAINTS' and s['case']:
            rows = []
            for f in parse_tab_rows(s['lines'], 7):
                tipo = ''
                joined = '\t'.join(f[7:]) if len(f) > 7 else ''
                tm = re.search(r'TYPE=([^;]+);?', joined)
                if tm:
                    tipo = tm.group(1).strip()
                rows.append({'node': int(f[0]),
                             'fx': fnum(f[1]) or 0.0, 'fy': fnum(f[2]) or 0.0,
                             'fz': fnum(f[3]) or 0.0, 'mx': fnum(f[4]) or 0.0,
                             'my': fnum(f[5]) or 0.0, 'mz': fnum(f[6]) or 0.0,
                             'type': tipo})
            if rows:
                restr[s['case']] = rows

    caso_label = {c['n']: f"{c['n']} ({c['type']}) {c['comb']}" for c in casos}
    fig_case = next((c['n'] for c in casos if c['n'] in displ), 1)
    return {
        'md_path': md_path, 'carpeta': carpeta, 'casos': casos,
        'passed': passed, 'ratio': ratio, 'node_crit': node_crit,
        'loadcase': loadcase, 'code': code, 'allow': allow,
        'case_crit': case_crit, 'esf': evaluados, 'top5': top5,
        'displ': displ, 'displ_overflow': sorted(displ_overflow),
        'fig_case': fig_case, 'restr': restr, 'caso_label': caso_label,
    }


# ---------------------------------------------------------------- salidas

def write_tables(data, assets: Path, linea: str):
    cl = data['caso_label']

    body = [[str(c['n']), esc(c['type']), esc(c['comb'])] for c in data['casos']]
    (assets / 'tab_casos.tex').write_text(table_float(
        'tab:casos', f'Casos de carga del análisis — línea {linea}.',
        'clc', ['Caso', 'Tipo', r'Combinaci\'on'], body), encoding='utf-8')

    body = [[str(e['node']), latex_num(e['bending']), latex_num(e['code']),
             latex_num(e['allow']), f"{e['ratio']:.1f}"] for e in data['esf']]
    (assets / 'tab_esfuerzos_critico.tex').write_text(table_float(
        'tab:esfuerzos-critico',
        f"Esfuerzos por nodo, caso crítico {esc(cl[data['case_crit']])} — línea {linea}.",
        'rrrrr', ['Nodo', 'Bending (\\si{kPa})', 'Code (\\si{kPa})',
                  'Allowable (\\si{kPa})', r'Ratio (\%)'], body,
        size=r'\footnotesize'), encoding='utf-8')

    body = [[str(i + 1), str(e['node']), latex_num(e['bending']),
             latex_num(e['code']), latex_num(e['allow']), f"{e['ratio']:.1f}",
             'Sí' if e['ratio'] <= 100 else 'No']
            for i, e in enumerate(data['top5'])]
    (assets / 'tab_top5_ratio.tex').write_text(table_float(
        'tab:top5-ratio',
        f'Nodos de mayor ratio de esfuerzo — línea {linea}. Criterio: Code $\\leq$ Allowable.',
        'crrrrrc', ['N', 'Nodo', 'Bending (\\si{kPa})', 'Code (\\si{kPa})',
                    'Allowable (\\si{kPa})', r'Ratio (\%)', 'Cumple'], body),
        encoding='utf-8')

    body = []
    for c in data['casos']:
        rows = data['displ'].get(c['n'], [])
        if not rows:
            continue
        mx = lambda k: max(abs(r[k]) for r in rows)
        body.append([f"{c['n']} ({esc(c['type'])})", f"{mx('dx'):.3f}",
                     f"{mx('dy'):.3f}", f"{mx('dz'):.3f}"])
    (assets / 'tab_desplazamientos_max.tex').write_text(table_float(
        'tab:desplaz-max',
        f'Desplazamientos máximos absolutos por caso de carga — línea {linea}.',
        'lrrr', ['Caso', r'max $|DX|$ (\si{mm})', r'max $|DY|$ (\si{mm})',
                 r'max $|DZ|$ (\si{mm})'], body), encoding='utf-8')

    sus_p = next((c['n'] for c in data['casos']
                  if c['type'] == 'SUS' and 'P' in c['comb']), None)
    # Tabla EXP: el caso crítico si es EXP; si no, el primer caso EXP del modelo
    tipo_crit = next(c['type'] for c in data['casos'] if c['n'] == data['case_crit'])
    exp_c = data['case_crit'] if tipo_crit == 'EXP' else next(
        (c['n'] for c in data['casos'] if c['type'] == 'EXP'), None)
    targets = {'ope': 1, 'sus': sus_p, 'exp': exp_c}
    for key, cn in targets.items():
        rows = data['restr'].get(cn)
        if not rows:
            print(f'  AVISO: sin restricciones para {key} (caso {cn})')
            continue
        body = [[str(r['node']), latex_num(r['fx'], 0), latex_num(r['fy'], 0),
                 latex_num(r['fz'], 0), latex_num(r['mx'], 0),
                 latex_num(r['my'], 0), latex_num(r['mz'], 0), esc(r['type'])]
                for r in rows]
        (assets / f'tab_restricciones_{key}.tex').write_text(table_float(
            f'tab:restricciones-{key}',
            f"Cargas en soportes, caso {esc(cl[cn])} — línea {linea}.",
            'lrrrrrrl', ['Nodo', 'FX (\\si{N})', 'FY (\\si{N})', 'FZ (\\si{N})',
                         'MX (\\si{N.m})', 'MY (\\si{N.m})', 'MZ (\\si{N.m})',
                         'Tipo'], body, size=r'\footnotesize'), encoding='utf-8')


def write_figures(data, assets: Path, linea: str):
    rows = data['displ'].get(data['fig_case'], [])
    if rows:
        x = [r['node'] for r in rows]
        fig, ax = plt.subplots(figsize=(8, 4.2))
        for k, lbl in [('dx', 'DX'), ('dy', 'DY'), ('dz', 'DZ')]:
            ax.plot(x, [r[k] for r in rows], marker='o', ms=3, lw=1.2, label=lbl)
        ax.set_xlabel('Nodo')
        ax.set_ylabel('Desplazamiento (mm)')
        ax.set_title(f"Desplazamientos caso {data['caso_label'][data['fig_case']]} — {linea}")
        ax.grid(alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(assets / 'fig_desplazamientos.png', dpi=300)
        plt.close(fig)

    esf = data['esf']
    if esf:
        x = [e['node'] for e in esf]
        y = [e['bending'] for e in esf]
        fig, ax = plt.subplots(figsize=(8, 4.2))
        ax.plot(x, y, marker='o', ms=3, lw=1.2, color='#b22222')
        imax = max(range(len(y)), key=lambda i: y[i])
        ax.annotate(f"máx {y[imax]:,.0f} kPa @N{x[imax]}".replace(',', ' '),
                    xy=(x[imax], y[imax]), xytext=(0.55, 0.85),
                    textcoords='axes fraction',
                    arrowprops=dict(arrowstyle='->', color='#444444'))
        ax.set_xlabel('Nodo')
        ax.set_ylabel('Esfuerzo bending (kPa)')
        ax.set_title(f"Esfuerzo de bending, caso {data['caso_label'][data['case_crit']]} — {linea}")
        ax.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(assets / 'fig_esfuerzos.png', dpi=300)
        plt.close(fig)


# Esquema de nombres para las gráficas CAESAR en los informes LaTeX:
# basename del PNG en Graficas/ → asset descriptivo (los .tex lo referencian).
GRAF_NOMBRE = {
    'Desplazamiento': 'graf_desplazamiento',    # §9.1
    'StressPercent': 'graf_stress_percent',     # §9.2
    'NodosSoporte': 'graf_nodos_soporte',       # §9.3
}


def copy_images(data, assets: Path):
    carpeta = data['carpeta']
    graf_dir = carpeta / 'Graficas'
    iso = None
    for ext in ('*.png', '*.jpeg', '*.jpg'):
        cand = [f for f in carpeta.glob(ext)
                if not f.name.startswith('ResultadosGraficos')]
        if graf_dir.is_dir():
            cand += [f for f in graf_dir.glob(ext)
                     if f.name.upper().startswith('PCF')]
        pcf = [f for f in cand if f.name.upper().startswith('PCF')]
        if pcf or cand:
            iso = (pcf or cand)[0]
            break
    if iso:
        shutil.copy2(iso, assets / iso.name)
        print(f'  isométrico: {iso.name}')
    if graf_dir.is_dir():
        for g in sorted(graf_dir.glob('*.png')):
            if g.name.startswith(('AnexoResultado', 'PCF')):
                continue
            m = re.match(r'([A-Za-z]+)(\d+)$', g.stem)
            base, num = m.groups() if m else (g.stem, '1')
            nombre = GRAF_NOMBRE.get(base, base.lower())
            sufijo = '' if num == '1' else f'_{num}'
            shutil.copy2(g, assets / f'{nombre}{sufijo}{g.suffix.lower()}')
            print(f'  gráfico: {g.name} -> {nombre}{sufijo}{g.suffix.lower()}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--linea', default='SIM-012')
    ap.add_argument('--root', default=str(Path(__file__).parent.parent))
    args = ap.parse_args()

    root = Path(args.root)
    assets = root / 'informes' / args.linea / 'assets'
    assets.mkdir(parents=True, exist_ok=True)

    data = extract(root, args.linea)
    write_tables(data, assets, args.linea)
    write_figures(data, assets, args.linea)
    copy_images(data, assets)

    resumen = {
        'linea': args.linea, 'md': str(data['md_path']),
        'passed': data['passed'], 'ratio_pct': data['ratio'],
        'nodo_critico': data['node_crit'], 'loadcase': data['loadcase'],
        'code_kpa': data['code'], 'allowable_kpa': data['allow'],
        'casos': data['casos'],
        'top5': [{'node': e['node'], 'ratio': e['ratio']} for e in data['top5']],
        'displ_overflow_casos': data['displ_overflow'],
        'displ_fig_case': data['fig_case'],
    }
    (assets / 'resumen_extraccion.json').write_text(
        json.dumps(resumen, indent=2, ensure_ascii=False), encoding='utf-8')

    print(f"\n=== Resumen extracción {args.linea} ===")
    print(f"  md: {data['md_path'].name}")
    print(f"  PASSED: {data['passed']} | ratio {data['ratio']} % @N{data['node_crit']}"
          f" | caso {data['loadcase']}")
    print(f"  Code {data['code']} kPa | Allowable {data['allow']} kPa")
    print(f"  casos: {len(data['casos'])} | nodos evaluados (caso crítico):"
          f" {len(data['esf'])}")
    if data['displ_overflow']:
        print(f"  AVISO: desplazamientos con campos overflow (*) excluidos,"
              f" casos: {data['displ_overflow']}")
    print(f"  assets -> {assets}")


if __name__ == '__main__':
    main()
