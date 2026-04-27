"""
OpenNemesis - File-based long-term memory layer.

This module complements SQLite history with curated Markdown memory files:
- SOUL.md (global identity)
- RULES.md (global operational rules)
- USER.md (per-user profile)
- MEMORY.md (per-user long-term memory)
"""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


MEMORY_BASE_DIR = Path(__file__).parent / "memory"
USERS_DIR = MEMORY_BASE_DIR / "users"


SOUL_TEMPLATE = """# SOUL

## Identity
- Eres OpenNemesis, asistente multimodal en tiempo real.

## Voice
- Tono claro, cercano y orientado a resolver.

## Values
- Prioriza utilidad, seguridad y contexto real del usuario.

## Boundaries
- No inventes resultados de herramientas.
- Evita acciones destructivas sin confirmacion clara.
"""


RULES_TEMPLATE = """# RULES

## Execution Rules
- Si hay datos suficientes, ejecuta directamente la herramienta adecuada.
- Si falta informacion clave, pregunta lo minimo necesario.

## Memory Rules
- Usa SOUL/USER/MEMORY para personalizar sin inflar tokens.
- Guarda en MEMORY hechos verificados y decisiones estables.

## Safety Rules
- No expongas secretos.
- Evita comandos irreversibles sin validacion explicita.
"""


USER_TEMPLATE = """# USER

## Stable Profile
- (pendiente)

## Communication Preferences
- (pendiente)

## Learned Preferences
- (pendiente)
"""


MEMORY_TEMPLATE = """# MEMORY

## Verified Facts
- (pendiente)

## Active Projects
- (pendiente)

## Decisions
- (pendiente)

## Open Loops
- (pendiente)

## Session Notes
"""


@dataclass
class SessionMemoryBuffer:
    user_messages: list[str] = field(default_factory=list)
    assistant_messages: list[str] = field(default_factory=list)

    def add_user(self, text: str) -> None:
        cleaned = (text or "").strip()
        if cleaned:
            self.user_messages.append(cleaned)

    def add_assistant(self, text: str) -> None:
        cleaned = (text or "").strip()
        if cleaned:
            self.assistant_messages.append(cleaned)

    def has_content(self) -> bool:
        return bool(self.user_messages or self.assistant_messages)


def _safe_user_id(user_id: str) -> str:
    value = (user_id or "anonymous").strip()
    value = re.sub(r"[^a-zA-Z0-9._-]", "_", value)
    return value[:80] or "anonymous"


def _ensure_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content.strip() + "\n", encoding="utf-8")


def ensure_memory_layout(user_id: str) -> tuple[Path, Path, Path, Path]:
    soul_path = MEMORY_BASE_DIR / "SOUL.md"
    rules_path = MEMORY_BASE_DIR / "RULES.md"
    user_dir = USERS_DIR / _safe_user_id(user_id)
    user_path = user_dir / "USER.md"
    memory_path = user_dir / "MEMORY.md"

    _ensure_file(soul_path, SOUL_TEMPLATE)
    _ensure_file(rules_path, RULES_TEMPLATE)
    _ensure_file(user_path, USER_TEMPLATE)
    _ensure_file(memory_path, MEMORY_TEMPLATE)
    return soul_path, rules_path, user_path, memory_path


def _read_limited(path: Path, max_chars: int) -> str:
    if max_chars <= 0:
        return ""
    try:
        text = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return ""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def build_file_memory_context(user_id: str) -> str:
    soul_path, rules_path, user_path, memory_path = ensure_memory_layout(user_id)

    soul = _read_limited(soul_path, 1000)
    rules = _read_limited(rules_path, 1000)
    user = _read_limited(user_path, 900)
    memory = _read_limited(memory_path, 1400)

    blocks: list[str] = []
    if soul:
        blocks.append("## SOUL\n" + soul)
    if rules:
        blocks.append("## RULES\n" + rules)
    if user:
        blocks.append("## USER\n" + user)
    if memory:
        blocks.append("## MEMORY\n" + memory)

    if not blocks:
        return ""

    return "\n\n".join([
        "",
        "=== MEMORIA CURADA DE LARGO PLAZO ===",
        "Usa esto para personalizar sin inventar hechos.",
        "\n\n".join(blocks),
        "=====================================",
    ])


def _extract_preference_hints(messages: list[str]) -> list[str]:
    hints: list[str] = []
    for raw in messages[-20:]:
        text = " ".join(raw.split())
        lower = text.lower()
        if "prefiero" in lower and len(text) <= 180:
            hints.append(text)
            continue
        if "quiero que" in lower and len(text) <= 180:
            hints.append(text)
            continue
        match = re.search(r"\bllamame\s+([a-zA-Z0-9 _.-]{2,40})", lower)
        if match:
            hints.append(f"Nombre preferido: {match.group(1).strip()}")

    deduped: list[str] = []
    for hint in hints:
        if hint not in deduped:
            deduped.append(hint)
    return deduped[:8]


def _append_session_to_memory(memory_path: Path, buffer: SessionMemoryBuffer) -> None:
    if not buffer.has_content():
        return

    lines = [f"\n### Session {datetime.now().isoformat(timespec='seconds')}"]
    if buffer.user_messages:
        lines.append("- User highlights:")
        for item in buffer.user_messages[-5:]:
            lines.append(f"  - {item[:240]}")
    if buffer.assistant_messages:
        lines.append("- Assistant outputs:")
        for item in buffer.assistant_messages[-5:]:
            lines.append(f"  - {item[:240]}")

    with memory_path.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _merge_preference_hints(user_path: Path, hints: list[str]) -> None:
    if not hints:
        return

    text = user_path.read_text(encoding="utf-8")
    existing = set()
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("- "):
            existing.add(line[2:].strip())

    to_add = [hint for hint in hints if hint not in existing]
    if not to_add:
        return

    marker = "## Learned Preferences"
    if marker not in text:
        text = text.rstrip() + "\n\n## Learned Preferences\n"

    insert_block = "\n".join(f"- {hint}" for hint in to_add)
    text = text.rstrip() + "\n" + insert_block + "\n"
    user_path.write_text(text, encoding="utf-8")


def _persist_session_sync(user_id: str, buffer: SessionMemoryBuffer) -> None:
    _, _, user_path, memory_path = ensure_memory_layout(user_id)
    _append_session_to_memory(memory_path, buffer)
    hints = _extract_preference_hints(buffer.user_messages)
    _merge_preference_hints(user_path, hints)


async def persist_session_memory(user_id: str, buffer: SessionMemoryBuffer) -> None:
    await asyncio.to_thread(_persist_session_sync, user_id, buffer)
