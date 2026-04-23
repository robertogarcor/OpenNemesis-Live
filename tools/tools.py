import logging
import os
import re
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Set

import requests
from ddgs import DDGS
from livekit.agents import function_tool, RunContext

from tools.obsidian_tools import OBSIDIAN_TOOLS


logger = logging.getLogger("OpenNemesis-Live.Tools")


def _parse_enabled_skills() -> Optional[Set[str]]:
    raw = os.getenv("ENABLED_SKILLS", "").strip()
    if not raw:
        return None
    parsed = {item.strip().lower() for item in raw.split(",") if item.strip()}
    return parsed or None


def _is_skill_enabled(skill_name: str, enabled: Optional[Set[str]] = None) -> bool:
    if enabled is None:
        enabled = _parse_enabled_skills()
    if enabled is None:
        return True
    return skill_name.lower() in enabled


_DANGEROUS_COMMAND_PATTERNS = [
    re.compile(r"(^|\s)rm(\s|$)"),
    re.compile(r"(^|\s)rmdir(\s|$)"),
    re.compile(r"(^|\s)mv(\s|$)"),
    re.compile(r"(^|\s)sudo(\s|$)"),
    re.compile(r"(^|\s)dd(\s|$)"),
    re.compile(r"(^|\s)mkfs(\s|$)"),
    re.compile(r"(^|\s)shutdown(\s|$)"),
    re.compile(r"(^|\s)reboot(\s|$)"),
    re.compile(r"(^|\s)poweroff(\s|$)"),
    re.compile(r"git\s+reset\s+--hard"),
    re.compile(r'git\s+clean\s+-[^\n]*f'),
]


def _is_dangerous_command(command: str) -> bool:
    normalized = command.strip().lower()
    if not normalized:
        return True
    return any(pattern.search(normalized) for pattern in _DANGEROUS_COMMAND_PATTERNS)


# === Funciones Base ===

def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    try:
        response = requests.get(f"https://wttr.in/{city}?format=3")
        if response.status_code == 200:
            logging.info(f"Weather for {city}: {response.text.strip()}")
            return response.text.strip()
        else:
            logging.error(f"Failed to get weather for {city}: {response.status_code}")
            return f"Could not retrieve weather for {city}."
    except Exception as e:
        logging.error(f"Error retrieving weather for {city}: {e}")
        return f"An error occurred while retrieving weather for {city}."


def get_time() -> str:
    """Get current time."""
    try:
        now = datetime.now()
        return f"Hora actual: {now.strftime('%H:%M:%S')}\nFecha: {now.strftime('%Y-%m-%d')}"
    except Exception as e:
        logging.error(f"Error retrieving time: {e}")
        return f"An error occurred while retrieving time."


def search_web(query: str) -> str:
    """Search the web using DuckDuckGo."""
    try:
        results = DDGS().text(query, max_results=5)
        if results:
            formatted = "\n".join([f"{r.get('title', '')}: {r.get('href', '')}" for r in results])
            logging.info(f"Search results for '{query}': {formatted}")
            return formatted
        return f"No results found for '{query}'."
    except Exception as e:
        logging.error(f"Error searching the web for '{query}': {e}")
        return f"An error occurred while searching the web."


def execute_command(command: str) -> str:
    """Execute a shell command."""
    try:
        if _is_dangerous_command(command):
            return (
                "Error: comando bloqueado por seguridad. "
                "No se permiten operaciones destructivas o de alto riesgo."
            )

        env = os.environ.copy()
        env["GOG_ACCOUNT"] = os.getenv("GOG_ACCOUNT", "")
        gogcli_path = os.getenv("GOGCLI_PATH", "bin/gogcli")
        
        if gogcli_path:
            gogcli_abs = os.path.abspath(gogcli_path)
            if gogcli_abs not in env.get("PATH", ""):
                env["PATH"] = gogcli_abs + ":" + env.get("PATH", "")
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            env=env
        )
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        return result.stdout if result.stdout else "Comando ejecutado correctamente."
    except subprocess.TimeoutExpired:
        return "Error: Timeout ejecutando comando"
    except Exception as e:
        return f"Error: {str(e)}"

# === Function Tools (para LiveKit) ===

@function_tool
async def weather(ctx: RunContext, city: str) -> str:
    """Get weather for a city."""
    return get_weather(city)


@function_tool
async def time(ctx: RunContext) -> str:
    """Get current time."""
    return get_time()


@function_tool
async def search(ctx: RunContext, query: str) -> str:
    """Search the web for information."""
    return search_web(query)


@function_tool
async def command(ctx: RunContext, command: str) -> str:
    """Execute a shell command."""
    return execute_command(command)


CORE_TOOLS = [weather, time, search]
GOG_TOOLS = [command]

TOOL_GROUPS: Dict[str, List] = {
    "core": CORE_TOOLS,
    "gog": GOG_TOOLS,
    "obsidian-tasks": OBSIDIAN_TOOLS,
}

TOOL_DESCRIPTIONS: Dict[str, str] = {
    "weather": "Consulta el clima de una ciudad.",
    "time": "Obtiene fecha y hora actual.",
    "search": "Busca información en web en tiempo real.",
    "command": "Ejecuta comandos CLI (uso principal: GOG Gmail/Calendar).",
    "obsidian_get_vault": "Muestra información de la bóveda Obsidian activa.",
    "obsidian_set_vault": "Cambia la bóveda Obsidian activa en runtime.",
    "obsidian_search": "Busca notas en Obsidian por nombre/contenido.",
    "obsidian_tasks_vault": "Lista tareas de toda la bóveda activa de Obsidian.",
    "obsidian_tasks": "Lista tareas Markdown en Obsidian.",
    "obsidian_add": "Añade una tarea en una nota de Obsidian.",
    "obsidian_complete": "Marca como completada una tarea en Obsidian.",
    "obsidian_create_vault": "Crea una nueva bóveda de Obsidian.",
    "obsidian_tasks_in_vault": "Lista tareas de una bóveda específica por nombre o ruta.",
}


def get_active_tools() -> List:
    enabled = _parse_enabled_skills()

    tools: List = []
    tools.extend(CORE_TOOLS)

    if _is_skill_enabled("gog", enabled):
        tools.extend(GOG_TOOLS)

    if _is_skill_enabled("obsidian-tasks", enabled):
        tools.extend(OBSIDIAN_TOOLS)

    return tools


def get_active_tool_descriptions() -> str:
    active = get_active_tools()
    if not active:
        return "No hay herramientas activas."

    lines = []
    for tool in active:
        name = tool.__name__
        desc = TOOL_DESCRIPTIONS.get(name, "Herramienta disponible.")
        lines.append(f"- {name}: {desc}")
    return "\n".join(lines)


AVAILABLE_TOOLS = get_active_tools()
