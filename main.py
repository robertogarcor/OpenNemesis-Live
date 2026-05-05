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
from livekit_agent.config import validate_config
from livekit_agent.status import startup

env_files = [Path(".env"), Path(".env.local")]
for env_path in env_files:
    if env_path.exists():
        load_dotenv(env_path)
        break


def run_livekit(mode: str = "dev"):
    """Ejecuta el agente de LiveKit."""
    project_dir = Path(__file__).parent
    
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_dir)
    
    agent_script = project_dir / "livekit_agent" / "agent.py"
    args = [sys.executable, str(agent_script), mode]
    
    process = subprocess.Popen(
        args,
        cwd=str(project_dir),
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
