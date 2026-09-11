# Inicializar proyecto

**Para el usuario**: en cada sesión nueva escribe simplemente:

```
ejecuta inicializa
```

y el agente cargará todo el contexto del proyecto desde la bóveda de memoria (`boveda/`).

---

**Para el agente**: cuando el usuario diga «ejecuta inicializa», «inicializa», «carga el proyecto» o similar, invoca la skill `inicializar` (`.kimi-code/skills/inicializar/SKILL.md`) y sigue su protocolo de carga. Si la skill no estuviera disponible, lee directamente en este orden:

1. `boveda/00-Inicio.md` — mapa de la bóveda
2. `boveda/60-Pendientes/Pendientes y bloqueos.md` — qué sigue
3. `boveda/20-Lineas/Resumen de líneas.md` — tabla verdad CAESAR (8 líneas, todas PASSED)
4. `boveda/50-Sesiones/Log de sesiones.md` — historial y dónde quedó el trabajo
5. `contexto.md` — estado detallado del proyecto
6. `AGENTS.md` — rol y estándares de entregables (si no está ya cargado)

Después reporta: estado global, última tarea, pendientes y próximo paso propuesto. Espera aprobación antes de ejecutar trabajo del backlog.

**Al cerrar la sesión** (o cuando el usuario pida «guarda el contexto/memoria»): invoca la skill `memoria` para actualizar la bóveda, `contexto.md` y `task/todo.md`.
