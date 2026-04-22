import logging
import os
import re
import subprocess
from datetime import datetime

import requests
from ddgs import DDGS
from livekit.agents import function_tool, RunContext

from tools.obsidian_tools import OBSIDIAN_TOOLS


logger = logging.getLogger("OpenNemesis-Live.Tools")


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


AVAILABLE_TOOLS = [
    weather,
    time,
    search,
    command,
    *OBSIDIAN_TOOLS,
]
