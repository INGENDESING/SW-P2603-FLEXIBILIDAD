# -*- coding: utf-8 -*-
"""
Corrige PCF de Plant 3D 2027 para que CAESAR II 2019 lo pueda importar.

Transformaciones:
 1. Elimina bloques END-POSITION-* del encabezado (no soportados).
 2. Elimina INSTRUMENT-DIAL (manometro PI) e INSTRUMENT de longitud cero (PT).
 3. Fusiona cada LAPJOINT-STUBEND + FLANGE de longitud cero en una sola
    FLANGE con la longitud del stub-end y el peso combinado.
 4. Elimina lineas TAP-CONNECTION y su CO-ORDS asociada.
 5. Elimina lineas STATUS DOTTED-DIMENSIONED y MATERIAL-LIST EXCLUDE.
 6. Repara el ITEM-CODE duplicado/corrupto de las valvulas actuadas.
"""
import re
import shutil
import sys

SRC = sys.argv[1]
BAD_VALVE_CODE = ('BALL VALVE, PNEUMATIC ACTUATOR, 8" ND, 150 LB, RF, ASME B16.10'
                  'BALL VALVE, PNEUMATIC ACTUATOR, 6" ND, 150 LB, RF, ASME B16.10')
GOOD_VALVE_CODE = 'BALL VALVE, PNEUMATIC ACTUATOR, 6" ND, 150 LB, RF, ASME B16.10'

raw = open(SRC, 'rb').read()
text = raw.decode('latin-1')
nl = '\r\n' if '\r\n' in text else '\n'
lines = text.split(nl)
# quitar posible linea vacia final para reponerla al escribir
trailing_empty = 0
while lines and lines[-1] == '':
    lines.pop()
    trailing_empty += 1

# ---- separar en bloques: una linea sin sangria inicia bloque ----
blocks = []          # lista de listas de lineas
for ln in lines:
    if ln[:1] not in (' ', '\t') and ln.strip():
        blocks.append([ln])
    else:
        if not blocks:
            blocks.append([])
        blocks[-1].append(ln)

def keyword(block):
    return block[0].strip() if block and block[0].strip() else ''

# indice del bloque MATERIALS (todo lo de ahi en adelante se pasa casi intacto)
mat_idx = next((i for i, b in enumerate(blocks) if keyword(b) == 'MATERIALS'), len(blocks))
body, tail = blocks[:mat_idx], blocks[mat_idx:]

EP_RE = re.compile(r'^(\s*END-POINT\s+)(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+([\d.]+)(\s+([A-Z]+))?\s*$')

def endpoints(block):
    out = []
    for i, ln in enumerate(block):
        m = EP_RE.match(ln)
        if m:
            coords = tuple(round(float(m.group(k)), 2) for k in (2, 3, 4))
            out.append({'idx': i, 'line': ln, 'coords': coords,
                        'bore': m.group(5), 'type': m.group(7) or ''})
    return out

def attr(block, name):
    for ln in block:
        s = ln.strip()
        if s.startswith(name + ' ') or s == name:
            return s[len(name):].strip()
    return ''

stats = {'end_position': 0, 'instr_dial': 0, 'instr_zero': 0, 'pairs': 0,
         'tap': 0, 'status': 0, 'mlist': 0, 'valve_code': 0}

# ---- pase 1: clasificar bloques ----
# bridas de longitud cero indexadas por coordenada
flange_by_coord = {}
for b in body:
    if keyword(b) == 'FLANGE':
        eps = endpoints(b)
        if len(eps) == 2 and eps[0]['coords'] == eps[1]['coords']:
            flange_by_coord.setdefault(eps[0]['coords'], []).append(b)

consumed = set()   # id() de bloques FLANGE absorbidos

