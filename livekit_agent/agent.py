"""
OpenNemesis-Live - LiveKit Voice Agent
Punto de entrada: python main.py dev|console
"""

import asyncio
import logging
import json

from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import google
from livekit.plugins import noise_cancellation

from livekit_agent.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    AGENT_VOICE,
    AGENT_TEMPERATURE,
    validate_config,
)
from tools.tools import AVAILABLE_TOOLS
from prompt import get_system_prompt
from data.db import (
    init_db,
    save_message,
    get_history,
    format_history_for_context,
)

load_dotenv()

logger = logging.getLogger("OpenNemesis-Live.Agent")

MAX_HISTORY_CONTEXT = 20


def get_user_id(ctx: agents.JobContext) -> str:
    # El metadata del participante local no está disponible al inicio
    # Solo usamos el metadata del job o el room.name
    
    # Intentar desde metadata del job
    if ctx.job.metadata:
        try:
            metadata = json.loads(ctx.job.metadata)
            if "user_id" in metadata:
                return metadata["user_id"]
        except (json.JSONDecodeError, TypeError):
            pass
    
    # Último fallback: usar el nombre del room
    return ctx.room.name


class AssistantAgent(Agent):
    """Agente de voz multimodal."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        # Prompt general: comportamiento, tareas, herramientas
        instructions = get_system_prompt()
        super().__init__(
            instructions=instructions,
            tools=AVAILABLE_TOOLS,
        )
    
    async def on_user_message(self, message: str) -> None:
        """Guarda mensaje del usuario en la base de datos."""
        logger.info(f"User message: {message[:100]}...")
        await save_message(self.user_id, "user", message)
    
    async def on_agent_message(self, message: str) -> None:
        """Guarda respuesta del agente en la base de datos."""
        logger.info(f"Agent message: {message[:100]}...")
        await save_message(self.user_id, "assistant", message)


async def my_agent(ctx: agents.JobContext):
    logger.info(f"User connected to room: {ctx.room.name}")
    
    user_id = get_user_id(ctx)
    logger.info(f"User identifier: {user_id}")
    
    db_initialized = False
    try:
        await init_db()
        db_initialized = True
        logger.info("DB initialized")
    except Exception as e:
        logger.warning(f"DB init skipped: {e}")
    
    history_context = ""
    if db_initialized:
        try:
            history = await get_history(user_id, limit=MAX_HISTORY_CONTEXT)
            logger.info(f"Loaded {len(history)} messages from history")
            history_context = format_history_for_context(history, max_messages=MAX_HISTORY_CONTEXT)
        except Exception as e:
            logger.warning(f"Could not load history: {e}")
    
    agent = AssistantAgent(user_id=user_id)
    logger.info("Agent created")
    
    session_instructions = history_context if history_context else ""
    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            api_key=GEMINI_API_KEY,
            model=GEMINI_MODEL,
            voice=AGENT_VOICE,
            temperature=AGENT_TEMPERATURE,
            instructions=session_instructions,
        ),
    )
    
    # Registrar eventos para debug
    @session.on("user_input_transcribed")
    def on_user_speech(ev):
        logger.info(f"USER SPEECH: {ev.text[:50]}...")
        asyncio.create_task(save_message(user_id, "user", ev.text))
    
    @session.on("conversation_item_added")
    def on_conversation_item(ev):
        logger.info(f"CONVERSATION ITEM: {ev.item.type} - {ev.item.text_content[:50] if ev.item.text_content else 'N/A'}...")
        if ev.item.text_content:
            asyncio.create_task(save_message(user_id, "assistant", ev.item.text_content))
    
    logger.info("Session created, starting...")
    
    try:
        await session.start(
            room=ctx.room,
            agent=agent,
            room_options=room_io.RoomOptions(
                audio_input=room_io.AudioInputOptions(
                    noise_cancellation=lambda params: noise_cancellation.BVCTelephony() if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP else noise_cancellation.BVC(), 
                ),
                video_input=True,
            ),
        )
        logger.info("Session started successfully!")
        
        # Obtener el identity correcto del participante después de conectar
        # El primer participante remote es el usuario
        for participant in ctx.room.remote_participants.values():
            correct_user_id = participant.identity
            logger.info(f"Correct user identity: {correct_user_id}")
            
            # Recargar historial con el user_id correcto
            if db_initialized and correct_user_id != user_id:
                logger.info("Reloading history with correct user_id...")
                history = await get_history(correct_user_id, limit=MAX_HISTORY_CONTEXT)
                logger.info(f"Loaded {len(history)} messages from history for user: {correct_user_id}")
                
                # Actualizar el user_id del agent
                agent.user_id = correct_user_id
                user_id = correct_user_id
                
                # Regenerar instrucciones con el historial correcto
                history_context = format_history_for_context(history, max_messages=MAX_HISTORY_CONTEXT)
                if history_context:
                    logger.info("Sending history context to agent...")
                    await session.generate_reply(instructions=history_context)
                break
        
    except Exception as e:
        logger.error(f"session.start failed: {e}", exc_info=True)
        raise
    
    logger.info(f"Agent session started for user: {user_id}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s.%(levelname)s… %(message)s"
    )
    
    if not validate_config():
        logger.error("Config validation failed")
        exit(1)
    
    logger.info(f"Tools: {[t.__name__ for t in AVAILABLE_TOOLS]}")
    logger.info("Starting LiveKit agent worker...")
    
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=my_agent))