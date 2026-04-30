from pathlib import Path

from data.file_memory import (
    SessionMemoryBuffer,
    _extract_agent_persona_from_agent_output,
    _extract_preference_hints,
    _extract_agent_persona_updates,
    _has_persona_intent,
    apply_default_persona,
    build_file_memory_context,
    ensure_memory_layout,
    get_persona_missing_fields,
    persist_persona_from_agent_output,
    persist_session_memory,
    persist_realtime_user_memory,
)


def test_ensure_memory_layout_creates_files(monkeypatch, tmp_path):
    from data import file_memory

    monkeypatch.setattr(file_memory, "MEMORY_BASE_DIR", tmp_path / "memory")
    monkeypatch.setattr(file_memory, "USER_PATH", tmp_path / "memory" / "USER.md")
    monkeypatch.setattr(file_memory, "MEMORY_PATH", tmp_path / "memory" / "MEMORY.md")

    soul, rules, user, memory = ensure_memory_layout()

    assert soul.exists()
    assert rules.exists()
    assert user.exists()
    assert memory.exists()


def test_build_file_memory_context_contains_sections(monkeypatch, tmp_path):
    from data import file_memory

    monkeypatch.setattr(file_memory, "MEMORY_BASE_DIR", tmp_path / "memory")
    monkeypatch.setattr(file_memory, "USER_PATH", tmp_path / "memory" / "USER.md")
    monkeypatch.setattr(file_memory, "MEMORY_PATH", tmp_path / "memory" / "MEMORY.md")

    context = build_file_memory_context()

    assert "=== MEMORIA CURADA DE LARGO PLAZO ===" in context
    assert "## SOUL" in context
    assert "## USER" in context


def test_persist_session_memory_appends_notes(monkeypatch, tmp_path):
    from data import file_memory

    monkeypatch.setattr(file_memory, "MEMORY_BASE_DIR", tmp_path / "memory")
    monkeypatch.setattr(file_memory, "USER_PATH", tmp_path / "memory" / "USER.md")
    monkeypatch.setattr(file_memory, "MEMORY_PATH", tmp_path / "memory" / "MEMORY.md")

    buffer = SessionMemoryBuffer()
    buffer.add_user("prefiero respuestas breves")
    buffer.add_assistant("Entendido")

    import asyncio

    asyncio.run(persist_session_memory(buffer))

    memory_md = (tmp_path / "memory" / "MEMORY.md").read_text(encoding="utf-8")
    user_md = (tmp_path / "memory" / "USER.md").read_text(encoding="utf-8")

    assert "Session" in memory_md
    assert "prefiero respuestas breves" in memory_md
    assert "prefiero respuestas breves" in user_md


def test_extract_preference_hints_detects_name_and_profession():
    hints = _extract_preference_hints([
        "Me llamo Roberto",
        "Trabajo como desarrollador backend",
    ])
    assert "Nombre: Roberto" in hints
    assert "Profesion: desarrollador backend" in hints


def test_extract_preference_hints_trims_name_with_extra_text():
    hints = _extract_preference_hints(["Me llamo Roberto y soy programador"])
    assert "Nombre: Roberto" in hints


def test_persist_realtime_user_memory_updates_user_md(monkeypatch, tmp_path):
    from data import file_memory

    monkeypatch.setattr(file_memory, "MEMORY_BASE_DIR", tmp_path / "memory")
    monkeypatch.setattr(file_memory, "USER_PATH", tmp_path / "memory" / "USER.md")
    monkeypatch.setattr(file_memory, "MEMORY_PATH", tmp_path / "memory" / "MEMORY.md")

    import asyncio

    asyncio.run(persist_realtime_user_memory("Me llamo Ana"))
    asyncio.run(persist_realtime_user_memory("Soy ingeniera de datos"))

    user_md = (tmp_path / "memory" / "USER.md").read_text(encoding="utf-8")
    assert "Nombre: Ana" in user_md
    assert "Profesion: ingeniera de datos" in user_md


def test_extract_agent_persona_updates_detects_fields():
    updates = _extract_agent_persona_updates(
        "Te llamas Nox y quiero que hables en tono directo. Actua como mentor tecnico"
    )
    assert updates.get("Name") == "Nox"
    assert "directo" in (updates.get("Tone") or "")
    assert "mentor tecnico" in (updates.get("Role") or "")


