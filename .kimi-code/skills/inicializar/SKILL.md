---
name: inicializar
description: Carga el contexto completo del proyecto P2603 SW-K60 desde la bóveda Obsidian (boveda/) al inicio de una sesión. Usar cuando el usuario dice "ejecuta inicializa", "inicializa", "carga el proyecto" o arranca una sesión nueva en este repositorio.
type: prompt
whenToUse: Cuando el usuario pida inicializar/cargar el contexto del proyecto, diga "ejecuta inicializa", o comience una sesión nueva en este repositorio
---

Inicializa la sesión cargando la memoria persistente del proyecto. Sigue el protocolo de carga de `boveda/50-Sesiones/Log de sesiones.md`:

1. Lee en orden (usa Read, varias en paralelo):
   - `boveda/00-Inicio.md`
   - `boveda/60-Pendientes/Pendientes y bloqueos.md`
   - `boveda/20-Lineas/Resumen de líneas.md`
   - `boveda/50-Sesiones/Log de sesiones.md`
   - `contexto.md`
   - `task/todo.md` (solo si la tarea a retomar lo requiere; es largo)
2. NO releas las carpetas de líneas ni el dashboard salvo que la tarea lo pida — la tabla verdad de `Resumen de líneas.md` es suficiente.
3. Reporta al usuario en español, en máximo 8 líneas:
   - Estado global del proyecto (líneas PASSED, dashboard, informes)
   - Última tarea completada y fecha
   - Pendientes (separa: esperan al usuario / trabajo del agente)
   - Próximo paso propuesto
4. Queda a la espera de instrucciones. No ejecutes trabajo del backlog sin aprobación (regla de `AGENTS.md`: fase 1 análisis → aprobación → fase 2 ejecución).

Recuerda las reglas del proyecto: los `.md` de CAESAR son la fuente de verdad numérica; nunca pintar FAILED por datos faltantes; sin viñetas en entregables cliente; no mutar git sin confirmación explícita.
