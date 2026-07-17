#!/usr/bin/env python3
"""
Parser CAESAR II .md → JSON
Extrae resultados de análisis de flexibilidad desde archivos Markdown
exportados de CAESAR II 2019 y genera JSON estructurado para el dashboard.

También copia isométricos y reportes .md a dashboard/assets/ para que el
dashboard sea autocontenido (rutas relativas a dashboard/).

Uso: python scripts/parse_caesar_md.py
"""

import re
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class CaesarParser:
    """Parser de archivos .md de CAESAR II"""

    # Regex patterns para detectar secciones
    HEADER_PATTERN = re.compile(r'CAESAR II 2019.*Date: (\w+) (\d+), (\d+)')
    JOB_PATTERN = re.compile(r'Job Name: (P2603-PR-PL-(?:SIM-)?\d+)')
    REPORT_PATTERN = re.compile(r'([A-Z][A-Z\.0-9 ]+) REPORT: (.+)')
    CASE_PATTERN = re.compile(r'CASE\s+\d+\s*\(([\w-]+)\)')

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.data = {
            'ultima_actualizacion': datetime.now().strftime('%Y-%m-%d'),
            'total_lineas': 0,
            'lineas': []
        }

    def find_md_files(self) -> List[Path]:
        """Encuentra todos los archivos .md de análisis en subcarpetas (sin duplicados)"""
        md_files = set()
        for pattern in ['P2603-PR-PL-SIM-*.md', 'P2603-PR-PL-*.md']:
            md_files.update(self.root_dir.glob(f'*/{pattern}'))
        return sorted(md_files)

    def parse_date(self, match) -> str:
        """Extrae fecha del header de CAESAR II"""
        if not match:
            return datetime.now().strftime('%Y-%m-%d')
        month, day, year = match.groups()
        month_map = {
            'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
            'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
            'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
        }
        return f'{year}-{month_map.get(month[:3].upper(), "01")}-{day.zfill(2)}'

    def extract_job_name(self, content: str) -> str:
        """Extrae el nombre del job (P2603-PR-PL-SIM-XXX o P2603-PR-PL-XXX)"""
        match = self.JOB_PATTERN.search(content)
        return match.group(1) if match else "UNKNOWN"

    def extract_linea_id(self, job_name: str) -> str:
        """Deriva el id SIM-XXX desde los dígitos finales del job name"""
        match = re.search(r'(\d+)\s*$', job_name)
        return f'SIM-{match.group(1)}' if match else job_name

    def extract_fecha(self, content: str) -> str:
        """Extrae fecha del análisis"""
        match = self.HEADER_PATTERN.search(content)
        return self.parse_date(match)

    def parse_compliance_section(self, lines: List[str]) -> Dict[str, Any]:
        """Parsea sección CODE COMPLIANCE REPORT (resumen global al final del .md)"""
        compliance = {
            'passed': False,
            'max_ratio_pct': 0.0,
            'max_node': 0,
            'loadcase': '',
            'code_stress_kpa': 0.0,
            'allowable_kpa': 0.0,
            'elements': []
        }

        # Buscar "CODE COMPLIANCE EVALUATION PASSED"
        for line in lines:
            if 'PASSED' in line:
                compliance['passed'] = True
                break
            elif 'FAILED' in line:
                compliance['passed'] = False
                break

        # Extraer "Highest Stresses" y "Ratio (%)"
        in_highest = False
        lines_since_highest = 0
        for line in lines:
            if 'Highest Stresses:' in line:
                in_highest = True
                lines_since_highest = 0
                continue

            if in_highest:
                lines_since_highest += 1
                # Buscar Ratio (%): XXX.X @Node XXX  LOADCASE: N (TYPE) ...
                ratio_match = re.search(r'Ratio\s*\(%\):\s*([\d.]+)\s+@Node\s+(\d+)', line)
                if ratio_match:
                    compliance['max_ratio_pct'] = float(ratio_match.group(1))
                    compliance['max_node'] = int(ratio_match.group(2))
                    loadcase_match = re.search(r'LOADCASE:\s*(.+?)\s*$', line)
                    if loadcase_match:
                        compliance['loadcase'] = loadcase_match.group(1)

                # Buscar Code Stress y Allowable
                stress_match = re.search(r'Code Stress:\s+([\d.]+)', line)
                if stress_match:
                    compliance['code_stress_kpa'] = float(stress_match.group(1))

                allowable_match = re.search(r'Allowable Stress:\s+([\d.]+)', line)
                if allowable_match:
                    compliance['allowable_kpa'] = float(allowable_match.group(1))

                # Salir después de unas líneas
                if lines_since_highest > 8:
                    break

        return compliance

    def parse_displacements_section(self, lines: List[str]) -> Optional[Dict[str, Any]]:
        """Parsea una sección DISPLACEMENTS REPORT (un caso de carga por sección)"""
        load_case = None
        for line in lines:
            case_match = self.CASE_PATTERN.search(line)
            if case_match:
                load_case = case_match.group(1).lower()
                break

        if not load_case:
            return None

        # Extraer desplazamientos nodales: Node DX DY DZ RX RY RZ
        nodes = []
        for line in lines:
            node_match = re.match(
                r'^\s*(\d+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)'
                r'\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)', line)
            if node_match:
                nodes.append({
                    'node': int(node_match.group(1)),
                    'dx': float(node_match.group(2)),
                    'dy': float(node_match.group(3)),
                    'dz': float(node_match.group(4)),
                    'rx': float(node_match.group(5)),
                    'ry': float(node_match.group(6)),
                    'rz': float(node_match.group(7))
                })

        return {'case': load_case, 'nodes': nodes}

    def parse_restraints_section(self, lines: List[str]) -> Optional[Dict[str, Any]]:
        """Parsea una sección RESTRAINTS REPORT (un caso de carga por sección)"""
        load_case = None
        for line in lines:
            case_match = self.CASE_PATTERN.search(line)
            if case_match:
                load_case = case_match.group(1).lower()
                break

        if not load_case:
            return None

        # Extraer cargas en soportes: Node FX FY FZ MX MY MZ [tab] TYPE=...
        nodes = []
        for line in lines:
            node_match = re.match(
                r'^\s*(\d+)\s+(-?[\d.]+|N/A)\s+(-?[\d.]+|N/A)\s+(-?[\d.]+|N/A)'
                r'\s+(-?[\d.]+|N/A)\s+(-?[\d.]+|N/A)\s+(-?[\d.]+|N/A)', line)
            if node_match:
                def val(g):
                    s = node_match.group(g)
                    return 0.0 if s == 'N/A' else float(s)

                type_match = re.search(r'(TYPE=.+)$', line)
                nodes.append({
                    'node': int(node_match.group(1)),
                    'fx': val(2), 'fy': val(3), 'fz': val(4),
                    'mx': val(5), 'my': val(6), 'mz': val(7),
                    'type': type_match.group(1).rstrip(';') if type_match else ''
                })

        return {'case': load_case, 'nodes': nodes}

    def parse_stresses_section(self, lines: List[str]) -> Optional[Dict[str, Any]]:
        """Parsea una sección B31.3 STRESSES REPORT (un caso de carga por sección)"""
        load_case = None
        for line in lines:
            case_match = self.CASE_PATTERN.search(line)
            if case_match:
                load_case = case_match.group(1).lower()
                break

        # Buscar Highest Stresses → Bending máximo del caso
        max_bending = 0.0
        max_node = 0
        for line in lines:
            bending_match = re.search(r'Bending\s+([\d.]+)\s+@Node\s+(\d+)', line)
            if bending_match:
                bending = float(bending_match.group(1))
                if bending > max_bending:
                    max_bending = bending
                    max_node = int(bending_match.group(2))

        return {'case': load_case, 'max_bending': max_bending, 'max_node': max_node}

    def split_into_sections(self, content: str) -> Dict[str, List[List[str]]]:
        """Divide el contenido en secciones según CAESAR II REPORT headers.

        Devuelve un dict tipo_reporte → lista de secciones (cada página/caso
        de carga genera una sección). Las líneas vacías (incl. las generadas
        por saltos de línea mixtos \r\r\n) se descartan.
        """
        sections: Dict[str, List[List[str]]] = {}
        lines = [line for line in content.split('\n') if line.strip()]

        current_section = None
        current_content: List[str] = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Detectar inicio de bloque CAESAR II (línea con "CAESAR II" + "Date:")
            if 'CAESAR II' in line and 'Date:' in line:
                # Buscar la línea REPORT en las siguientes líneas (Job/Licensed/...)
                report_match = None
                j = i + 1
                while j < min(i + 6, len(lines)):
                    report_match = self.REPORT_PATTERN.search(lines[j])
                    if report_match:
                        break
                    j += 1

                if report_match:
                    # Guardar sección anterior si existe
                    if current_section and current_content:
                        sections.setdefault(current_section, []).append(current_content)

                    current_section = report_match.group(1).strip()
                    current_content = lines[i:j + 1]
                    i = j + 1
                    continue
            elif current_section:
                current_content.append(line)

            i += 1

        # Guardar última sección
        if current_section and current_content:
            sections.setdefault(current_section, []).append(current_content)

        return sections

    def copy_assets(self, md_path: Path, job_name: str, iso_src: Optional[Path],
                    graficos_src: Optional[Path] = None,
                    linea_id: str = '') -> Dict[str, Optional[str]]:
        """Copia isométrico, resultados gráficos y .md a dashboard/assets/ y devuelve rutas relativas"""
        iso_rel = None
        md_rel = None
        graf_rel = None

        if iso_src:
            iso_dir = self.root_dir / 'dashboard' / 'assets' / 'iso'
            iso_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(iso_src, iso_dir / iso_src.name)
            iso_rel = f'assets/iso/{iso_src.name}'

        if graficos_src and linea_id:
            graf_dir = self.root_dir / 'dashboard' / 'assets' / 'graficos'
            graf_dir.mkdir(parents=True, exist_ok=True)
            graf_name = f'{linea_id}{graficos_src.suffix.lower()}'
            shutil.copy2(graficos_src, graf_dir / graf_name)
            graf_rel = f'assets/graficos/{graf_name}'

        if job_name != 'UNKNOWN':
            md_dir = self.root_dir / 'dashboard' / 'assets' / 'md'
            md_dir.mkdir(parents=True, exist_ok=True)
            md_name = f'{job_name}.md'
            shutil.copy2(md_path, md_dir / md_name)
            md_rel = f'assets/md/{md_name}'

        return {'isometrico': iso_rel, 'reporte_md': md_rel, 'resultados_graficos': graf_rel}

    def copy_logo(self):
        """Copia el logo DML (logo1.png en la raíz del proyecto) a dashboard/assets/"""
        logo_src = self.root_dir / 'logo1.png'
        if logo_src.exists():
            assets_dir = self.root_dir / 'dashboard' / 'assets'
            assets_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(logo_src, assets_dir / 'logo.png')

    def parse_md_file(self, md_path: Path) -> Optional[Dict[str, Any]]:
        """Parsea un archivo .md individual"""
        try:
            # newline='' + normalización explícita: los .md de CAESAR mezclan
            # \r\n y \r sueltos; sin esto split('\n') deja \r colgados
            with open(md_path, 'r', encoding='utf-8', errors='ignore', newline='') as f:
                content = f.read().replace('\r\n', '\n').replace('\r', '\n')

            # Extraer información básica
            job_name = self.extract_job_name(content)
            fecha = self.extract_fecha(content)
            carpeta = md_path.parent.name

            # Buscar isométrico correspondiente (excluir ResultadosGraficos,
            # que son salidas gráficas de CAESAR, no el isométrico de Plant 3D)
            iso_src = None
            for ext in ['*.png', '*.jpeg', '*.jpg']:
                iso_files = [f for f in md_path.parent.glob(ext)
                             if not f.name.startswith('ResultadosGraficos')]
                if iso_files:
                    iso_src = iso_files[0]
                    break

            # Buscar resultados gráficos exportados de CAESAR (si existen)
            graficos_src = None
            graf_files = [f for f in sorted(md_path.parent.glob('ResultadosGraficos*'))
                          if f.suffix.lower() in ('.png', '.jpg', '.jpeg')]
            if graf_files:
                graficos_src = graf_files[0]

            linea_id = self.extract_linea_id(job_name)

            # Copiar assets al dashboard
            assets = self.copy_assets(md_path, job_name, iso_src, graficos_src, linea_id)

            # Dividir en secciones
            sections = self.split_into_sections(content)

            # Parsear cada sección
            linea_data = {
                'id': linea_id,
                'job_name': job_name,
                'nombre': carpeta,
                'carpeta': carpeta,
                'isometrico': assets['isometrico'],
                'reporte_md': assets['reporte_md'],
                'resultados_graficos': assets['resultados_graficos'],
                'fecha_analisis': fecha,
                'compliance': {},
                'displacements': {'load_cases': {}},
                'restraints': {'load_cases': {}, 'total_restraints': 0},
                'stresses': {'max_stress': 0.0, 'max_node': 0, 'max_case': ''}
            }

            for section_name, section_list in sections.items():
                if 'CODE COMPLIANCE' in section_name:
                    # El último CODE COMPLIANCE REPORT es el resumen global
                    linea_data['compliance'] = self.parse_compliance_section(section_list[-1])

                elif 'DISPLACEMENTS' in section_name:
                    cases = linea_data['displacements']['load_cases']
                    for sec_lines in section_list:
                        parsed = self.parse_displacements_section(sec_lines)
                        if parsed and parsed['nodes']:
                            case = parsed['case']
                            entry = cases.setdefault(case, {
                                'nodes': [], 'max_dx': 0.0, 'max_dy': 0.0, 'max_dz': 0.0
                            })
                            entry['nodes'].extend(parsed['nodes'])
                            for n in parsed['nodes']:
                                entry['max_dx'] = max(entry['max_dx'], abs(n['dx']))
                                entry['max_dy'] = max(entry['max_dy'], abs(n['dy']))
                                entry['max_dz'] = max(entry['max_dz'], abs(n['dz']))

                elif 'RESTRAINTS' in section_name:
                    cases = linea_data['restraints']['load_cases']
                    for sec_lines in section_list:
                        parsed = self.parse_restraints_section(sec_lines)
                        if parsed and parsed['nodes']:
                            case = parsed['case']
                            entry = cases.setdefault(case, {'nodes': []})
                            entry['nodes'].extend(parsed['nodes'])
                            linea_data['restraints']['total_restraints'] += len(parsed['nodes'])

                elif 'STRESSES' in section_name:
                    for sec_lines in section_list:
                        parsed = self.parse_stresses_section(sec_lines)
                        if parsed and parsed['max_bending'] > linea_data['stresses']['max_stress']:
                            linea_data['stresses']['max_stress'] = parsed['max_bending']
                            linea_data['stresses']['max_node'] = parsed['max_node']
                            linea_data['stresses']['max_case'] = parsed['case'] or ''

            return linea_data

        except Exception as e:
            print(f"Error parseando {md_path}: {e}")
            return None

    def parse_all(self) -> Dict[str, Any]:
        """Parsea todos los archivos .md encontrados"""
        md_files = self.find_md_files()

        for md_path in md_files:
            print(f"Parseando: {md_path}")
            linea_data = self.parse_md_file(md_path)
            if linea_data:
                self.data['lineas'].append(linea_data)

        self.data['total_lineas'] = len(self.data['lineas'])

        # Logo DML (asset global del dashboard)
        self.copy_logo()

        return self.data

    def save_json(self, output_path: str):
        """Guarda los datos parseados en formato JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        print(f"JSON guardado en: {output_path}")


def main():
    """Función principal"""
    # Directorio raíz del proyecto
    root_dir = Path(__file__).parent.parent

    # Crear parser y procesar
    parser = CaesarParser(root_dir)
    data = parser.parse_all()

    # Guardar JSON
    output_dir = root_dir / 'dashboard' / '_data'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'lineas.json'

    parser.save_json(str(output_path))

    # Resumen
    print(f"\n{'='*50}")
    print(f"Total líneas procesadas: {data['total_lineas']}")
    print(f"Última actualización: {data['ultima_actualizacion']}")
    print(f"{'='*50}")


if __name__ == '__main__':
    main()