def test_extract_agent_persona_updates_detects_natural_and_command_forms():
    natural = _extract_agent_persona_updates("Quiero que hables mas directo y breve")
    assert natural.get("Tone") in {"directo", "serio", "profesional", "cercano", "formal", "amigable"}
    assert natural.get("Style") in {"breve", "conciso", "detallado", "tecnico", "técnico", "didactico", "didáctico"}

    explicit = _extract_agent_persona_updates("config agente nombre=Nova tono=formal estilo=conciso rol=mentor")
    assert explicit.get("Name") == "Nova"
    assert explicit.get("Tone") == "formal"
    assert explicit.get("Style") == "conciso"
    assert explicit.get("Role") == "mentor"


def test_extract_agent_persona_updates_detects_indirect_name_request():
    updates = _extract_agent_persona_updates("Tu nombre me gustaria que fuese Niobe, que te parece?")
    assert updates.get("Name") == "Niobe"


def test_extract_agent_persona_from_agent_output_detects_style():
    updates = _extract_agent_persona_from_agent_output(
        "Mi estilo de asistencia, que he elegido, es profesional, directo y proactivo."
    )
    assert "profesional" in (updates.get("Style") or "")


def test_extract_agent_persona_updates_keeps_long_role_phrase():
    text = "Actua como mi asistente personal para gestionar correo, calendario, tareas y proyectos"
    updates = _extract_agent_persona_updates(text)
    assert "correo, calendario, tareas" in (updates.get("Role") or "")
    assert updates.get("Style") == "claro y conciso"


def test_has_persona_intent_detects_persona_language():
    assert _has_persona_intent("Te llamas Atlas") is True
    assert _has_persona_intent("Config agente nombre=Atlas") is True
    assert _has_persona_intent("Que tiempo hace en Madrid") is False


def test_persist_realtime_user_memory_updates_soul_persona(monkeypatch, tmp_path):
    from data import file_memory

    monkeypatch.setattr(file_memory, "MEMORY_BASE_DIR", tmp_path / "memory")
    monkeypatch.setattr(file_memory, "USER_PATH", tmp_path / "memory" / "USER.md")
    monkeypatch.setattr(file_memory, "MEMORY_PATH", tmp_path / "memory" / "MEMORY.md")

    import asyncio

    result = asyncio.run(persist_realtime_user_memory("Te llamas Atlas"))
    asyncio.run(persist_realtime_user_memory("Actua como arquitecto software"))

    soul_md = (tmp_path / "memory" / "SOUL.md").read_text(encoding="utf-8")
    assert result["persona_updates"]
    assert result["persona_intent"] is True
    assert "- Name: Atlas" in soul_md
    assert "- Role: arquitecto software" in soul_md


def test_persona_missing_fields_and_defaults(monkeypatch, tmp_path):
    from data import file_memory

    monkeypatch.setattr(file_memory, "MEMORY_BASE_DIR", tmp_path / "memory")
    monkeypatch.setattr(file_memory, "USER_PATH", tmp_path / "memory" / "USER.md")
    monkeypatch.setattr(file_memory, "MEMORY_PATH", tmp_path / "memory" / "MEMORY.md")

    missing = get_persona_missing_fields()
    assert set(missing) == {"Name", "Tone", "Style", "Role"}

    defaults = apply_default_persona()
    assert defaults["Name"] == "OpenNemesis"
    assert get_persona_missing_fields() == []


def test_persist_persona_from_agent_output_updates_soul(monkeypatch, tmp_path):
    from data import file_memory

    monkeypatch.setattr(file_memory, "MEMORY_BASE_DIR", tmp_path / "memory")
    monkeypatch.setattr(file_memory, "USER_PATH", tmp_path / "memory" / "USER.md")
    monkeypatch.setattr(file_memory, "MEMORY_PATH", tmp_path / "memory" / "MEMORY.md")

    import asyncio

    updates = asyncio.run(
        persist_persona_from_agent_output(
            "Mi estilo de asistencia es profesional, directo y proactivo."
        )
    )

    soul_md = (tmp_path / "memory" / "SOUL.md").read_text(encoding="utf-8")
    assert updates.get("Style")
    assert "Style:" in soul_md
