# OpenNemesis-Live

Asistente personal de voz multimodal con LiveKit + Gemini, orientado a productividad personal (voz, chat, Gmail/Calendar y Obsidian).

## Estado actual

- Backend desacoplado en `backend/` con entrypoint oficial `python backend/main.py dev`
- Dos clientes web separados:
  - `chat-web/` -> widget embebido tipo popup
  - `chat-web-full/` -> cliente full-page
- Memoria híbrida activa:
  - Historial en SQLite
  - Memoria curada en Markdown (`SOUL.md`, `RULES.md`, `USER.md`, `MEMORY.md`)
- API opcional de observabilidad en `backend/api.py` (`/health`, `/status`)

## Arquitectura

Cliente Web <-> LiveKit Cloud <-> Agente de Voz (Python)

- `backend/` -> orquestación del agente, tools, skills, persistencia y tests
- `backend/data/memory/` -> memoria curada personal (SOUL/RULES/USER/MEMORY)
- `chat-web/` -> interfaz embebida
- `chat-web-full/` -> interfaz completa
- `bin/gogcli/gog` -> integración CLI con Gmail/Calendar
- Obsidian local -> vault del usuario para búsqueda de notas y gestión de tareas

## Stack

- Python 3.10+
- LiveKit Agents SDK
- Gemini Realtime (`gemini-2.5-flash-native-audio-latest`)
- SQLite (`aiosqlite`)
- Next.js + React + Tailwind CSS

## Quickstart

### 1) Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

cp backend/.env.example backend/.env.local
# Edita backend/.env.local con tus credenciales

python backend/main.py dev
```

### 2) API opcional (health/status)

En otra terminal, con el mismo venv activo:

```bash
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

Endpoints:

- `GET /health` -> estado básico del proceso
- `GET /status` -> estado de `livekit`, `gemini`, `skills`, `tools`, `gog`

### 3) Frontend embebido (`chat-web`)

```bash
cd chat-web
npm install
cp .env.example .env.local
npm run dev
```

### 4) Frontend full-page (`chat-web-full`)

```bash
cd chat-web-full
npm install
cp .env.example .env.local
npm run dev
```

## Variables de entorno por servicio

- Backend: `backend/.env.local` (plantilla: `backend/.env.example`)
- Widget: `chat-web/.env.local` (plantilla: `chat-web/.env.example`)
- Full page: `chat-web-full/.env.local` (plantilla: `chat-web-full/.env.example`)

Cada servicio lee su propio `.env.local`.

## LiveKit: Cloud + Self-hosted

### Cloud (recomendado)

1. Crea cuenta en LiveKit Cloud: `https://livekit.com/`
2. Crea un proyecto en el portal.
3. Copia `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`.
4. Pega esas variables en `backend/.env.local`.
5. Arranca backend y verifica estado con `GET /status`.

Referencias:

- `https://docs.livekit.io/intro/overview/`
- `https://docs.livekit.io/agents/start/voice-ai/`
- `https://docs.livekit.io/agents/playground/` (Playground para probar el agente)

### Self-hosted (alternativa)

1. Despliega un servidor LiveKit propio.
2. Arranca el servidor LiveKit local siguiendo la guia oficial.
3. Usa la URL y credenciales de ese servidor en `backend/.env.local`.
4. Arranca el agente con `python backend/main.py dev`.
5. Verifica conectividad con `GET /status`.

Referencias:

- `https://github.com/livekit`
- `https://docs.livekit.io/transport/self-hosting/local/`

Nota: el código del agente no cambia entre Cloud y self-hosted; cambia la infraestructura (operación, TLS, red y mantenimiento).

## Tools disponibles

- `weather`, `time`, `search`
- `command` (uso principal: GOG Gmail/Calendar)
- `obsidian_get_vault`, `obsidian_set_vault`, `obsidian_search`
- `obsidian_tasks_vault`, `obsidian_tasks`, `obsidian_add`, `obsidian_complete`
- `obsidian_create_vault`, `obsidian_tasks_in_vault`

`ENABLED_SKILLS` permite activar/desactivar skills opcionales. El grupo `core` siempre está activo.

## Integración GOG (Gmail/Calendar)

1. Guarda `client_secret.json` en `backend/credentials/` (directorio local, no versionado).
2. Registra credenciales OAuth:

```bash
./bin/gogcli/gog auth credentials /path/to/client_secret.json
```

3. Autoriza la cuenta:

```bash
./bin/gogcli/gog auth add you@gmail.com --services gmail,calendar
```

## Memoria curada personal

Ruta: `backend/data/memory/`

- `SOUL.md` -> personalidad/identidad del agente
- `RULES.md` -> reglas operativas
- `USER.md` -> perfil y preferencias del usuario
- `MEMORY.md` -> resumen y continuidad de sesiones

Puedes configurar personalidad en lenguaje natural o con comando explícito:

```bash
config agente nombre=Niobe tono=profesional estilo=conciso rol=asistente personal
```

## Qué se sube y qué no

Sí se sube:

- Código fuente
- `*.env.example`
- Documentación

No se sube:

- `.env.local`, `.env`, secretos y credenciales OAuth
- `backend/credentials/`
- `node_modules/`, `.next/`, `.venv/`
- Bases locales (`*.db`)

## Comprobación rápida antes de publicar

```bash
git status
git ls-files "*.env.local" "*.env" "*.db"
git ls-files "**/node_modules/*" "**/.next/*"
```

## Documentación del proyecto

- `SPEC.md` -> especificación técnica y alcance
- `MEMORIA.md` -> estado funcional actual
- `CHANGELOG.md` -> historial de cambios
- `AGENTS.md` -> guía operativa para agentes AI

## Recursos oficiales LiveKit

- `https://livekit.com/`
- `https://github.com/livekit`
- `https://github.com/livekit`
