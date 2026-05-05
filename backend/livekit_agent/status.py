"""
OpenNemesis-Live - Status Check
Verificación de servicios y estado del sistema
"""

import logging
import os
import subprocess
from pathlib import Path

import requests

from backend.livekit_agent.config import (
    GEMINI_API_KEY,
    LIVEKIT_URL,
)


def check_services():
    """Verifica que los servicios estén conectados y activos."""
    GOGCLI_PATH = os.getenv("GOGCLI_PATH", "bin/gogcli/gog")
    
    logger = logging.getLogger("OpenNemesis-Live")
    status = {}
    
    # Verificar LiveKit Cloud
    try:
        if LIVEKIT_URL:
            response = requests.get(
                LIVEKIT_URL.replace("wss", "https").replace("/room", "/health"),
                timeout=5
            )
            status["livekit"] = "✅ OK" if response.status_code == 200 else "❌ Error"
        else:
            status["livekit"] = "❌ NOT SET"
    except Exception as e:
        status["livekit"] = f"❌ Error: {str(e)[:30]}"
    
    # Verificar Gemini API
    try:
        if GEMINI_API_KEY:
            from google.genai import Client
            client = Client(api_key=GEMINI_API_KEY)
            client.models.list()
            status["gemini"] = "✅ OK"
        else:
            status["gemini"] = "❌ NOT SET"
    except Exception as e:
        status["gemini"] = f"❌ Error: {str(e)[:30]}"
    
    
    # Verificar Skills
    try:
        from backend.skills.loader import get_skill_names
        skills = get_skill_names()
        skill_list = ", ".join(skills) if skills else "none"
        status["skills"] = f"✅ OK ({skill_list})"
    except Exception as e:
        status["skills"] = f"❌ Error: {str(e)[:30]}"
    
    # Verificar Tools
    try:
        from backend.tools.tools import AVAILABLE_TOOLS
        status["tools"] = f"✅ OK ({len(AVAILABLE_TOOLS)} tools)"
    except Exception as e:
        status["tools"] = f"❌ Error: {str(e)[:30]}"
    
    # Verificar GOG CLI
    try:
        root_dir = Path(__file__).resolve().parents[2]
        gog_env = os.getenv("GOGCLI_PATH", "")
        if gog_env:
            gog_base = Path(gog_env)
            if not gog_base.is_absolute():
                gog_base = (root_dir / gog_base).resolve()
        else:
            gog_base = (root_dir / "bin" / "gogcli").resolve()

        gog_executable = gog_base if gog_base.name == "gog" else gog_base / "gog"
        result = subprocess.run(
            [str(gog_executable), "version"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.decode().strip()[:20]
            status["gog"] = f"✅ OK ({version})"
        else:
            status["gog"] = "❌ Error ejecutando gog"
    except FileNotFoundError:
        status["gog"] = "⏸️ BINARIO NO ENCONTRADO"
    except Exception:
        status["gog"] = "⏸️ NOT CONFIGURED"
    
    return status


def startup(mode: str = "dev"):
    """Unified startup: banner + mode + services check."""
    logger = logging.getLogger("OpenNemesis-Live")
    
    print("""
╔═══════════════════════════════════════════════════════════╗
║                  OpenNemesis-Live v1.0                   ║
║           Voice AI Agent with LiveKit & Gemini           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    logger.info(f"Mode: {mode}")
    logger.info(f"Starting {mode} mode...")
    
    logger.info("=== Services Status ===")
    services = check_services()
    for service, st in services.items():
        logger.info(f"  {service}: {st}")
    
    return True
