# MEMORIA.md - OpenNemesis-Live

## Estado del Proyecto
Asistente de voz multimodal basado en LiveKit.

## Arquitectura

### Componentes
- **livekit_agent/agent.py**: Agente de voz con Gemini Realtime
- **data/db.py**: Persistencia SQLite para historial
- **tools/tools.py**: Herramientas primarias del agente
- **tools/obsidian_tools.py**: Herramientas de Obsidian (notas y tareas)
- **skills/loader.py**: Sistema de skills
- **main.py**: Entry point
- **livekit_agent/status.py**: Verificación de servicios
- **chat-web/**: Widget embebido tipo popup (Next.js) inspirado en agent-starter-embed
- **chat-web-full/**: Cliente web completo (full page) en Next.js

### Stack Tecnológico
- Python 3.10+ con venv
- LiveKit Agents SDK
- Google Gemini (gemini-2.5-flash-native-audio-latest)
- SQLite (aiosqlite)
- GOG CLI para Google Workspace
- Next.js 15 + React (Frontend)
- Tailwind CSS v4 (chat-web y chat-web-full)

## Herramientas Disponibles

El agente dispone de 13 tools:

| Tool | Descripción |
|------|-------------|
| weather | Consulta el clima de una ciudad |
| time | Obtiene la hora y fecha actual |
| search | Búsqueda web con DuckDuckGo |
| command | Ejecuta comandos GOG (Gmail, Calendar) |
| obsidian_get_vault | Muestra bóveda activa de Obsidian |
| obsidian_set_vault | Cambia bóveda activa en runtime |
| obsidian_search | Busca notas por texto en Obsidian |
| obsidian_tasks_vault | Lista tareas de toda la bóveda activa |
| obsidian_tasks | Lista tareas en notas Markdown |
| obsidian_add | Añade tareas en notas |
| obsidian_complete | Marca tareas como completadas |
| obsidian_create_vault | Crea una nueva bóveda de Obsidian |
| obsidian_tasks_in_vault | Lista tareas de una bóveda específica |

## Integración GOG

- **Autenticación**: `./bin/gogcli/gog auth add fontflorida1093@gmail.com --services gmail,calendar`
- **Servicios activos**: Gmail, Calendar
- **Binario**: `bin/gogcli/gog` con permisos de ejecución
- **Configuración**: GOGCLI_PATH en .env.local

## Servicios

| Servicio | Estado |
|----------|--------|
| LiveKit Cloud | ✅ Conectado |
| Gemini | ✅ Configurado |
| Tools (13) | ✅ Disponibles |
| GOG | ✅ Autenticado |
| chat-web | ✅ Conectado (popup embebido) |
| chat-web-full | ✅ Cliente full page disponible |

## chat-web (Estado)

- UI estilo embed con popup, botones y tooltips
- Landing base (hero + guia rapida) para evitar pagina vacia
- Texto via DataChannel (cliente -> agente) y respuestas del agente al chat
- Fuente visual unica en UI (camara o pantalla), con miniatura activa
- Barra compacta de voz+miniatura encima del chat cuando el texto esta abierto
- Worker con timeouts ampliados para evitar AssignmentTimeout
- Contexto temporal: menciones de "hoy/ayer" en ventana 48h
- Obsidian con guardrails: sin borrado de bóvedas/notas desde el agente
- Activación selectiva de skills con `ENABLED_SKILLS`

## chat-web-full (Estado)

- Cliente completo en pantalla (sin burbuja embebida)
- Reusa token API de LiveKit (`/api/token`) y flujo de DataChannel
- Incluye controles de microfono, camara y pantalla
- Layout responsive para desktop/movil con panel de chat siempre visible

## Documentación
- SPEC.md: Especificaciones del proyecto
- AGENTS.md: Guías para agentes AI
- MEMORIA.md: Estado actual
- CHANGELOG.md: Registro de cambios

## Próximos Pasos

1. Probar chat-web-full en desktop y movil
2. Ajustes visuales finales entre cliente embebido y full page
3. Desplegar en Vercel
