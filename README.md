# OpenNemesis-Live

Asistente personal de voz multimodal basado en LiveKit.

## Tech Stack

- **Lenguaje:** Python >= 3.10
- **IA:** Gemini 2.5 Flash (soporte audio nativo)
- **Voz:** LiveKit Agents SDK
- **Cliente Web:** LiveKit JavaScript Client
- ** hosting:** Vercel
- **DB:** SQLite

## Estructura

```
livekit_agent/     # Agente de voz
tools/             # Herramientas disponibles
bin/               # Binarios (GOG CLI)
frontend/          # Cliente web
```

## Herramientas

- `execute_command` - Gmail/Calendar via GOG CLI
- `get_weather` - Clima actual
- `search_web` - Búsqueda en tiempo real
- `get_time` - Fechas y zonas horarias

## Setup

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables
cp .env.local.example .env.local
# Editar .env.local con tus credenciales

# Iniciar agente
python -m livekit_agent.agent
```

## Documentación

- [SPEC.md](./SPEC.md) - Especificación técnica
- [AGENTS.md](./AGENTS.md) - Instrucciones para agentes
- [MEMORIA.md](./MEMORIA.md) - Estado del proyecto
- [CHANGELOG.md](./CHANGELOG.md) - Registro de cambios
