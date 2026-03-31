# MEMORIA.md - OpenNemesis-Live

## Estado del Proyecto
Asistente de voz multimodal basado en LiveKit.

## Arquitectura

### Componentes
- **livekit_agent/agent.py**: Agente de voz con Gemini Realtime
- **data/db.py**: Persistencia SQLite para historial
- **tools/tools.py**: Herramientas del agente
- **skills/loader.py**: Sistema de skills GOG
- **main.py**: Entry point
- **livekit_agent/status.py**: Verificación de servicios
- **frontend/**: Cliente web Next.js basado en agent-starter-embed

### Stack Tecnológico
- Python 3.10+ con venv
- LiveKit Agents SDK
- Google Gemini (gemini-2.5-flash-native-audio-latest)
- SQLite (aiosqlite)
- GOG CLI para Google Workspace
- Next.js 15 (Frontend)

## Herramientas Disponibles

El agente dispone de 4 tools:

| Tool | Descripción |
|------|-------------|
| weather | Consulta el clima de una ciudad |
| time | Obtiene la hora y fecha actual |
| search | Búsqueda web con DuckDuckGo |
| command | Ejecuta comandos GOG (Gmail, Calendar) |

## Integración GOG

- **Autenticación**: Completada con `gog login fontflorida1093@gmail.com --services=gmail,calendar`
- **Servicios activos**: Gmail, Calendar
- **Binario**: `bin/gogcli/gog` con permisos de ejecución
- **Configuración**: GOGCLI_PATH en .env.local

## Servicios

| Servicio | Estado |
|----------|--------|
| LiveKit Cloud | ✅ Conectado |
| Gemini | ✅ Configurado |
| Tools (4) | ✅ Disponibles |
| GOG | ✅ Autenticado |
| Frontend | ✅ Configurado (Next.js) |

## Documentación
- SPEC.md: Especificaciones del proyecto
- AGENTS.md: Guías para agentes AI
- MEMORIA.md: Estado actual
- CHANGELOG.md: Registro de cambios

## Próximos Pasos

1. Desplegar en Vercel
2. Probar integración frontend + agente
3. Configurar dominio personalizado (opcional)

