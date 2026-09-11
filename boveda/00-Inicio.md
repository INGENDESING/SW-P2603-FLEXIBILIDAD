# Bóveda de memoria — ISOS ANÁLISIS FLEXIBILIDAD (P2603 SW-K60)

Mapa de contenido de la memoria persistente del proyecto. Esta bóveda sobrevive entre sesiones: cada sesión nueva arranca leyendo estas notas (ver `inicializar.md` en la raíz).

## Cómo usar esta bóveda

- **Inicio de sesión**: el usuario dice «ejecuta inicializa» → se leen las notas marcadas con ✅ en [[50-Sesiones/Log de sesiones#Protocolo de carga|Protocolo de carga]].
- **Durante la sesión**: decisiones, resultados y lecciones se registran en la nota correspondiente (skill `memoria`).
- **Cierre de sesión**: se actualiza [[50-Sesiones/Log de sesiones|Log de sesiones]] y `contexto.md`.

## Notas

### Proyecto
- [[10-Proyecto/Contexto P2603 SW-K60|Contexto P2603 SW-K60]] — qué es el proyecto, cliente, flujo de trabajo
- [[10-Proyecto/Bases de diseño congeladas|Bases de diseño congeladas]] — normativa, material, condiciones (NO revisar)

### Líneas analizadas (8/8 PASSED)
- [[20-Lineas/Resumen de líneas|Resumen de líneas]] — tabla verdad CAESAR de las 8 líneas
- Notas individuales: [[20-Lineas/SIM-002|SIM-002]] · [[20-Lineas/SIM-003|SIM-003]] · [[20-Lineas/SIM-007|SIM-007]] · [[20-Lineas/SIM-008|SIM-008]] · [[20-Lineas/SIM-009|SIM-009]] · [[20-Lineas/SIM-010|SIM-010]] · [[20-Lineas/SIM-011|SIM-011]] · [[20-Lineas/SIM-012|SIM-012]]

### Decisiones y lecciones
- [[30-Decisiones/Decisiones y lecciones|Decisiones y lecciones]] — por qué se hizo cada cosa, errores ya resueltos (no repetirlos)

### Workflows
- [[40-Workflows/Comandos y pipelines|Comandos y pipelines]] — parser, dashboard, informes LaTeX, despliegue

### Estado
- [[60-Pendientes/Pendientes y bloqueos|Pendientes y bloqueos]] — qué falta, qué espera del usuario
- [[50-Sesiones/Log de sesiones|Log de sesiones]] — historial cronológico sesión por sesión

## Archivos hermanos fuera de la bóveda

- `contexto.md` — resumen de estado (se mantiene sincronizado; formato definido en `AGENTS.md`)
- `task/todo.md` — planes y revisiones por tarea (auditoría completa)
- `generadorinf.md` — prompt maestro v1.1 para informes LaTeX
- `AGENTS.md` — rol, principios operativos y estándares de entregables
