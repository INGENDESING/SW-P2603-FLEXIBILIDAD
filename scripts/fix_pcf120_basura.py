# -*- coding: utf-8 -*-
"""
Rescate de componentes que Plant 3D exportó en coordenada basura en PCF120.

Modos:
  --proponer  (solo lectura) tabla de propuesta de reconstrucción.
  --aplicar   escribe el PCF rescatado (respaldo previo 'PCF120 - ANTES RESCATE.pcf'):
              1) 24 stub-ends (PIPE degradados) -> FLANGE "LJ C/W STUB-END" con bore del vecino;
              2) elimina las 24 bridas LJ basura donantes;
              3) reubica las 10 válvulas bridadas basura en sus uniones (cara LAP + 3.175 mm);
              4) recupera el MAGNETIC FLOW METER 4" (INSTRUMENT, TAG FIT-I30BT09F01-F1);
              5) ramal 2": bola THD en hueco de 91.8 mm, 2x ELL 45 SW en huecos de 46.9 mm,
                 sockolet en el riser 6"; elimina el 2do sockolet (manual);
              6) elimina los 18 soportes basura (lista en 'PCF120 - SOPORTES ELIMINADOS.txt');
              7) deduplica GASKET/BOLT/WELD (artefactos 58x de la exportación).
              Al final ejecuta la verificación automática (T4).

Uso:
    python scripts/fix_pcf120_basura.py "15.0 DESCARGA BOMBA PP30BT17/PCF120.pcf" --proponer
    python scripts/fix_pcf120_basura.py "15.0 DESCARGA BOMBA PP30BT17/PCF120.pcf" --aplicar
"""
import math
import re
import shutil
import sys

GARBAGE = (-9776646.0, -9840066.0, -102887.0)
TOL = 0.75
GASKET_THK = 3.175  # 1/16"

EP_RE = re.compile(
    r'^\s*END-POINT\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+([\d.]+)(\s+([A-Z]+))?\s*$')

# pesos de brida LJ 150# por bore (de los donantes sanos) y códigos por bore
FL_W = {'3.0000': 4.082373219631679, '4.0000': 5.443164292842239, '6.0000': 8.164746439263357}
FL_CODE = {'3.0000': 'SSS3-12517', '4.0000': 'SSS3-12521', '6.0000': 'SSS3-12525'}


def is_garbage(c):
    return all(abs(c[i] - GARBAGE[i]) < 1.0 for i in range(3))


def vsub(a, b):
    return tuple(a[i] - b[i] for i in range(3))


def vadd(a, b):
    return tuple(a[i] + b[i] for i in range(3))


def vscale(a, s):
    return tuple(x * s for x in a)


def vlen(a):
    return math.sqrt(sum(x * x for x in a))


def vdot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def vcross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def vnorm(a):
    L = vlen(a)
    return tuple(x / L for x in a) if L else (0.0, 0.0, 0.0)


def dist(a, b):
    return vlen(vsub(a, b))


def fmt(c):
    return '(%.2f, %.2f, %.2f)' % c


def ep_line(c, bore, suffix=''):
    s = '    END-POINT        %.4f    %.4f    %.4f    %s' % (c[0], c[1], c[2], bore)
    return s + ('  ' + suffix if suffix else '')


class Block:
    def __init__(self, lines, idx):
        self.lines = lines
        self.idx = idx
        self.kw = lines[0].strip().split()[0] if lines[0].strip() else ''
        self.eps = []
        self.garbage = False
        for ln in lines:
            m = EP_RE.match(ln)
            if m:
                c = (float(m.group(1)), float(m.group(2)), float(m.group(3)))
                self.eps.append((c, m.group(4)))
                if is_garbage(c):
                    self.garbage = True
            elif re.match(r'^\s*(CO-ORDS|CENTRE-POINT|BRANCH1-POINT)', ln):
                p = ln.split()
                try:
                    if is_garbage((float(p[1]), float(p[2]), float(p[3]))):
                        self.garbage = True
                except (ValueError, IndexError):
                    pass

    def attr(self, name):
        for ln in self.lines:
            s = ln.strip()
            if s.startswith(name + ' ') or s == name:
                return s[len(name):].strip()
        return ''


