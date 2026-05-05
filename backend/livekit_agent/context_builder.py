"""Builds conversation context for LiveKit sessions."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from data.db import format_history_for_context, get_history, get_history_with_timestamps
from data.file_memory import build_file_memory_context


@dataclass
class LoadedContext:
    file_memory_context: str
    history_context: str
    temporal_context: str

    @property
    def combined(self) -> str:
        return "".join(
            [self.file_memory_context, self.history_context, self.temporal_context]
        ).strip()


def _normalize_dt(value: datetime | None, local_tz: ZoneInfo) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=local_tz)
    return value.astimezone(local_tz)


def build_temporal_context(
    messages: list,
    now: datetime,
    local_tz: ZoneInfo,
    temporal_window_hours: int,
) -> str:
    if not messages:
        return ""

    window = timedelta(hours=temporal_window_hours)
    recent = []
    for msg in messages:
        created_at = _normalize_dt(msg.get("created_at"), local_tz)
        if created_at is None:
            continue
        if now - created_at <= window:
            recent.append({**msg, "created_at": created_at})

    if not recent:
        return ""

    last_user = next((m for m in reversed(recent) if m.get("role") == "user"), None)
    if not last_user:
        return ""

    last_time = last_user["created_at"]
    label = "hoy" if last_time.date() == now.date() else "ayer"
    content = (last_user.get("content") or "").strip()
    if len(content) > 200:
        content = content[:197] + "..."

    return "\n".join(
        [
            "",
            "=== CONTEXTO TEMPORAL (ULTIMAS 36H) ===",
            "Usa esto solo si aporta contexto a la respuesta.",
            f"Hablaste con el usuario {label} sobre: {content}",
            "======================================",
        ]
    )


async def load_context(
    *,
    user_id: str,
    db_initialized: bool,
    max_history_context: int,
    local_tz: ZoneInfo,
    temporal_window_hours: int,
    logger: logging.Logger,
) -> LoadedContext:
    history_context = ""
    temporal_context = ""

    try:
        file_memory_context = build_file_memory_context()
        logger.info("File memory context loaded")
    except Exception as e:
        logger.warning(f"Could not load file memory context: {e}")
        file_memory_context = ""

    if db_initialized:
        try:
            history = await get_history(user_id, limit=max_history_context)
            history_with_ts = await get_history_with_timestamps(
                user_id, limit=max_history_context
            )
            logger.info(f"Loaded {len(history)} messages from history")
            history_context = format_history_for_context(
                history, max_messages=max_history_context
            )
            temporal_context = build_temporal_context(
                history_with_ts,
                now=datetime.now(local_tz),
                local_tz=local_tz,
                temporal_window_hours=temporal_window_hours,
            )
        except Exception as e:
            logger.warning(f"Could not load history: {e}")

    return LoadedContext(
        file_memory_context=file_memory_context,
        history_context=history_context,
        temporal_context=temporal_context,
    )
