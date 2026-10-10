# Metodología de Evaluación de Uniones Bridadas y Cargas en Boquillas

Documento metodológico de referencia para el análisis de estanqueidad en uniones bridadas estándar y verificación de esfuerzos en conexiones a equipos, aplicable a las líneas del proyecto P2603 SW-K60 (iniciado para carpeta 16.0 / PCF-301 y proyectado a carpeta 17.0 / PCF-302 y subsecuentes).

---

## 1. Evaluación de Uniones Bridadas (Estanqueidad contra Fuga)

### 1.1 Método Empleado
Se adopta el **Método de Presión Equivalente de Kellogg** (*Kellogg Equivalent Pressure Method*), implementado en CAESAR II 2019 mediante la opción $P_{eq}$ del módulo *Flange Check*. 

Este procedimiento constituye la práctica estándar en la industria para verificar la integridad contra fuga de bridas normalizadas según **ASME B16.5** sujetas a solicitaciones mecánicas externas (momentos flectores y fuerzas axiales inducidas por la flexibilidad de la tubería), en instalaciones gobernadas por **ASME B31.3**. Dado que el código ASME B31.3 no prescribe una formulación analítica mandatoria para la verificación de fuga en bridas estándar, se adopta este método de ingeniería ampliamente reconocido, conceptualmente análogo al método de la norma ASME Boiler and Pressure Vessel Code (BPVC) Sección III, Subsección NC, numeral NC-3658.3.

### 1.2 Formulación Matemática
Las cargas mecánicas externas actuantes sobre la interfaz bridada —momento flector resultante $M$ y fuerza axial neta $F$, calculadas en el caso operativo de flexibilidad— se transforman en una sobrepresión estática equivalente ($P_{eq}$) que se superpone a la presión interna de diseño:

$$P_{eq} = \frac{16 M}{\pi G^3} + \frac{4 F}{\pi G^2}$$

$$P_{total} = P_D + P_{eq} \le P_{rating}(T_{op})$$

Donde:
* $M$: Momento flector resultante en el plano de la junta bridada: $M = \sqrt{M_y^2 + M_z^2}$ $[\text{N}\cdot\text{m}]$.
* $F$: Fuerza axial neta perpendicular a la cara de la brida (tracción positiva) $[\text{N}]$.
* $G$: Diámetro de reacción efectivo del empaque (diámetro medio de contacto según ASME B16.20 / ASME B16.21) $[\text{m}]$.
* $P_D$: Presión de operación o diseño interior simultánea del sistema $[\text{kPa}]$.
* $P_{eq}$: Presión interna equivalente inducida por las solicitaciones externas $[\text{kPa}]$.
* $P_{total}$: Presión efectiva total sobre la unión bridada $[\text{kPa}]$.
* $P_{rating}(T_{op})$: Presión máxima admisible de la brida según las tablas de presión-temperatura de **ASME B16.5** para la clase y grupo de material correspondiente, evaluada a la temperatura de operación $T_{op}$ $[\text{kPa}]$.

### 1.3 Criterio de Aceptación
El índice de utilización o ratio de presión equivalente se define como:

$$\text{Ratio} = \frac{P_D + P_{eq}}{P_{rating}(T_{op})} \times 100\%$$

* **Criterio de aprobación:** $\text{Ratio} < 100.0\%$.
* **Criterio de no conformidad:** $\text{Ratio} \ge 100.0\%$, lo cual señala riesgo de pérdida de estanqueidad (fuga de fluido por relajación de apriete o separación de caras). Ante esta condición se exige rediseñar el trazado (mayor flexibilidad), incorporar soportes adicionales para mitigar el momento externo actuante, o incrementar la clase nominal de la brida (p. ej., de Clase 150 a Clase 300).

---

## 2. Parámetros de Entrada para Modelado

### 2.1 Datos Típicos de Línea Base (Caso PCF-301, extensible a PCF-302 / 17.0)

