"""OpenNemesis - File-based long-term memory layer.

This module complements SQLite history with curated Markdown memory files:
- SOUL.md (global identity)
- RULES.md (global operational rules)
- USER.md (personal profile)
- MEMORY.md (personal long-term memory)
"""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


MEMORY_BASE_DIR = Path(__file__).parent / "memory"
USER_PATH = MEMORY_BASE_DIR / "USER.md"
MEMORY_PATH = MEMORY_BASE_DIR / "MEMORY.md"
PERSONA_FIELDS = ("Name", "Tone", "Style", "Role")


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

## Agent Persona
- Name: (pendiente)
- Tone: (pendiente)
- Style: (pendiente)
- Role: (pendiente)
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


def _has_persona_intent(text: str) -> bool:
    lower = (text or "").lower()
    return any(
        token in lower
        for token in [
            "te llamas",
            "tu nombre es",
            "quiero llamarte",
            "te puedo llamar",
            "tu tono",
            "quiero que hables",
            "habla en tono",
            "responde de forma",
            "tu estilo",
            "actua como",
            "actúa como",
            "tu rol",
            "config agente",
        ]
    )


def _ensure_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content.strip() + "\n", encoding="utf-8")


def ensure_memory_layout() -> tuple[Path, Path, Path, Path]:
    soul_path = MEMORY_BASE_DIR / "SOUL.md"
    rules_path = MEMORY_BASE_DIR / "RULES.md"
    user_path = USER_PATH
    memory_path = MEMORY_PATH

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


def build_file_memory_context() -> str:
    soul_path, rules_path, user_path, memory_path = ensure_memory_layout()

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
    def _trim_name(value: str) -> str:
        cleaned = value.strip(" .,:;")
        cleaned = re.split(r"\b(?:y|que|pero)\b", cleaned, maxsplit=1, flags=re.IGNORECASE)[0]
        cleaned = cleaned.strip(" .,:;")
        return cleaned

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
            continue
        match = re.search(r"\bme\s+llamo\s+([a-zA-Z][a-zA-Z0-9 _.-]{1,40})", text, flags=re.IGNORECASE)
        if match:
            candidate = _trim_name(match.group(1))
            if candidate:
                hints.append(f"Nombre: {candidate}")
            continue
        match = re.search(r"\bmi\s+nombre\s+es\s+([a-zA-Z][a-zA-Z0-9 _.-]{1,40})", text, flags=re.IGNORECASE)
        if match:
            candidate = _trim_name(match.group(1))
            if candidate:
                hints.append(f"Nombre: {candidate}")
            continue
        match = re.search(r"\btrabajo\s+como\s+([a-zA-Z][a-zA-Z0-9 _.,-]{1,60})", text, flags=re.IGNORECASE)
        if match:
            hints.append(f"Profesion: {match.group(1).strip(' .,:;')}")
            continue
        match = re.search(r"\bme\s+dedico\s+a\s+([a-zA-Z][a-zA-Z0-9 _.,-]{1,60})", text, flags=re.IGNORECASE)
        if match:
            hints.append(f"Profesion: {match.group(1).strip(' .,:;')}")
            continue
        match = re.search(r"\bsoy\s+(?:un|una)?\s*([a-zA-Z][a-zA-Z0-9 _.,-]{1,60})", text, flags=re.IGNORECASE)
        if match:
            candidate = match.group(1).strip(' .,:;')
            if len(candidate.split()) <= 6:
                hints.append(f"Profesion: {candidate}")

    deduped: list[str] = []
    for hint in hints:
        if hint not in deduped:
            deduped.append(hint)
    return deduped[:8]


def _append_session_to_memory(memory_path: Path, buffer: SessionMemoryBuffer) -> None:
    if not buffer.has_content():
        return

    def _clip(value: str, max_len: int = 420) -> str:
        text = value.strip()
        if len(text) <= max_len:
            return text
        window = text[: max_len + 1]
        cut = max(window.rfind(". "), window.rfind("; "), window.rfind(", "))
        if cut > int(max_len * 0.6):
            return window[:cut].rstrip() + "..."
        return text[: max_len - 3].rstrip() + "..."

    lines = [f"\n### Session {datetime.now().isoformat(timespec='seconds')}"]
    if buffer.user_messages:
        lines.append("- User highlights:")
        for item in buffer.user_messages[-5:]:
            lines.append(f"  - {_clip(item)}")
    if buffer.assistant_messages:
        lines.append("- Assistant outputs:")
        for item in buffer.assistant_messages[-5:]:
            lines.append(f"  - {_clip(item)}")

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
    text = _cleanup_pending_markers(text)
    user_path.write_text(text, encoding="utf-8")


