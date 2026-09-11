---
name: memoria
description: Actualiza la bóveda Obsidian (boveda/) — memoria persistente del proyecto P2603 — tras completar tareas, tomar decisiones, resolver errores o antes de cerrar la sesión. Mantiene sincronizados contexto.md y task/todo.md.
type: prompt
whenToUse: Al completar una tarea, tomar una decisión de diseño, resolver un error recurrente, o cuando el usuario pida guardar contexto/memoria o vaya a cerrar la sesión
---

Actualiza la memoria persistente del proyecto. Reglas:

1. **Qué va dónde**:
   - Estado, tabla verdad, archivos clave → `contexto.md` (formato y límite de 300 líneas definidos en `AGENTS.md`, sección cierre_de_sesion).
   - Planes, tareas y revisiones por tarea → `task/todo.md` (estructura de `AGENTS.md` fase_1/verificacion_final).
   - Decisiones de diseño y errores resueltos → `boveda/30-Decisiones/Decisiones y lecciones.md`.
   - Datos de una línea (resultado, peculiaridades, informe) → `boveda/20-Lineas/SIM-0XX.md` y la tabla de `boveda/20-Lineas/Resumen de líneas.md`.
   - Pendientes nuevos o completados → `boveda/60-Pendientes/Pendientes y bloqueos.md`.
   - Resumen de la sesión (fecha, qué se hizo, dónde quedó, próximo paso) → nueva entrada en `boveda/50-Sesiones/Log de sesiones.md`.
2. **Ediciones mínimas**: actualiza solo las notas afectadas; no reescribas notas completas ni dupliques información (cada dato vive en UNA nota; el resto enlaza con `[[wikilinks]]`).
3. **Fechas**: usa la fecha real del sistema (`date`), no la del arranque de sesión.
4. **Sincronía**: si un cambio afecta tanto `contexto.md` como la bóveda (típico: estado actual, pendientes), actualiza ambos en la misma pasada.
5. Mantén el español y las convenciones de `AGENTS.md` (trazabilidad, sin inventar valores).
6. Al terminar, confirma al usuario en 2-3 líneas qué notas se actualizaron.

$ARGUMENTS
