# OpenNemesis-Live Assistant (SPEC.md)

## 1. Resumen
Asistente personal de voz multimodal basado en LiveKit. El usuario se conecta desde un cliente web (navegador) al agente de voz de LiveKit, que procesa consultas usando Gemini con herramientas integradas (clima, búsqueda, tiempo, comandos).

## 2. Tecnologías (Tech Stack)
- **Lenguaje:** Python >= 3.10
- **IA Generativa:** `gemini-2.5-flash-native-audio-latest` (o superior) con soporte para Multimodal Audio.
- **Voz & Tiempo Real:** LiveKit Agents SDK (Python).
- **Cliente Web:** LiveKit JavaScript Client (agent-starter-embed).
- **Hosting Frontend:** Vercel (gratis).
- **LiveKit:** LiveKit Cloud (self-hosted opcional).
- **Audio TTS/STT:** edge-tts y capacidades nativas de Gemini.
- **Base de Datos:** SQLite (aiosqlite) para persistencia de historial.

## 3. Arquitectura y Flujo de Datos

### 3.1 Componentes Principales
- **Cliente Web (Frontend):** Interfaz web basada en agent-starter-embed de LiveKit. Funciona en navegador y móvil. Se conecta directamente a LiveKit Cloud.
- **LiveKit Agent (Backend de voz):** Proceso Python que se une a la sala cuando el usuario se conecta.
- **Base de datos:** SQLite con historial de conversaciones.

### 3.2 Pipeline de Interacción
1. **Entrada:** El usuario abre el cliente web y se conecta a la sala de LiveKit.
2. **Procesamiento:** El Agente de LiveKit procesa el stream de audio con Gemini.
3. **Acción:** El agente ejecuta herramientas (search, weather, time, commands) según necesidad.
4. **Salida:** Audio nativo entregado por LiveKit al cliente web.

## 4. Requisitos Funcionales

### 4.1 Herramientas (Tools)
- `execute_command(command: str)`: Ejecución de comandos CLI (GOG) para Gmail y Calendar.
- `get_weather(city: str)`: Consulta de clima actual.
- `search_web(query: str)`: Búsqueda de información en tiempo real.
- `get_time()`: Gestión de fechas y zonas horarias.
- `obsidian_search(query, limit)`: Búsqueda de notas en el vault local de Obsidian.
- `obsidian_get_vault()`: Consulta de la bóveda activa de Obsidian.
- `obsidian_set_vault(vault_path)`: Cambio de bóveda activa en runtime.
- `obsidian_tasks(note_path, status, limit)`: Listado de tareas Markdown en Obsidian.
- `obsidian_add(note_path, task)`: Alta de tareas en notas de Obsidian.
- `obsidian_complete(note_path, task_contains)`: Cierre de tareas en Obsidian.
- `obsidian_create_vault(vault_name, base_dir)`: Creación de nuevas bóvedas de Obsidian.

### 4.2 Gestión de Sesiones
- **Autenticación:** El cliente web obtiene token de LiveKit Cloud directamente.
- **Persistencia:** El agente mantiene historial en SQLite para contexto de conversación.

## 5. Requisitos No Funcionales
- **Latencia:** Objetivo < 1.5s para respuestas de voz.
- **Accesibilidad:** Cada interacción de voz debe tener transcripción textual.
- **Persistencia:** Mantener historial de conversación entre sesiones.

## 6. Manejo de Errores
- **Fallo de Micro:** Notificar al usuario en la interfaz del cliente web.
- **Desconexión:** Reintento automático de conexión con backoff exponencial.
- **Validación de token:** Verificar token antes de permitir conexión a sala.

## 7. Protocolo de Actualización

### 7.1 Sistema de Memoria (Engram MCP)
- **Búsqueda activa:** En cada sesión nueva o inicio de interacciones, DEBE realizarse una búsqueda en Engram para recuperar contexto previo.
- **Recuperación:** Usar `mem_search` con palabras clave del proyecto para encontrar decisiones, patrones y aprendizajes previos.
- **Consolidación:** Al final de cada sesión/significativo, guardar observaciones importantes con `mem_save`.

### 7.2 Documentación Activa
En cada avance del proyecto se debe mantener:
1. **Engram MCP:** Memoria de largo plazo (búsqueda + guardado)
2. **MEMORIA.md:** Estado actual de la arquitectura y funcionalidades
3. **CHANGELOG.md:** Registro de versiones y cambios. Formato a seguir en **skills/changelog-generator**
4. **Git:** Rama main - Commits con formato predefinido en **skills/github-committer**

### 7.3 Flujo de Trabajo
1. Iniciar sesión → Buscar en Engram contexto previo
2. Durante desarrollo: 
    - Guardar decisiones importantes y avances en Engram.
    - Actualizar MEMORIA.md y CHANGELOG.md
    - Commit → realizar committers del avance realizado.
3. Finalizar sesión → Actualizar toda documentación.

## 8. Servicios Externos
- **LiveKit Cloud:** Proveedor de la infraestructura de voz/video.
- **Google Gemini:** Modelo de IA para procesamiento de voz.
- **GOG CLI:** Integración con Google Workspace (Gmail, Calendar).