def _extract_agent_persona_updates(text: str) -> dict[str, str]:
    cleaned = " ".join((text or "").split())
    if not cleaned:
        return {}

    updates: dict[str, str] = {}

    # Explicit command mode: config agente nombre=... tono=... estilo=... rol=...
    explicit = re.search(r"\bconfig\s+agente\b(.+)$", cleaned, flags=re.IGNORECASE)
    if explicit:
        tail = explicit.group(1)
        for key, value in re.findall(
            r"\b(nombre|tono|estilo|rol)\s*=\s*(.+?)(?=\s+(?:nombre|tono|estilo|rol)\s*=|$)",
            tail,
            flags=re.IGNORECASE,
        ):
            cleaned_value = value.strip(" .,:;")
            if not cleaned_value:
                continue
            normalized_key = key.lower()
            if normalized_key == "nombre":
                updates["Name"] = cleaned_value
            elif normalized_key == "tono":
                updates["Tone"] = cleaned_value
            elif normalized_key == "estilo":
                updates["Style"] = cleaned_value
            elif normalized_key == "rol":
                updates["Role"] = cleaned_value

    name_match = re.search(r"\bte\s+llamas\s+([a-zA-Z][a-zA-Z0-9 _.-]{1,40})", cleaned, flags=re.IGNORECASE)
    if name_match:
        value = name_match.group(1).strip(" .,:;")
        value = re.split(r"\b(?:y|pero|que)\b", value, maxsplit=1, flags=re.IGNORECASE)[0].strip(" .,:;")
        if value:
            updates["Name"] = value

    name_match_2 = re.search(r"\b(?:tu\s+nombre\s+es|quiero\s+llamarte|te\s+puedo\s+llamar)\s+([a-zA-Z][a-zA-Z0-9 _.-]{1,40})", cleaned, flags=re.IGNORECASE)
    if name_match_2:
        value = name_match_2.group(1).strip(" .,:;")
        value = re.split(r"\b(?:y|pero|que)\b", value, maxsplit=1, flags=re.IGNORECASE)[0].strip(" .,:;")
        if value:
            updates["Name"] = value

    name_match_3 = re.search(
        r"\b(?:tu\s+nombre\s+me\s+gustaria\s+que\s+fuese|tu\s+nombre\s+sea|me\s+gustaria\s+que\s+te\s+llamases|podrias\s+llamarte|podr[ií]as\s+llamarte)\s+([a-zA-Z][a-zA-Z0-9 _.-]{1,40})",
        cleaned,
        flags=re.IGNORECASE,
    )
    if name_match_3:
        value = name_match_3.group(1).strip(" .,:;")
        value = re.split(r"\b(?:y|pero|que)\b", value, maxsplit=1, flags=re.IGNORECASE)[0].strip(" .,:;")
        if value:
            updates["Name"] = value

    tone_match = re.search(r"\b(?:tu\s+tono\s+es|habla\s+en\s+tono|quiero\s+que\s+hables\s+en\s+tono)\s+([a-zA-Z][a-zA-Z0-9 _.,-]{1,50})", cleaned, flags=re.IGNORECASE)
    if tone_match:
        value = tone_match.group(1).strip(" .,:;")
        if value:
            updates["Tone"] = value

    style_match = re.search(r"\b(?:tu\s+estilo\s+es|quiero\s+que\s+respondas\s+de\s+forma|responde\s+de\s+forma)\s+([a-zA-Z][a-zA-Z0-9 _.,-]{1,60})", cleaned, flags=re.IGNORECASE)
    if style_match:
        value = style_match.group(1).strip(" .,:;")
        if value:
            updates["Style"] = value

    role_match = re.search(r"\b(?:actua\s+como|actúa\s+como|tu\s+rol\s+es|quiero\s+que\s+seas)\s+([a-zA-Z][a-zA-Z0-9 _.,/-]{1,180})", cleaned, flags=re.IGNORECASE)
    if role_match:
        value = role_match.group(1).strip(" .,:;")
        value = re.split(r"[.!?]", value, maxsplit=1)[0].strip(" .,:;")
        if value:
            updates["Role"] = value

    lower = cleaned.lower()
    persona_intent = _has_persona_intent(cleaned)
    if persona_intent:
        tone_keywords = ["formal", "cercano", "directo", "amigable", "serio", "profesional"]
        style_keywords = ["breve", "conciso", "detallado", "tecnico", "técnico", "didactico", "didáctico"]
        for keyword in tone_keywords:
            if keyword in lower:
                updates.setdefault("Tone", keyword)
                break
        for keyword in style_keywords:
            if keyword in lower:
                updates.setdefault("Style", keyword)
                break

        if "agradable" in lower and "Tone" not in updates:
            updates["Tone"] = "agradable"

        if "paso a paso" in lower and "Style" not in updates:
            updates["Style"] = "paso a paso"

        if "proactivo" in lower and "Style" not in updates:
            updates["Style"] = "proactivo"

    if updates.get("Role") and "Style" not in updates:
        updates["Style"] = "claro y conciso"

    return updates