def load(path):
    raw = open(path, 'rb').read().decode('latin-1')
    nl = '\r\n' if '\r\n' in raw else '\n'
    lines = raw.split(nl)
    while lines and lines[-1] == '':
        lines.pop()
    blocks, cur = [], []
    for ln in lines:
        if ln[:1] not in (' ', '\t') and ln.strip():
            if cur:
                blocks.append(Block(cur, len(blocks)))
            cur = [ln]
        else:
            cur.append(ln)
    if cur:
        blocks.append(Block(cur, len(blocks)))
    sec = '?'
    for bl in blocks:
        if bl.kw == 'PIPELINE-REFERENCE':
            sec = bl.lines[0].split()[-1]
        bl.section = sec
    return blocks, nl


def build_ep_map(blocks):
    ep_map = {}
    for bl in blocks:
        if bl.garbage:
            continue
        for c, bore in bl.eps:
            if not is_garbage(c):
                ep_map.setdefault(c, []).append((bl, bore))
    return ep_map


def make_neighbors(ep_map):
    def neighbors(coord, tol=TOL):
        out = []
        for k, v in ep_map.items():
            if dist(k, coord) <= tol:
                out.extend(v)
        return out
    return neighbors


def compute_stubs(blocks, neighbors):
    """24 stub-ends (PIPE degradados): cara LAP (la que apilan gaskets), bore del vecino."""
    stubs = [b for b in blocks
             if b.kw == 'PIPE' and 'STUB-END' in b.attr('ITEM-DESCRIPTION').upper()]
    info = []
    for st in stubs:
        (c1, _), (c2, _) = st.eps
        n1 = sum(1 for bl, _ in neighbors(c1) if bl.kw == 'GASKET')
        n2 = sum(1 for bl, _ in neighbors(c2) if bl.kw == 'GASKET')
        lap, other = (c1, c2) if n1 >= n2 else (c2, c1)
        bore = next((b for bl, b in neighbors(other)
                     if bl is not st and float(b) > 0), '?')
        info.append({'blk': st, 'lap': lap, 'other': other,
                     'n': vnorm(vsub(lap, other)), 'bore': bore,
                     'sec': st.section, 'code': st.attr('ITEM-CODE')})
    return info


def compute_pairs(stub_info):
    """Empareja stubs colineales, enfrentados, mismo bore. Devuelve (pairs, unpaired)."""
    cands = []
    for i in range(len(stub_info)):
        for j in range(i + 1, len(stub_info)):
            a, b = stub_info[i], stub_info[j]
            v = vsub(b['lap'], a['lap'])
            L = vlen(v)
            if L < 20 or L > 600:
                continue
            vn = vnorm(v)
            if vdot(vn, a['n']) < 0.999 or vdot(vnorm(vsub(a['lap'], b['lap'])), b['n']) < 0.999:
                continue
            if a['bore'] != b['bore']:
                continue
            cands.append((L, i, j))
    cands.sort()
    pairs, used = [], set()
    for L, i, j in cands:
        if i in used or j in used:
            continue
        used.update((i, j))
        pairs.append({'a': stub_info[i], 'b': stub_info[j], 'gap': L})
    return pairs, [k for k in range(len(stub_info)) if k not in used]


def classify(ff, bore):
    b = float(bore) if bore not in (None, '?') else 0
    if abs(ff - 248.0) < 8 and b == 4:
        return 'MAGMETER'
    if abs(ff - 50.96) < 1.5 and b == 3:
        return 'KNIFE3'
    if abs(ff - 165.1) < 2 and b == 3:
        return 'VPORT3'
    if abs(ff - 73.0) < 2 and b == 3:
        return 'CHECK3'
    if abs(ff - 98.4) < 2 and b == 6:
        return 'CHECK6'
    if b == 3 and (abs(ff - 42.0) < 2 or abs(ff - 46.9) < 2):
        return 'BFLY3'
    if b == 4 and abs(ff - 52.0) < 2:
        return 'BFLY4'
    if b == 6 and abs(ff - 57.3) < 2:
        return 'BFLY6'
    return '?'


