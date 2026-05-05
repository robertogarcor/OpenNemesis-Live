"""
OpenNemesis-Live - LiveKit Agent Configuration
Variables de configuración del agente
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Cargar variables de entorno (root preferido, fallback local)
ROOT_DIR = Path(__file__).resolve().parents[2]
_env_candidates = [
    ROOT_DIR / ".env.local",
    ROOT_DIR / ".env",
    Path.cwd() / ".env.local",
    Path.cwd() / ".env",
]
for env_path in _env_candidates:
    if env_path.exists():
        load_dotenv(env_path)
        break

# LiveKit Configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Agent Configuration
AGENT_VOICE = os.getenv("AGENT_VOICE", "sulafat")
AGENT_TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.8"))
LIVEKIT_AGENT_NAME = os.getenv("LIVEKIT_AGENT_NAME", "")

# GOG CLI Configuration (Optional)
GOG_ACCOUNT = os.getenv("GOG_ACCOUNT", "")
GOGCLI_PATH = os.getenv("GOGCLI_PATH", "bin/gogcli/gog")

# Obsidian Configuration (Optional)
OBSIDIAN_VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH", "")
OBSIDIAN_ALLOWED_BASE_DIRS = os.getenv("OBSIDIAN_ALLOWED_BASE_DIRS", "")

# Feature Flags (Optional)
ENABLED_SKILLS = os.getenv("ENABLED_SKILLS", "")


def validate_config() -> bool:
    """Valida que la configuración mínima esté presente."""
    errors = []
    
    if not LIVEKIT_URL:
        errors.append("LIVEKIT_URL is required")
    if not LIVEKIT_API_KEY:
        errors.append("LIVEKIT_API_KEY is required")
    if not LIVEKIT_API_SECRET:
        errors.append("LIVEKIT_API_SECRET is required")
    if not GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY is required")
    
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True