def _extract_agent_persona_from_agent_output(text: str) -> dict[str, str]:
    cleaned = " ".join((text or "").split())
    if not cleaned:
        return {}

    updates: dict[str, str] = {}

    name_patterns = [
        r"\b(?:me\s+llamar[eé]|mi\s+nombre\s+ser[aá]|soy)\s+([A-Za-z][A-Za-z0-9 _.-]{1,40})",
        r"\b([A-Za-z][A-Za-z0-9 _.-]{1,40})\s+ser[aá]\s+mi\s+nombre",
    ]
    for pattern in name_patterns:
        match = re.search(pattern, cleaned, flags=re.IGNORECASE)
        if match:
            value = match.group(1).strip(" .,:;")
            value = re.split(r"\b(?:y|pero|que)\b", value, maxsplit=1, flags=re.IGNORECASE)[0].strip(" .,:;")
            if value and len(value.split()) <= 4:
                updates["Name"] = value
                break

    style_match = re.search(
        r"\bmi\s+estilo(?:\s+de\s+asistencia)?(?:\s+como\s+asistente)?\s+.*?\s+es\s+([^.!?]{3,140})",
        cleaned,
        flags=re.IGNORECASE,
    )
    if style_match:
        value = style_match.group(1).strip(" .,:;")
        if value:
            updates["Style"] = value

    tone_match = re.search(
        r"\bmi\s+tono\s+.*?\s+es\s+([^.!?]{3,120})",
        cleaned,
        flags=re.IGNORECASE,
    )
    if tone_match:
        value = tone_match.group(1).strip(" .,:;")
        if value:
            updates["Tone"] = value

    role_match = re.search(
        r"\b(?:mi\s+rol\s+como|ser[eé]\s+tu\s+asistente|soy\s+tu\s+asistente)\s+([^.!?]{3,180})",
        cleaned,
        flags=re.IGNORECASE,
    )
    if role_match:
        value = role_match.group(1).strip(" .,:;")
        if value:
            updates["Role"] = value

    return updates


