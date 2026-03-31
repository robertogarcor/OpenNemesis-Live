import logging
import os
import subprocess
from datetime import datetime

import requests
from ddgs import DDGS
from livekit.agents import function_tool, RunContext


logger = logging.getLogger("OpenNemesis-Live.Tools")


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


AVAILABLE_TOOLS = [weather, time, search, command]
