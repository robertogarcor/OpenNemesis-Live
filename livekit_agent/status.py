"""
OpenNemesis-Live - Status Check
Verificación de servicios y estado del sistema
"""

import logging
import requests


def check_services():
    """Verifica que los servicios estén conectados y activos."""
    import os
    from livekit_agent.config import (
        LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET,
        GEMINI_API_KEY
    )
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
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
        from skills.loader import get_skill_names
        skills = get_skill_names()
        skill_list = ", ".join(skills) if skills else "none"
        status["skills"] = f"✅ OK ({skill_list})"
    except Exception as e:
        status["skills"] = f"❌ Error: {str(e)[:30]}"
    
    # Verificar Tools
    try:
        from tools.tools import AVAILABLE_TOOLS
        status["tools"] = f"✅ OK ({len(AVAILABLE_TOOLS)} tools)"
    except Exception as e:
        status["tools"] = f"❌ Error: {str(e)[:30]}"
    
    # Verificar GOG CLI
    try:
        import subprocess
        GOGCLI_PATH = os.getenv("GOGCLI_PATH", "bin/gogcli")
        gog_executable = GOGCLI_PATH if GOGCLI_PATH.endswith("/gog") or GOGCLI_PATH.endswith("gog") else os.path.join(GOGCLI_PATH, "gog")
        result = subprocess.run(
            [gog_executable, "version"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.decode().strip()[:20]
            status["gog"] = f"✅ OK ({version})"
        else:
            status["gog"] = "❌ Error"
    except Exception as e:
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