def tangent_intersection(p1, d1, p2, d2):
    """Intersección de las tangentes (p1 + t·d1) y (p2 + s·d2) -> (punto, t, s)."""
    cr = vcross(d1, d2)
    denom = vdot(cr, cr)
    if denom < 1e-12:
        return None
    w = vsub(p2, p1)
    t = vdot(vcross(w, d2), cr) / denom
    s = vdot(vcross(w, d1), cr) / denom
    return vadd(p1, vscale(d1, t)), t, s


# ======================================================================
# MODO --proponer
# ======================================================================
def propose(path):
    blocks, _ = load(path)
    ep_map = build_ep_map(blocks)
    neighbors = make_neighbors(ep_map)
    stub_info = compute_stubs(blocks, neighbors)
    pairs, unpaired = compute_pairs(stub_info)

    print('(a) PARES: %d  |  sin pareja: %d' % (len(pairs), len(unpaired)))
    for n, p in enumerate(pairs, 1):
        ff = p['gap'] - 2 * GASKET_THK
        print('  %2d bore=%s FF=%6.1f %s <-> %s  %s'
              % (n, p['a']['bore'], ff, fmt(p['a']['lap']), fmt(p['b']['lap']),
                 classify(ff, p['a']['bore'])))
    for k in unpaired:
        s = stub_info[k]
        print('  sin pareja: bore=%s lap=%s' % (s['bore'], fmt(s['lap'])))