def _cleanup_pending_markers(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("## "):
            section = [line]
            i += 1
            while i < len(lines) and not lines[i].startswith("## "):
                section.append(lines[i])
                i += 1

            has_real_items = any(
                s.strip().startswith("- ") and "(pendiente)" not in s for s in section[1:]
            )
            if has_real_items:
                section = [s for s in section if s.strip() != "- (pendiente)" and s.strip() != "- (actualizado)"]
            out.extend(section)
            continue

        out.append(line)
        i += 1

    return "\n".join(out).rstrip() + "\n"


def _merge_agent_persona(soul_path: Path, updates: dict[str, str]) -> None:
    if not updates:
        return

    text = soul_path.read_text(encoding="utf-8")
    for key, value in updates.items():
        pattern = rf"^- {re.escape(key)}: .*?$"
        replacement = f"- {key}: {value}"
        if re.search(pattern, text, flags=re.MULTILINE):
            text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
        else:
            marker = "## Agent Persona"
            if marker not in text:
                text = text.rstrip() + "\n\n## Agent Persona\n"
            text = text.rstrip() + "\n" + replacement + "\n"

    soul_path.write_text(_cleanup_pending_markers(text), encoding="utf-8")


def get_agent_persona() -> dict[str, str]:
    soul_path, _, _, _ = ensure_memory_layout()
    text = soul_path.read_text(encoding="utf-8")
    result: dict[str, str] = {}
    for field in PERSONA_FIELDS:
        match = re.search(rf"^- {field}:\s*(.+)$", text, flags=re.MULTILINE)
        if match:
            value = match.group(1).strip()
            if value and value != "(pendiente)":
                result[field] = value
    return result


def get_persona_missing_fields() -> list[str]:
    persona = get_agent_persona()
    return [field for field in PERSONA_FIELDS if not persona.get(field)]


def apply_default_persona() -> dict[str, str]:
    defaults = {
        "Name": "OpenNemesis",
        "Tone": "profesional y cercano",
        "Style": "claro y conciso",
        "Role": "asistente personal para gestionar tareas, correo y calendario",
    }
    soul_path, _, _, _ = ensure_memory_layout()
    _merge_agent_persona(soul_path, defaults)
    return defaults


def _compact_memory_file(memory_path: Path, keep_last_sessions: int = 15) -> None:
    text = memory_path.read_text(encoding="utf-8")
    parts = text.split("\n### Session ")
    if len(parts) <= keep_last_sessions + 1:
        return

    header = parts[0]
    sessions = parts[1:]
    old = sessions[:-keep_last_sessions]
    recent = sessions[-keep_last_sessions:]

    old_ids: list[str] = []
    for chunk in old:
        first_line = chunk.splitlines()[0].strip()
        if first_line:
            old_ids.append(first_line)

    summary_lines = [
        "\n## Historical Summary",
        f"- Sessions compactadas: {len(old)}",
    ]
    if old_ids:
        summary_lines.append(f"- Rango: {old_ids[0]} -> {old_ids[-1]}")

    rebuilt = header.rstrip() + "\n" + "\n".join(summary_lines) + "\n"
    for chunk in recent:
        rebuilt += "\n### Session " + chunk

    memory_path.write_text(rebuilt.rstrip() + "\n", encoding="utf-8")


def _persist_session_sync(buffer: SessionMemoryBuffer) -> None:
    _, _, user_path, memory_path = ensure_memory_layout()
    _append_session_to_memory(memory_path, buffer)
    _compact_memory_file(memory_path)
    hints = _extract_preference_hints(buffer.user_messages)
    _merge_preference_hints(user_path, hints)


async def persist_session_memory(buffer: SessionMemoryBuffer) -> None:
    await asyncio.to_thread(_persist_session_sync, buffer)


async def persist_realtime_user_memory(text: str) -> dict[str, dict[str, str] | list[str] | bool]:
    cleaned = (text or "").strip()
    if not cleaned:
        return {"persona_updates": {}, "user_hints": [], "persona_intent": False}

    result: dict[str, dict[str, str] | list[str] | bool] = {
        "persona_updates": {},
        "user_hints": [],
        "persona_intent": _has_persona_intent(cleaned),
    }

    def _persist_one() -> None:
        soul_path, _, user_path, _ = ensure_memory_layout()
        hints = _extract_preference_hints([cleaned])
        _merge_preference_hints(user_path, hints)
        updates = _extract_agent_persona_updates(cleaned)
        _merge_agent_persona(soul_path, updates)
        result["persona_updates"] = updates
        result["user_hints"] = hints

    await asyncio.to_thread(_persist_one)
    return result


async def persist_persona_from_agent_output(text: str) -> dict[str, str]:
    cleaned = (text or "").strip()
    if not cleaned:
        return {}

    result: dict[str, str] = {}

    def _persist_one() -> None:
        soul_path, _, _, _ = ensure_memory_layout()
        updates = _extract_agent_persona_from_agent_output(cleaned)
        _merge_agent_persona(soul_path, updates)
        result.update(updates)

    await asyncio.to_thread(_persist_one)
    return result
