"""
OpenNemesis-Live - Main Entry Point
Punto de entrada: python main.py <modo>
"""

import logging
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from backend.livekit_agent.config import validate_config
from backend.livekit_agent.status import startup

env_files = [
    BACKEND_DIR / ".env.local",
    BACKEND_DIR / ".env",
    Path(".env.local"),
    Path(".env"),
]
for env_path in env_files:
    if env_path.exists():
        load_dotenv(env_path)
        break


def run_livekit(mode: str = "dev"):
    """Ejecuta el agente de LiveKit."""
    backend_dir = BACKEND_DIR
    
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [
            str(ROOT_DIR),
            str(backend_dir),
            env.get("PYTHONPATH", ""),
        ]
    ).strip(os.pathsep)
    
    agent_script = backend_dir / "livekit_agent" / "agent.py"
    args = [sys.executable, str(agent_script), mode]
    
    process = subprocess.Popen(
        args,
        cwd=str(backend_dir),
        env=env,
    )
    
    try:
        process.wait()
    except KeyboardInterrupt:
        logging.getLogger("OpenNemesis-Live").info("Stopping...")
        process.terminate()
        process.wait()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    if not validate_config():
        logging.error("Config validation failed")
        return
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "dev"
    
    startup(mode)
    
    if mode == "dev":
        run_livekit("dev")
    elif mode == "console":
        run_livekit("console")
    else:
        logging.info(f"Unknown mode: {mode}")
        logging.info("Usage: python main.py dev|console")


if __name__ == "__main__":
    main()