# ======================================================================
# MODO --aplicar
# ======================================================================
def apply(path):
    blocks, nl = load(path)
    ep_map = build_ep_map(blocks)
    neighbors = make_neighbors(ep_map)
    stub_info = compute_stubs(blocks, neighbors)
    pairs, unpaired = compute_pairs(stub_info)
    assert len(stub_info) == 24 and len(pairs) == 11 and len(unpaired) == 2, \
        'censo inesperado: stubs=%d pares=%d sueltos=%d' % (len(stub_info), len(pairs), len(unpaired))

    report = []
    delete_ids = set()        # bloques a eliminar (por índice)
    replace_lines = {}        # idx -> nuevas líneas del bloque
    insert_after = {}         # idx del bloque -> [bloques nuevos (listas de líneas)]

    # ---- 1) stub-ends -> FLANGE LJ C/W STUB-END ----
    for s in stub_info:
        st = s['blk']
        bore = s['bore']
        assert bore in FL_W, 'bore no mapeado: %r en %s' % (bore, fmt(s['lap']))
        new = ['FLANGE']
        skey_done = False
        for ln in st.lines[1:]:
            m = EP_RE.match(ln)
            if m:
                c = (float(m.group(1)), float(m.group(2)), float(m.group(3)))
                if dist(c, s['lap']) < TOL:
                    new.append(ep_line(c, bore, 'FL'))
                else:
                    new.append(ep_line(c, bore))
                continue
            s2 = ln.strip()
            if s2.startswith('SKEY'):
                new.append('    SKEY  FLWN')
                skey_done = True
            elif s2.startswith('ITEM-CODE'):
                if not skey_done:
                    new.append('    SKEY  FLWN')
                    skey_done = True
                new.append('    ITEM-CODE  ' + FL_CODE[bore])
            elif s2.startswith('ITEM-DESCRIPTION'):
                new.append('    ITEM-DESCRIPTION  FLANGE LJ C/W STUB-END, 150 LB, ASME B16.5 / B16.9-C')
            elif s2.startswith('COMPONENT-ATTRIBUTE2'):
                new.append('    COMPONENT-ATTRIBUTE2   BOMCOLUMN_SCHClass_150')
            elif s2.startswith('WEIGHT'):
                w = float(st.attr('WEIGHT') or 0) + FL_W[bore]
                new.append('    WEIGHT  ' + repr(w))
            else:
                new.append(ln)
        replace_lines[st.idx] = new
    report.append('24 stub-ends convertidos en FLANGE LJ C/W STUB-END (bore y peso por tamaño)')

    # ---- 2) eliminar las 24 bridas LJ basura donantes ----
    fl_garbage = [b for b in blocks if b.kw == 'FLANGE' and b.garbage]
    assert len(fl_garbage) == 24
    for b in fl_garbage:
        delete_ids.add(b.idx)
    report.append('24 bridas LJ basura eliminadas (donantes)')

    # ---- 3) válvulas bridadas a sus uniones ----
    for p in pairs:
        p['tipo'] = classify(p['gap'] - 2 * GASKET_THK, p['a']['bore'])
    valv_g = [b for b in blocks if b.kw == 'VALVE' and b.garbage]
    by_skey = {}
    for v in valv_g:
        by_skey.setdefault(v.attr('SKEY'), []).append(v)
    assign = {}  # valve block -> pair
    used_pairs = set()

    def take_pair(tipo):
        for k, p in enumerate(pairs):
            if k not in used_pairs and p['tipo'] == tipo:
                used_pairs.add(k)
                return p
        return None

    # asignaciones amarradas por tipo/FF
    for v in by_skey.get('CVFL', []):
        assign[v.idx] = take_pair('KNIFE3')           # PMVAL1-084
    for v in by_skey.get('VVFL', []):
        assign[v.idx] = take_pair('VPORT3')           # I30RF01K01-V1
    ck = by_skey.get('CKFL', [])                      # doc order: 037, 065, 305
    for v in ck[:2]:
        assign[v.idx] = take_pair('CHECK3')
    for v in ck[2:]:
        assign[v.idx] = take_pair('CHECK6')
    for v in by_skey.get('VYFL', []):                 # doc order: 079, s/TAG, Z01, 083, 306
        p = take_pair('BFLY3') or take_pair('BFLY4') or take_pair('BFLY6')
        assign[v.idx] = p
    assert all(p is not None for p in assign.values()) and len(used_pairs) == 10

    for v in valv_g:
        if v.attr('SKEY') == 'VBSC':
            continue  # la bola THD va al ramal, paso 5
        p = assign[v.idx]
        bore = p['a']['bore']
        ep1 = vadd(p['a']['lap'], vscale(p['a']['n'], GASKET_THK))
        ep2 = vadd(p['b']['lap'], vscale(p['b']['n'], GASKET_THK))
        new, ne = [], 0
        for ln in v.lines:
            if EP_RE.match(ln) and ne < 2:
                new.append(ep_line(ep1 if ne == 0 else ep2, bore, 'FL'))
                ne += 1
            else:
                new.append(ln)
        replace_lines[v.idx] = new
        report.append('Válvula TAG=%s (%s) reubicada: unión %s FF=%.1f bore=%s'
                      % (v.attr('TAG') or '—', v.attr('SKEY'), p['tipo'],
                         p['gap'] - 2 * GASKET_THK, bore))

    # ---- 4) MAGNETIC FLOW METER 4" (INSTRUMENT) ----
    mpair = take_pair('MAGMETER')
    assert mpair is not None
    ep1 = vadd(mpair['a']['lap'], vscale(mpair['a']['n'], GASKET_THK))
    ep2 = vadd(mpair['b']['lap'], vscale(mpair['b']['n'], GASKET_THK))
    instr = ['INSTRUMENT',
             ep_line(ep1, '4.0000', 'FL'),
             ep_line(ep2, '4.0000', 'FL'),
             '    SKEY  IIFL',
             '    ITEM-CODE  MAGNETIC FLOW METER, 4" ND, CL 150, RF',
             '    ITEM-DESCRIPTION  MAGNETIC FLOW METER, CL 150, RF',
             '    FABRICATION-ITEM',
             '    TAG  FIT-I30BT09F01-F1',
             '    PIPING-SPEC  SSS3',
             '    TRACING-SPEC  ',
             '    COMPONENT-ATTRIBUTE1   BOMCOLUMN_Material_',
             '    COMPONENT-ATTRIBUTE2   BOMCOLUMN_SCHClass_150']
    anchor = max(mpair['a']['blk'].idx, mpair['b']['blk'].idx)
    insert_after.setdefault(anchor, []).append(instr)
    report.append('MAGNETIC FLOW METER 4" recuperado como INSTRUMENT (unión MAGMETER, FF=%.1f)'
                  % (mpair['gap'] - 2 * GASKET_THK))

    # ---- 5) ramal 2": bola THD, 2x ELL 45 SW, sockolet ----
    small = [b for b in blocks if b.kw == 'PIPE' and not b.garbage
             and 'STUB-END' not in b.attr('ITEM-DESCRIPTION').upper()
             and b.eps and all(0 < float(bo) <= 2.0 for _, bo in b.eps)]

    def only_pipe_weld(coord):
        hits = [(bl, bo) for bl, bo in neighbors(coord)]
        pipes = [bl for bl, _ in hits if bl.kw == 'PIPE']
        return (len(pipes) == 1
                and all(bl.kw in ('PIPE', 'WELD') for bl, _ in hits)), (pipes[0] if pipes else None)

    gaps = []   # (d, c1, c2, pipe1, pipe2)
    ends = []
    for b in small:
        for c, _ in b.eps:
            ok, pipe = only_pipe_weld(c)
            if ok:
                ends.append((c, b))
    raw_gaps = []
    for i in range(len(ends)):
        for j in range(i + 1, len(ends)):
            c1, b1 = ends[i]
            c2, b2 = ends[j]
            if b1 is b2:
                continue
            d = dist(c1, c2)
            if 20 < d < 250:
                raw_gaps.append((d, c1, c2, b1, b2))
    # descartar huecos transitivos: si un tercer extremo queda más cerca de ambos,
    # el hueco real es el menor (el mayor solo lo contiene)
    for d, c1, c2, b1, b2 in raw_gaps:
        transitivo = any(
            dist(c1, c3) < d * 0.999 and dist(c2, c3) < d * 0.999
            for c3, b3 in ends if b3 is not b1 or (dist(c3, c1) > TOL and dist(c3, c2) > TOL))
        if not transitivo:
            gaps.append((d, c1, c2, b1, b2))
    gaps.sort()
    assert len(gaps) == 3, 'huecos de ramal inesperados: %s' % [(round(g[0], 1)) for g in gaps]

    # 5a) bola THD en el hueco mayor (91.8)
    ball = next(v for v in valv_g if v.attr('SKEY') == 'VBSC')
    d, c1, c2, _, _ = gaps[-1]
    new, ne = [], 0
    for ln in ball.lines:
        if EP_RE.match(ln) and ne < 2:
            new.append(ep_line(c1 if ne == 0 else c2, '2.0000'))
            ne += 1
        else:
            new.append(ln)
    replace_lines[ball.idx] = new
    report.append('Bola THD 2" (TAG=%s) en hueco de %.1f mm del ramal' % (ball.attr('TAG'), d))

    # 5b) 2x ELL 45 SW en los huecos de 46.9
    ell_g = [b for b in blocks if b.kw == 'ELBOW' and b.garbage]
    assert len(ell_g) == 2
    for (d, c1, c2, p1, p2), ell in zip(gaps[:2], ell_g):
        d1 = vnorm(vsub(c1, next(c for c, _ in p1.eps if dist(c, c1) > TOL)))
        d2 = vnorm(vsub(next(c for c, _ in p2.eps if dist(c, c2) > TOL), c2))
        ti = tangent_intersection(c1, d1, c2, d2)
        assert ti is not None
        centre, t1, t2 = ti
        new = []
        for ln in ell.lines:
            if EP_RE.match(ln):
                if not hasattr(ell, '_ne'):
                    ell._ne = 0
                new.append(ep_line(c1 if ell._ne == 0 else c2, '2.0000', 'SW'))
                ell._ne += 1
            elif ln.strip().startswith('CENTRE-POINT'):
                new.append('    CENTRE-POINT     %.4f    %.4f    %.4f' % centre)
            elif ln.strip().startswith('ANGLE'):
                new.append('    ANGLE   4500')
            else:
                new.append(ln)
        replace_lines[ell.idx] = new
        report.append('ELL 45 SW reubicado (hueco %.1f mm; tangentes %.1f/%.1f mm)' % (d, abs(t1), abs(t2)))

    # 5c) sockolet en el riser 6"; el 2º se elimina (manual)
    start = next(c for c, b in ends
                 if all(dist(c, g[1]) > TOL and dist(c, g[2]) > TOL for g in gaps)
                 and dist(c, (0.7641, 0.1153, c[2])) < 200)
    ole_g = [b for b in blocks if b.kw == 'OLET' and b.garbage]
    assert len(ole_g) == 2
    new = []
    for ln in ole_g[0].lines:
        if ln.strip().startswith('CENTRE-POINT'):
            new.append('    CENTRE-POINT     %.4f    %.4f    %.4f' % (0.7641, 0.1153, start[2]))
        elif ln.strip().startswith('BRANCH1-POINT'):
            new.append('    BRANCH1-POINT    %.4f    %.4f    %.4f    2.0000' % start)
        else:
            new.append(ln)
    replace_lines[ole_g[0].idx] = new
    delete_ids.add(ole_g[1].idx)
    report.append('Sockolet 1 en riser 6" (CENTRE (0.7641, 0.1153, %.2f), BRANCH1 %s); '
                  'sockolet 2 ELIMINADO (ubicación no resoluble — revisar en isométrico/CAESAR)'
                  % (start[2], fmt(start)))

    # ---- 6) soportes basura ----
    sup_g = [b for b in blocks if b.kw == 'SUPPORT' and b.garbage]
    sup_txt = ['Soportes eliminados de PCF120.pcf (exportación Plant 3D en coordenada basura).',
               'Reponer manualmente en CAESAR II según el modelo Plant 3D / isométrico.', '']
    for n, s in enumerate(sup_g, 1):
        delete_ids.add(s.idx)
        sup_txt.append('%3d  %-12s SKEY=%-6s %s' % (n, s.section, s.attr('SKEY') or '—',
                                                    s.attr('ITEM-DESCRIPTION') or '(bloque vacío)'))
    open(path.replace('.pcf', ' - SOPORTES ELIMINADOS.txt'), 'w', encoding='utf-8').write(
        '\n'.join(sup_txt) + '\n')
    report.append('%d soportes eliminados (lista en PCF120 - SOPORTES ELIMINADOS.txt)' % len(sup_g))

    # ---- 7) dedupe GASKET/BOLT/WELD ----
    seen_sig = {}
    ndup = 0
    for b in blocks:
        if b.kw not in ('GASKET', 'BOLT', 'WELD') or b.garbage or b.idx in delete_ids:
            continue
        pts = []
        for ln in b.lines:
            m = EP_RE.match(ln) or re.match(
                r'^\s*CO-ORDS\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)', ln)
            if m:
                pts.append(tuple(round(float(m.group(k)), 1) for k in (1, 2, 3)))
        sig = (b.kw, tuple(sorted(pts)))
        if sig in seen_sig:
            delete_ids.add(b.idx)
            ndup += 1
        else:
            seen_sig[sig] = b.idx
    report.append('Duplicados 58x eliminados: %d bloques GASKET/BOLT/WELD' % ndup)

    # ---- escribir ----
    bak = path.replace('.pcf', ' - ANTES RESCATE.pcf')
    shutil.copyfile(path, bak)
    out = []
    for b in blocks:
        if b.idx in delete_ids:
            continue
        out.extend(replace_lines.get(b.idx, b.lines))
        for extra in insert_after.get(b.idx, []):
            out.extend(extra)
    open(path, 'wb').write((nl.join(out) + nl).encode('latin-1'))
    print('Respaldo:', bak)
    print('Escrito :', path)
    print()
    print('ACCIONES:')
    for r in report:
        print(' -', r)


