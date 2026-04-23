import os
from pathlib import Path

import pytest

from tools import obsidian_tools


def test_resolve_vault_path_accepts_existing_absolute_dir(tmp_path):
    vault_dir = tmp_path / "MiVault"
    vault_dir.mkdir()

    resolved = obsidian_tools._resolve_vault_path(str(vault_dir))
    assert resolved == vault_dir.resolve()


def test_resolve_vault_path_finds_vault_by_name_in_allowed_bases(monkeypatch, tmp_path):
    allowed_base = tmp_path / "allowed"
    allowed_base.mkdir()
    target = allowed_base / "Trabajo"
    target.mkdir()

    monkeypatch.setenv("OBSIDIAN_ALLOWED_BASE_DIRS", str(allowed_base))
    resolved = obsidian_tools._resolve_vault_path("Trabajo")

    assert resolved == target.resolve()


def test_resolve_vault_path_raises_when_not_found(monkeypatch, tmp_path):
    allowed_base = tmp_path / "allowed"
    allowed_base.mkdir()
    monkeypatch.setenv("OBSIDIAN_ALLOWED_BASE_DIRS", str(allowed_base))

    with pytest.raises(FileNotFoundError):
        obsidian_tools._resolve_vault_path("NoExiste")


def test_set_active_vault_accepts_name_and_updates_env(monkeypatch, tmp_path):
    allowed_base = tmp_path / "allowed"
    allowed_base.mkdir()
    vault = allowed_base / "Personal"
    vault.mkdir()
    (vault / ".obsidian").mkdir()

    monkeypatch.setenv("OBSIDIAN_ALLOWED_BASE_DIRS", str(allowed_base))
    result = obsidian_tools.set_active_vault("Personal")

    assert result.startswith("Bóveda activa actualizada")
    assert Path(os.getenv("OBSIDIAN_VAULT_PATH", "")) == vault.resolve()
