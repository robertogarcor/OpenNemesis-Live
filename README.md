# OpenNemesis-Live

Asistente personal de voz multimodal basado en LiveKit.

## Tech Stack

- **Lenguaje:** Python >= 3.10
- **IA:** Gemini 2.5 Flash (soporte audio nativo)
- **Voz:** LiveKit Agents SDK
- **Cliente Web:** LiveKit JavaScript Client
- ** hosting:** Vercel
- **DB:** SQLite
- **Memoria curada:** Markdown personal en `backend/data/memory` (`SOUL.md`, `RULES.md`, `USER.md`, `MEMORY.md`)

## Estructura

```
backend/           # Backend LiveKit (agent, tools, data, tests)
bin/               # Binarios (GOG CLI)
chat-web/          # Widget embebido (popup)
chat-web-full/     # Cliente web completo (full page)
backend/data/memory/  # Memoria curada de largo plazo
```

## Herramientas

- `execute_command` - Gmail/Calendar via GOG CLI
- `get_weather` - Clima actual
- `search_web` - Búsqueda en tiempo real
- `get_time` - Fechas y zonas horarias
- `obsidian_search` - Buscar notas en vault local
- `obsidian_get_vault` - Ver bóveda activa
- `obsidian_set_vault` - Cambiar bóveda activa (sesión)
- `obsidian_tasks_vault` - Listar tareas de toda la bóveda
- `obsidian_tasks` - Listar tareas Markdown
- `obsidian_add` - Crear tarea en nota
- `obsidian_complete` - Completar tarea en nota
- `obsidian_create_vault` - Crear una nueva bóveda
- `obsidian_tasks_in_vault` - Listar tareas de una bóveda específica

## Setup

### Requisitos Previos
- Python 3.10+ con entorno virtual (`venv`)

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r backend/requirements.txt

# Configurar variables del backend
cp backend/.env.example backend/.env.local
# Editar backend/.env.local con tus credenciales

# Iniciar agente
python backend/main.py dev
```

### Variables por servicio (desacoplado)

- Backend: `backend/.env.local` (plantilla: `backend/.env.example`)
- chat-web: `chat-web/.env.local` (plantilla: `chat-web/.env.example`)
- chat-web-full: `chat-web-full/.env.local` (plantilla: `chat-web-full/.env.example`)

Cada servicio lee su propio `.env.local`.

### GOG (Gmail/Calendar)

Primero registra las credenciales OAuth de Google (client secret):

Guarda tu `client_secret.json` en `backend/credentials/` (o usa una ruta absoluta segura).

```bash
./bin/gogcli/gog auth credentials /path/to/client_secret.json
```

Despues autoriza la cuenta y servicios:

```bash
./bin/gogcli/gog auth add you@gmail.com --services gmail,calendar
```

Notas:

- El directorio `backend/credentials/` es local para secretos OAuth y **no se sube a Git**.
- No compartas ni subas `client_secret.json` ni tokens de acceso.

### Obsidian (vault local)

Configura el path del vault para habilitar tools de notas/tareas:

```bash
export OBSIDIAN_VAULT_PATH="$HOME/Documents/Obsidian"
export OBSIDIAN_ALLOWED_BASE_DIRS="$HOME/obsidean:$HOME/Documents"
```

### Activar/Desactivar skills

Usa `ENABLED_SKILLS` para controlar qué skills y tools opcionales están activas.

```bash
# Todas activas (por defecto): dejar vacío
export ENABLED_SKILLS=""

# Solo GOG + Obsidian
export ENABLED_SKILLS="gog,obsidian-tasks"
```

`core` (weather/time/search) permanece siempre activo.

### Seguridad (Obsidian)

- El agente no debe borrar bóvedas ni notas de Obsidian.
- Las operaciones destructivas por `execute_command` están bloqueadas por seguridad.

## chat-web (widget embebido)

```bash
cd chat-web
npm install
npm run dev
```

Abre `http://localhost:3000` y conecta el widget.

## chat-web-full (cliente web completo)

```bash
cd chat-web-full
npm install
npm run dev
```

Abre `http://localhost:3000` para usar el cliente full page (sin burbuja).

## Documentación

- [SPEC.md](./SPEC.md) - Especificación técnica
- [AGENTS.md](./AGENTS.md) - Instrucciones para agentes
- [MEMORIA.md](./MEMORIA.md) - Estado del proyecto
- [CHANGELOG.md](./CHANGELOG.md) - Registro de cambios

## Memoria curada (personal)

El agente usa memoria en `backend/data/memory/`:

- `SOUL.md` -> identidad y personalidad del agente (Name/Tone/Style/Role)
- `RULES.md` -> reglas operativas base
- `USER.md` -> perfil y preferencias del usuario
- `MEMORY.md` -> notas de sesiones y resumen de largo plazo

Puedes personalizar al agente con lenguaje natural, por ejemplo:

- `Te llamas Niobe`
- `Tu tono es agradable y profesional`
- `Responde de forma breve y tecnica`
- `Actua como mi asistente personal para correo, calendario y tareas`

Tambien puedes usar modo explicito:

```bash
config agente nombre=Niobe tono=profesional estilo=conciso rol=asistente personal
```

Si faltan campos de personalidad al iniciar, el agente te lo indicara y puedes decir `usa por defecto`.