| Parámetro | Valor de Entrada | Referencia / Observaciones |
| :--- | :--- | :--- |
| **Brida** | NPS 6" (DN 150), Clase 150 | ASME B16.5, tipo Lap Joint (o Slip-On según isométrico) |
| **Material de brida** | ASTM A182 Gr F304L | Grupo 2.2 según ASME B16.5 (coherente con A312 TP304L) |
| **Diámetro empaque ($G$)** | $193\ \text{a}\ 196\ \text{mm}$ | Diámetro medio de contacto según tabla B16.5 en CAESAR II |
| **Caso de carga evaluado** | L3: W+T2+P2 | Caso de operación térmica y mecánica continua (OPE) |
| **Temperatura ($T_2$)** | $90\ \text{°C}$ | Temperatura de diseño de la línea |
| **Presión interna ($P_2$)** | $1241\ \text{kPa g}$ ($180\ \text{psig}$) | Presión de diseño del sistema (bases congeladas) |
| **Presión admisible $P_{rating}$**| Interpolada a $90\ \text{°C}$ | Tabla 2-2.2 de ASME B16.5 para material Grupo 2.2 |

---

## 3. Alcance y Limitaciones Metodológicas

1. **Aplicabilidad exclusiva a bridas de tubería estándar:** Este método aplica estrictamente a bridas normalizadas bajo estándar ASME B16.5 (o ASME B16.47) con empaquetaduras y pernos de resistencia estándar dimensionados bajo norma. No es aplicable a bridas no estándar diseñadas bajo ASME BPVC Sección VIII División 1 Apéndice 2, ni a conexiones propietarias.
2. **Exclusión de boquillas de equipos mecánicos:** Las bridas de conexión a boquillas de bombas centrífugas u otros equipos rotativos/estáticos (p. ej. boquilla de descarga de bomba en nodo 250) **no se evalúan mediante este método**. Su límite admisible está gobernado por las cargas admisibles en boquillas de equipo según **API 610** (o normas de fabricante), las cuales se evalúan de forma independiente mediante el módulo *Equipment Limits* de CAESAR II.
3. **Mecanismo evaluado (Fuga vs. Resistencia estructural):** El método de Kellogg evalúa el riesgo de pérdida de estanqueidad hidráulica (fuga interfacial). No cuantifica la deformación plástica del cuello de la brida ni el estado tensional detallado del perno. Para evaluaciones de alta severidad que exijan verificación analítica de la sección del perno se reservaría el método ASME Sección III NC-3658.3 con área de pernos, no requerido para las condiciones de este proyecto.
4. **Sensibilidad de las cargas externas:** Las reacciones mecánicas $M$ y $F$ dependen directamente del peso propio modelado para los accesorios en línea (válvulas de guillotina, válvulas de retención) y de la densidad de fluido considerada ($1000\ \text{kg/m}^3$).

---

## 4. Criterios de Par Técnico y Trazabilidad

1. **Margen operativo y declaración en informe:**
   * Si el ratio resultante bajo el caso crítico de operación ($L_3$) se ubica holgadamente por debajo del límite ($\text{Ratio} < 50\%$), se cita el cumplimiento pleno del método sin notas especiales.
   * Si el ratio calculado se sitúa en una banda exigente ($90\% \le \text{Ratio} < 100\%$), se debe declarar explícitamente en el cuerpo del informe técnico el margen residual de seguridad disponible.
2. **Trazabilidad de componentes de catálogo:**
   * Si el peso de un accesorio (por ejemplo, válvula de guillotina con peso de base de datos de CAESAR II de $787\ \text{N}$) corresponde a un valor genérico por defecto, la nota *"peso genérico pendiente de confirmación contra ficha técnica de fabricante"* **debe mantenerse visible en las memorias e informes** hasta disponer formalmente del catálogo del proveedor. La preservación de este supuesto constituye rigor y trazabilidad de ingeniería, no debilidad documental.
