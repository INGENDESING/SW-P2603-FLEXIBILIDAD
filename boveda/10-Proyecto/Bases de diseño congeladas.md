# Bases de diseño congeladas

Valores acordados que **NO deben revisarse ni re-derivarse**. Citarlos tal cual en informes y análisis.

## Normativa y material

- **Norma de análisis**: ASME B31.3-2016 (ed. Jan 31, 2017)
- **Material**: ASTM A312 TP 304L, Sch 10S, sin corrosión (CA = 0)
- **Esfuerzos básicos**: Sc = Sh = 16.7 ksi (115.1 MPa) para TP304L (Tabla A-1)

## Condiciones de operación

- Presión máxima: 180 psig = 12.41 bar g = 1241 kPa g
- Temperatura operación: 90 °C (ΔT = 65 °C vs instalación 25 °C)
- Fluido: agua (SG = 1.0, densidad 1000 kg/m³ = 0.001 kg/cm³)

## Casos de carga

- OPE = W+T1+P1 · SUS = W+P1 · EXP = OPE−SUS
- Distribución típica por línea: 2 OPE, 2 Alt-SUS, 2 SUS, 3 EXP (verificar en el `.md` de cada línea, no asumir)

## Verificaciones numéricas hechas en el piloto SIM-012 (no repetir)

- SE = √(Sb² + 4St²) **sin /2** — B31.3-2016 párr. 319.4.4 ec. 17. Confirmado: √(91345² + 4×7838.1²) ≈ 92 680 + axial = 92 844.5 kPa = Code de CAESAR @130.
- CAESAR usa la forma liberal SA = f[1.25(Sc+Sh) − SL] (ec. 1b, párr. 302.3.5(d)): 1.25×(16.7+16.7) ksi − SL ≈ 41.6 ksi = 286 952.5 kPa = Allowable reportado.
- SL en 302.3.5(c) evaluado por 320.2; f en Tabla 302.3.5 (1.0 hasta 7000 ciclos).
