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
chat-web/          # Widget embebido (popup)
```

## Herramientas

- `execute_command` - Gmail/Calendar via GOG CLI
- `get_weather` - Clima actual
- `search_web` - Búsqueda en tiempo real
- `get_time` - Fechas y zonas horarias

## Setup

### Requisitos Previos
- Python 3.10+ con entorno virtual (`venv`)

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
python main.py dev
```

### GOG (Gmail/Calendar)

Para activar o renovar el token:

```bash
./bin/gogcli/gog auth add you@gmail.com --services gmail,calendar
```

## chat-web (widget embebido)

```bash
cd chat-web
npm install
npm run dev
```

Abre `http://localhost:3000` y conecta el widget.

## Documentación

- [SPEC.md](./SPEC.md) - Especificación técnica
- [AGENTS.md](./AGENTS.md) - Instrucciones para agentes
- [MEMORIA.md](./MEMORIA.md) - Estado del proyecto
- [CHANGELOG.md](./CHANGELOG.md) - Registro de cambios