# ======================================================================
# Verificación (T4)
# ======================================================================
def verify(path):
    blocks, _ = load(path)
    text = open(path, 'rb').read().decode('latin-1')
    print()
    print('=' * 100)
    print('VERIFICACIÓN POST-PARCHE')
    print('-' * 100)
    ngarbage = text.count('-9776646')
    print('[1] Ocurrencias de coordenada basura: %d %s' % (ngarbage, 'OK' if ngarbage == 0 else 'FALLA'))

    from collections import Counter
    cnt = Counter(b.kw for b in blocks)
    gcnt = Counter(b.kw for b in blocks if b.garbage)
    print('[2] Conteos: FLANGE=%d VALVE=%d INSTRUMENT=%d ELBOW=%d OLET=%d SUPPORT=%d GASKET=%d BOLT=%d WELD=%d'
          % (cnt['FLANGE'], cnt['VALVE'], cnt['INSTRUMENT'], cnt['ELBOW'], cnt['OLET'],
             cnt['SUPPORT'], cnt['GASKET'], cnt['BOLT'], cnt['WELD']))
    print('    Bloques aún en basura por tipo: %s %s' % (dict(gcnt) or '{}', 'OK' if not gcnt else 'FALLA'))

    # conectividad: todo END-POINT de componente reconstruido toca otro bloque distinto
    ep_map = {}
    for b in blocks:
        for c, bore in b.eps:
            ep_map.setdefault(c, []).append(b)

    def n_blocks(coord):
        s = set()
        for k, v in ep_map.items():
            if dist(k, coord) <= TOL:
                s.update(id(x) for x in v)
        return s

    orphan = []
    for b in blocks:
        if b.kw in ('GASKET', 'BOLT', 'WELD', 'PIPELINE-REFERENCE'):
            continue
        for c, _ in b.eps:
            others = n_blocks(c) - {id(b)}
            if not others:
                orphan.append((b.kw, b.attr('TAG') or b.attr('ITEM-DESCRIPTION')[:40], fmt(c)))
    print('[3] Extremos de componentes sin vecino (nodos sueltos): %d' % len(orphan))
    for o in orphan:
        print('      SUELTO: %s %s %s' % o)

    # coherencia de bore en nodos compartidos por componentes portantes
    ep_bore = {}
    for b in blocks:
        for c, bore in b.eps:
            ep_bore.setdefault(c, []).append((b, bore))
    bad_bore = 0
    for b in blocks:
        if b.kw not in ('FLANGE', 'VALVE', 'INSTRUMENT', 'ELBOW', 'OLET', 'PIPE', 'TEE', 'REDUCER-CONCENTRIC'):
            continue
        for c, bore in b.eps:
            if float(bore) == 0:
                continue
            for k, v in ep_bore.items():
                if dist(k, c) <= TOL:
                    for b2, bo2 in v:
                        if b2 is not b and b2.kw not in ('GASKET', 'BOLT', 'WELD') \
                           and float(bo2) > 0 and bo2 != bore:
                            bad_bore += 1
                            print('      BORE DISTINTO en %s: %s (%s) vs %s (%s)'
                                  % (fmt(c), bore, b.kw, bo2, b2.kw))
    print('[4] Nodos con bore incoherente: %d %s' % (bad_bore, 'OK' if bad_bore == 0 else 'REVISAR'))

    # bridas fusionadas: 24 FLANGE con SKEY FLWN y bore > 0
    flwn = [b for b in blocks if b.kw == 'FLANGE' and b.attr('SKEY') == 'FLWN']
    ok_fl = all(all(float(bo) > 0 for _, bo in b.eps) and len(b.eps) == 2 for b in flwn)
    print('[5] FLANGE FLWN fusionadas: %d (bore>0 y 2 EPs: %s)' % (len(flwn), 'OK' if ok_fl and len(flwn) == 24 else 'REVISAR'))


def main():
    path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else '--proponer'
    if mode == '--aplicar':
        apply(path)
        verify(path)
    else:
        propose(path)
        verify(path) if mode == '--verificar' else None


if __name__ == '__main__':
    main()