def merge_stubend(b):
    """LAPJOINT-STUBEND -> FLANGE fusionada con la brida loca en su cara LAP."""
    eps = endpoints(b)
    lap = next((e for e in eps if e['type'] == 'LAP'), None)
    if lap is None or len(eps) != 2:
        return None
    fl_list = flange_by_coord.get(lap['coords'], [])
    fl = next((f for f in fl_list if id(f) not in consumed), None)
    if fl is None:
        return None
    consumed.add(id(fl))
    other = next(e for e in eps if e is not lap)
    lap_line = re.sub(r'LAP\s*$', 'FL', lap['line'])
    w_stub = float(attr(b, 'WEIGHT') or 0)
    w_fl = float(attr(fl, 'WEIGHT') or 0)
    spec = attr(fl, 'PIPING-SPEC') or attr(b, 'PIPING-SPEC')
    code = attr(fl, 'ITEM-CODE')
    new = ['FLANGE',
           lap_line,
           other['line'],
           '    SKEY  FLWN',
           '    ITEM-CODE  ' + code,
           '    ITEM-DESCRIPTION  FLANGE LJ C/W STUB-END, 150 LB, ASME B16.5 / B16.9-C',
           '    FABRICATION-ITEM',
           '    PIPING-SPEC  ' + spec,
           '    TRACING-SPEC  ',
           '    COMPONENT-ATTRIBUTE1   BOMCOLUMN_Material_',
           '    COMPONENT-ATTRIBUTE2   BOMCOLUMN_SCHClass_150',
           '    WEIGHT  ' + repr(w_stub + w_fl)]
    stats['pairs'] += 1
    return new

def clean_lines(b):
    """quita TAP-CONNECTION (+CO-ORDS siguiente), STATUS y MATERIAL-LIST"""
    out, skip_coords = [], False
    for ln in b:
        s = ln.strip()
        if skip_coords and s.startswith('CO-ORDS'):
            skip_coords = False
            continue
        skip_coords = False
        if s.startswith('TAP-CONNECTION'):
            stats['tap'] += 1
            skip_coords = True
            continue
        if s.startswith('STATUS DOTTED-DIMENSIONED'):
            stats['status'] += 1
            continue
        if s.startswith('MATERIAL-LIST EXCLUDE'):
            stats['mlist'] += 1
            continue
        if BAD_VALVE_CODE in ln:
            ln = ln.replace(BAD_VALVE_CODE, GOOD_VALVE_CODE)
            stats['valve_code'] += 1
        out.append(ln)
    return out

# ---- pase 2a: emparejar todos los stub-ends antes de emitir ----
merged_by_stub = {}
for b in body:
    if keyword(b) == 'LAPJOINT-STUBEND':
        merged = merge_stubend(b)
        if merged is not None:
            merged_by_stub[id(b)] = merged
        else:
            print('AVISO: stub-end sin brida pareja en', endpoints(b)[0]['coords'])

# ---- pase 2b: reconstruir ----
result = []
for b in body:
    kw = keyword(b)
    if kw.startswith('END-POSITION'):
        stats['end_position'] += 1
        continue
    if kw == 'INSTRUMENT-DIAL':
        stats['instr_dial'] += 1
        continue
    if kw == 'INSTRUMENT' and len(endpoints(b)) < 2:
        stats['instr_zero'] += 1
        continue
    if kw == 'FLANGE' and id(b) in consumed:
        continue
    if kw == 'LAPJOINT-STUBEND':
        if id(b) in merged_by_stub:
            result.append(merged_by_stub[id(b)])
        else:
            # sin pareja: degradar a PIPE para no dejar keyword desconocida
            nb = ['PIPE'] + [re.sub(r'(LAP|BW)\s*$', '', ln) if EP_RE.match(ln) else ln
                             for ln in b[1:] if 'SKEY' not in ln]
            result.append(clean_lines(nb))
        continue
    result.append(clean_lines(b))

# los FLANGE consumidos que quedaron antes de su stub-end ya se saltaron arriba;
# verificar que ninguno quedo sin absorber
leftover = [c for c, fl_list in flange_by_coord.items()
            for f in fl_list if id(f) not in consumed]
if leftover:
    print('AVISO: bridas de longitud cero sin fusionar en:', leftover)

for b in tail:
    result.append(clean_lines(b))

out_lines = [ln for b in result for ln in b]
out_text = nl.join(out_lines) + nl * max(trailing_empty, 1)

bak = SRC.replace('.pcf', ' - ORIGINAL PLANT3D.pcf')
shutil.copyfile(SRC, bak)
open(SRC, 'wb').write(out_text.encode('latin-1'))

print('Backup :', bak)
print('Escrito:', SRC)
for k, v in stats.items():
    print(f'  {k}: {v}')
