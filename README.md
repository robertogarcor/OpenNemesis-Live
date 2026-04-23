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

## Documentación

- [SPEC.md](./SPEC.md) - Especificación técnica
- [AGENTS.md](./AGENTS.md) - Instrucciones para agentes
- [MEMORIA.md](./MEMORIA.md) - Estado del proyecto
- [CHANGELOG.md](./CHANGELOG.md) - Registro de cambios
