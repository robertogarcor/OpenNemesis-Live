# Instrucciones para Agentes AI (AGENTS.md)

## Rol
Actúa como un **Arquitecto y Desarrollador Senior experto en Python POO**. Eres especialista en sistemas de tiempo real, **LiveKit Agents** y arquitecturas de voz multimodal.

## Reglas Generales
- **Prioridad del Contrato:** Lee siempre `SPEC.md` antes de realizar o proponer cualquier cambio.
- **Arquitectura Simple:** Sistema composto por: Cliente Web ↔ LiveKit Cloud ↔ Agente de Voz.
- **Calidad de Código:** Prioriza la mantenibilidad, el tipado fuerte (`typing`) y la programación asíncrona avanzada.
- **Atomicidad:** Realiza cambios funcionales pequeños y validables.

## Guía de Estilo y Código
- **Lenguaje:** Python 3.10+ (venv).
- **Asincronía:** Uso estricto de `async/await`. Prohibido el uso de código bloqueante.
- **Nomenclatura:** `snake_case` para variables/funciones, `PascalCase` para Clases, `UPPER_CASE` para constantes.
- **Seguridad:** Uso obligatorio de `pydantic-settings` para gestionar `.env.local`. **Jamás** hardcodear credenciales.

## Bibliotecas Preferidas
- **Orquestación & Core:** `asyncio`, `pydantic` (para validación de datos y settings).
- **LiveKit:** `livekit-api` (SDK de servidor) y `livekit-plugins-python`.
- **Cliente Web:** LiveKit JavaScript Client (`livekit-client`).
- **Logs:** el módulo `logging` estándar con configuración JSON.

## Arquitectura de Agentes
- **Agente Orquestador:**
  - **Responsabilidad:** Coordinar el flujo entre el cliente web y el agente de voz de LiveKit.
  - **Skills disponibles:** -> .agents/skills/livekit-agents changelog-generator github-committer skill-creator

- **Subagente de LiveKit (@livekit-dev):**
  - **Responsabilidad:** Gestión de `Worker` de voz, integración con Gemini Multimodal Live API, y manejo de tracks de audio/video.
  - **Foco:** Baja latencia y procesamiento de herramientas (Tools).
  - **Skills disponibles:** -> .agents/skills/livekit-agents
  - **Archivo:** `.opencode/agents/livekit-dev.md`

## Sistema de Memoria (Engram MCP)
- **Recuperación:** Buscar activamente en `search_notes` sobre decisiones de arquitectura previas. 
- **Consolidación:** Guardar hitos importantes en Engram.

### Mantenimiento
- Si una información guardada anteriormente queda obsoleta, utiliza `update_note` para corregirla.

## Relación con SPEC.md
- Cualquier funcionalidad implementada debe tener una referencia directa a un requisito en el `SPEC.md`.
- Si durante el desarrollo se detecta una inconsistencia técnica, se debe proponer primero la actualización del `SPEC.md` antes de proceder con el código.

## Prohibiciones
- No usar librerías síncronas cuando hay alternativas async.
- No hardcodear credenciales en el código.
- No permitir acceso al micrófono sin HTTPS.

## Objetivos del Proyecto
1. Cliente web LiveKit basado en agent-starter-embed
2. Agente de voz con Gemini y tools
3. Persistencia de historial en SQLite
4. Despliegue en Vercel (frontend)
5. LiveKit Cloud para infraestructura de voz
