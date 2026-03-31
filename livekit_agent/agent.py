"""
OpenNemesis-Live - LiveKit Voice Agent
Punto de entrada: python main.py dev|console
"""

import asyncio
import logging
import json

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import google

from livekit_agent.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    AGENT_VOICE,
    AGENT_TEMPERATURE,
    validate_config,
)
from skills.loader import get_skill_names
from tools.tools import AVAILABLE_TOOLS
from prompt import get_system_prompt
from data.db import (
    init_db,
    save_message,
    get_history,
    format_history_for_context,
    close_db,
)

load_dotenv()

logger = logging.getLogger("OpenNemesis-Live.Agent")

# Máximo de mensajes del historial a incluir en el contexto
MAX_HISTORY_CONTEXT = 20


def get_user_id(ctx: agents.JobContext) -> str:
    """
    Extrae el user_id del contexto de la sesión.
    Prioriza:
    1. ctx.job.metadata (si contiene user_id en JSON)
    2. room.name (identificador único de la sala)
    """
    # Intentar obtener user_id desde metadata del job
    if ctx.job.metadata:
        try:
            metadata = json.loads(ctx.job.metadata)
            if "user_id" in metadata:
                return metadata["user_id"]
        except (json.JSONDecodeError, TypeError):
            pass
    
    # Fallback: usar el nombre del room como identificador
    return ctx.room.name


class VoiceAgent(Agent):
    """Agente de voz con persistencia de historial."""
    
    def __init__(self, user_id: str, history_context: str = ""):
        self.user_id = user_id
        self.history_context = history_context
        skills = get_skill_names()
        logger.info(f"Skills: {skills}, UserID: {user_id}")
        
        # Combinar instrucciones base con historial
        instructions = get_system_prompt()
        if history_context:
            instructions = f"{instructions}\n{history_context}"
        
        super().__init__(
            instructions=instructions,
            tools=AVAILABLE_TOOLS,
        )
    
    async def on_enter(self) -> None:
        """Called when the agent enters a conversation."""
        logger.info(f"VoiceAgent activated in session for user: {self.user_id}")
    
    async def on_user_message(self, message: str) -> None:
        """Called when user sends a message (text input)."""
        logger.info(f"User message: {message[:100]}...")
        # Guardar mensaje del usuario
        await save_message(self.user_id, "user", message)
    
    async def on_agent_message(self, message: str) -> None:
        """Called when agent generates a message/response."""
        logger.info(f"Agent message: {message[:100]}...")
        # Guardar respuesta del agente
        await save_message(self.user_id, "assistant", message)


server = AgentServer()


@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    """Entry point when user connects."""
    logger.info(f"User connected to room: {ctx.room.name}")
    
    # Obtener user_id
    user_id = get_user_id(ctx)
    logger.info(f"User identifier: {user_id}")
    
    # Inicializar base de datos
    db_initialized = False
    try:
        await init_db()
        db_initialized = True
    except Exception as e:
        logger.warning(f"DB init skipped: {e}")
    
    # Cargar historial solo si DB está inicializada
    history = []
    history_context = ""
    
    if db_initialized:
        try:
            history = await get_history(user_id, limit=MAX_HISTORY_CONTEXT)
            logger.info(f"Loaded {len(history)} messages from history")
            
            # Formatear historial para contexto
            history_context = format_history_for_context(history, max_messages=MAX_HISTORY_CONTEXT)
        except Exception as e:
            logger.warning(f"Could not load history: {e}")
    
    # Crear agente con contexto histórico
    agent = VoiceAgent(user_id=user_id, history_context=history_context)
    
    # Crear sesión con Gemini Realtime
    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            api_key=GEMINI_API_KEY,
            model=GEMINI_MODEL,
            voice=AGENT_VOICE,
            temperature=AGENT_TEMPERATURE,
            # Las instrucciones ya incluyen el historial en el agente
            instructions=agent.instructions,
        ),
    )
    
    # Iniciar sesión
    await session.start(
        room=ctx.room,
        agent=agent,
        room_options=room_io.RoomOptions(
            text_input=True,
        )
    )
    
    logger.info("Session started, setting up data listener...")
    
    # Escuchar mensajes de datos del room (para mensajes de texto desde TMA)
    @ctx.room.on("data_received")
    def on_data_received(msg):
        """Handle incoming data messages from participants."""
        logger.info(f"Data received from {msg.participant.identity}: {msg.data[:50] if msg.data else 'empty'}")
        if msg.data:
            try:
                text_data = msg.data.decode('utf-8')
                import json
                msg_json = json.loads(text_data)
                if msg_json.get('type') == 'text':
                    user_text = msg_json.get('text', '')
                    logger.info(f"Received text from TMA: {user_text}")
                    # Trigger agent response
                    async def respond():
                        await session.generate_reply(instructions=f"User said: {user_text}. Respond appropriately.")
                    asyncio.create_task(respond())
            except Exception as e:
                logger.warning(f"Could not parse data message: {e}")
    
    # Saludo inicial
    logger.info("Sending greeting...")
    
    # Registrar callback para guardar mensajes del usuario
    # (Esto funciona cuando el usuario envía texto)
    
    logger.info(f"Agent session started for user: {user_id}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    if not validate_config():
        logger.error("Config validation failed")
        exit(1)
    
    logger.info(f"Tools: {[t.__name__ for t in AVAILABLE_TOOLS]}")
    
    agents.cli.run_app(server)
