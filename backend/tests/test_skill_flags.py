from tools import tools


def _tool_names(active_tools):
    return {tool.__name__ for tool in active_tools}


def test_parse_enabled_skills_empty_returns_none(monkeypatch):
    monkeypatch.setenv("ENABLED_SKILLS", "")
    assert tools._parse_enabled_skills() is None


def test_parse_enabled_skills_normalizes_values(monkeypatch):
    monkeypatch.setenv("ENABLED_SKILLS", " gog, Obsidian-Tasks ,gog ")
    assert tools._parse_enabled_skills() == {"gog", "obsidian-tasks"}


def test_get_active_tools_with_all_enabled_by_default(monkeypatch):
    monkeypatch.delenv("ENABLED_SKILLS", raising=False)
    names = _tool_names(tools.get_active_tools())

    assert {"weather", "time", "search"}.issubset(names)
    assert "command" in names
    assert "obsidian_tasks_in_vault" in names


def test_get_active_tools_only_gog(monkeypatch):
    monkeypatch.setenv("ENABLED_SKILLS", "gog")
    names = _tool_names(tools.get_active_tools())

    assert {"weather", "time", "search", "command"}.issubset(names)
    assert "obsidian_tasks" not in names
    assert "obsidian_tasks_in_vault" not in names


def test_get_active_tools_only_obsidian(monkeypatch):
    monkeypatch.setenv("ENABLED_SKILLS", "obsidian-tasks")
    names = _tool_names(tools.get_active_tools())

    assert {"weather", "time", "search"}.issubset(names)
    assert "command" not in names
    assert "obsidian_tasks" in names
    assert "obsidian_tasks_in_vault" in names
