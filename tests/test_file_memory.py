from pathlib import Path

from data.file_memory import (
    SessionMemoryBuffer,
    _safe_user_id,
    build_file_memory_context,
    ensure_memory_layout,
    persist_session_memory,
)


def test_safe_user_id_normalizes_chars():
    assert _safe_user_id("user 1/2") == "user_1_2"


def test_ensure_memory_layout_creates_files(monkeypatch, tmp_path):
    from data import file_memory

    monkeypatch.setattr(file_memory, "MEMORY_BASE_DIR", tmp_path / "memory")
    monkeypatch.setattr(file_memory, "USERS_DIR", tmp_path / "memory" / "users")

    soul, rules, user, memory = ensure_memory_layout("demo-user")

    assert soul.exists()
    assert rules.exists()
    assert user.exists()
    assert memory.exists()


def test_build_file_memory_context_contains_sections(monkeypatch, tmp_path):
    from data import file_memory

    monkeypatch.setattr(file_memory, "MEMORY_BASE_DIR", tmp_path / "memory")
    monkeypatch.setattr(file_memory, "USERS_DIR", tmp_path / "memory" / "users")

    context = build_file_memory_context("demo-user")

    assert "=== MEMORIA CURADA DE LARGO PLAZO ===" in context
    assert "## SOUL" in context
    assert "## USER" in context


def test_persist_session_memory_appends_notes(monkeypatch, tmp_path):
    from data import file_memory

    monkeypatch.setattr(file_memory, "MEMORY_BASE_DIR", tmp_path / "memory")
    monkeypatch.setattr(file_memory, "USERS_DIR", tmp_path / "memory" / "users")

    buffer = SessionMemoryBuffer()
    buffer.add_user("prefiero respuestas breves")
    buffer.add_assistant("Entendido")

    import asyncio

    asyncio.run(persist_session_memory("demo-user", buffer))

    user_dir = tmp_path / "memory" / "users" / "demo-user"
    memory_md = (user_dir / "MEMORY.md").read_text(encoding="utf-8")
    user_md = (user_dir / "USER.md").read_text(encoding="utf-8")

    assert "Session" in memory_md
    assert "prefiero respuestas breves" in memory_md
    assert "prefiero respuestas breves" in user_md
