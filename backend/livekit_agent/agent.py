"""
OpenNemesis-Live - LiveKit Voice Agent
Punto de entrada: python main.py dev|console
"""

import asyncio
import json
import logging
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import Agent, AgentSession, room_io
from livekit.plugins import google, noise_cancellation

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
    close_db,
    format_history_for_context,
    get_history,
    init_db,
    save_message,
)
from data.file_memory import (
    SessionMemoryBuffer,
    get_persona_missing_fields,
    persist_session_memory,
)
from livekit_agent.context_builder import load_context
from livekit_agent.realtime_memory import (
    make_chat_publisher,
    persist_persona_updates_from_output,
    process_realtime_memory_capture,
)

load_dotenv()

logger = logging.getLogger("OpenNemesis-Live.Agent")

MAX_HISTORY_CONTEXT = 20
TEMPORAL_WINDOW_HOURS = 48
LOCAL_TZ = ZoneInfo("Europe/Madrid")


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
    logger.info(f"Room participants: {list(ctx.room.remote_participants.keys())}")
    
    user_id = get_user_id(ctx)
    logger.info(f"User identifier: {user_id}")
    session_memory = SessionMemoryBuffer()
    persona_prompted = False

    async def flush_file_memory() -> None:
        try:
            await persist_session_memory(session_memory)
            logger.info("File memory persisted")
        except Exception as e:
            logger.warning(f"Could not persist file memory: {e}")

    ctx.add_shutdown_callback(flush_file_memory)
    
    db_initialized = False
    try:
        await init_db()
        db_initialized = True
        logger.info("DB initialized")
        ctx.add_shutdown_callback(close_db)
    except Exception as e:
        logger.warning(f"DB init skipped: {e}")
    
    loaded_context = await load_context(
        user_id=user_id,
        db_initialized=db_initialized,
        max_history_context=MAX_HISTORY_CONTEXT,
        local_tz=LOCAL_TZ,
        temporal_window_hours=TEMPORAL_WINDOW_HOURS,
        logger=logger,
    )
    
    agent = AssistantAgent(user_id=user_id)
    logger.info("Agent created")
    
    session_instructions = loaded_context.combined
    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            api_key=GEMINI_API_KEY,
            model=GEMINI_MODEL,
            voice=AGENT_VOICE,
            temperature=AGENT_TEMPERATURE,
            instructions=session_instructions,
        ),
    )

    publish_chat_message = make_chat_publisher(ctx, logger)

    async def handle_text_input(text: str) -> None:
        cleaned = text.strip()
        if not cleaned:
            return
        session_memory.add_user(cleaned)
        await save_message(user_id, "user", cleaned)
        asyncio.create_task(
            process_realtime_memory_capture(cleaned, publish_chat_message, logger)
        )
        await session.generate_reply(
            user_input=cleaned,
            input_modality="text",
            instructions=(
                "Si hay entrada visual activa (camara o pantalla), usala tambien en esta respuesta por texto. "
                "Solo indica que no ves imagen si realmente no llega video."
            ),
        )
    
    # Registrar eventos para debug
    @session.on("user_input_transcribed")
    def on_user_speech(ev):
        logger.info(f"USER SPEECH DETECTED: {ev.transcript}")
        session_memory.add_user(ev.transcript)
        asyncio.create_task(save_message(user_id, "user", ev.transcript))
        asyncio.create_task(
            process_realtime_memory_capture(ev.transcript, publish_chat_message, logger)
        )
    
    @session.on("conversation_item_added")
    def on_conversation_item(ev):
        logger.info(
            f"CONVERSATION ITEM: {ev.item.type} - {ev.item.text_content[:100] if ev.item.text_content else 'N/A'}..."
        )
        if ev.item.text_content:
            asyncio.create_task(save_message(user_id, "assistant", ev.item.text_content))
            if getattr(ev.item, "role", None) == "assistant":
                session_memory.add_assistant(ev.item.text_content)
                asyncio.create_task(publish_chat_message("assistant", ev.item.text_content))
                asyncio.create_task(
                    persist_persona_updates_from_output(ev.item.text_content, logger)
                )
    
    logger.info("Session created, starting...")
    
    logger.info("Starting session.start...")
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

    missing_fields = await asyncio.to_thread(get_persona_missing_fields)
    if missing_fields and not persona_prompted:
        persona_prompted = True
        await publish_chat_message(
            "system",
            "Me falta definir mi personalidad ({fields}). Puedes decirmela natural o usar: config agente nombre=... tono=... estilo=... rol=...; tambien puedes decir 'usa por defecto'.".format(
                fields=", ".join(missing_fields)
            ),
        )

    @ctx.room.on("data_received")
    def on_data_received(packet: rtc.DataPacket):
        try:
            payload = json.loads(packet.data.decode("utf-8"))
        except Exception:
            return

        if payload.get("type") != "chat":
            return

        if payload.get("role") == "user":
            text = payload.get("text", "")
            asyncio.create_task(handle_text_input(text))
    
    # Obtener el identity correcto del participante después de conectar
    logger.info("Checking remote participants...")
    for participant in ctx.room.remote_participants.values():
        logger.info(f"Found participant: {participant.identity}")
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
            history_context = format_history_for_context(
                history, max_messages=MAX_HISTORY_CONTEXT
            )
            refreshed = await load_context(
                user_id=correct_user_id,
                db_initialized=True,
                max_history_context=MAX_HISTORY_CONTEXT,
                local_tz=LOCAL_TZ,
                temporal_window_hours=TEMPORAL_WINDOW_HOURS,
                logger=logger,
            )
            combined_context = "".join(
                [refreshed.file_memory_context, history_context, refreshed.temporal_context]
            ).strip()
            if combined_context:
                logger.info("Sending history context to agent...")
                await session.generate_reply(instructions=combined_context)
            break
    
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
    
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=my_agent,
            initialize_process_timeout=60.0,
            shutdown_process_timeout=30.0,
            num_idle_processes=1,
        )
    )
