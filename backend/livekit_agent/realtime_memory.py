"""Realtime memory capture and user feedback helpers."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Callable, Coroutine
from typing import Any

from data.file_memory import (
    apply_default_persona,
    get_persona_missing_fields,
    persist_persona_from_agent_output,
    persist_realtime_user_memory,
)

Publisher = Callable[[str, str], Coroutine[Any, Any, None]]


def make_chat_publisher(ctx, logger: logging.Logger) -> Publisher:
    async def publish_chat_message(role: str, text: str) -> None:
        payload = json.dumps({"type": "chat", "role": role, "text": text})
        try:
            await ctx.room.local_participant.publish_data(payload, reliable=True)
        except Exception as e:
            logger.warning(f"Failed to publish data message: {e}")

    return publish_chat_message


async def process_realtime_memory_capture(text: str, publish: Publisher, logger: logging.Logger) -> None:
    try:
        lower = (text or "").lower()
        if any(
            token in lower
            for token in ["usa por defecto", "usar por defecto", "elige tu", "elige tú"]
        ):
            defaults = await asyncio.to_thread(apply_default_persona)
            summary = ", ".join(f"{k}={v}" for k, v in defaults.items())
            await publish("system", f"Personalidad por defecto aplicada: {summary}")
            return

        result = await persist_realtime_user_memory(text)
        persona_updates = (result or {}).get("persona_updates", {})
        persona_intent = bool((result or {}).get("persona_intent", False))
        if isinstance(persona_updates, dict) and persona_updates:
            summary = ", ".join(f"{k}={v}" for k, v in persona_updates.items())
            missing = await asyncio.to_thread(get_persona_missing_fields)
            if missing:
                summary = f"{summary}. Faltan por definir: {', '.join(missing)}"
            await publish("system", f"Personalidad del agente guardada: {summary}")
        elif persona_intent:
            await publish(
                "system",
                "He detectado personalizacion, pero no pude extraer campos claros. Usa: config agente nombre=... tono=... estilo=... rol=...",
            )
    except Exception as e:
        logger.warning(f"Could not persist realtime memory: {e}")


async def persist_persona_updates_from_output(text: str, logger: logging.Logger) -> None:
    try:
        updates = await persist_persona_from_agent_output(text)
        if updates:
            logger.info(f"Persona updated from assistant output: {updates}")
    except Exception as e:
        logger.warning(f"Could not persist persona from assistant output: {e}")
