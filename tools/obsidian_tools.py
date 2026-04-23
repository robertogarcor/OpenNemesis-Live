import logging
import os
import re
from pathlib import Path
from typing import List, Tuple

from livekit.agents import RunContext, function_tool

logger = logging.getLogger("OpenNemesis-Live.ObsidianTools")

TASK_PATTERN = re.compile(r"^(\s*[-*]\s\[)( |x|X)(\]\s)(.+)$")
VAULT_NAME_PATTERN = re.compile(r"^[\w\-. ]+$")


def _is_within_dir(path: Path, base: Path) -> bool:
    return path == base or base in path.parents


def _get_obsidian_vault_path() -> Path:
    raw_path = os.getenv("OBSIDIAN_VAULT_PATH", "").strip()
    if not raw_path:
        return Path.home() / "Documents" / "Obsidian"
    return Path(raw_path).expanduser().resolve()


def _get_allowed_base_dirs() -> List[Path]:
    raw = os.getenv("OBSIDIAN_ALLOWED_BASE_DIRS", "").strip()
    allowed: List[Path] = []

    if raw:
        for chunk in raw.split(os.pathsep):
            chunk = chunk.strip()
            if not chunk:
                continue
            try:
                allowed.append(Path(chunk).expanduser().resolve())
            except Exception:
                continue

    # Fallbacks seguros por defecto
    fallback = [
        _get_default_vault_base_dir().resolve(),
        (Path.home() / "obsidean").resolve(),
    ]
    for candidate in fallback:
        if candidate not in allowed:
            allowed.append(candidate)

    return allowed


def _resolve_vault_path(vault_ref: str) -> Path:
    """Resuelve una referencia de bóveda por ruta absoluta o por nombre."""
    cleaned = vault_ref.strip()
    if not cleaned:
        raise ValueError("Debes indicar una ruta o nombre de bóveda.")

    # Ruta absoluta/relativa existente
    direct = Path(cleaned).expanduser().resolve()
    if direct.exists() and direct.is_dir():
        return direct

    # Si parece nombre de bóveda, probar en bases permitidas
    if VAULT_NAME_PATTERN.match(cleaned):
        for base in _get_allowed_base_dirs():
            candidate = (base / cleaned).resolve()
            if candidate.exists() and candidate.is_dir():
                return candidate

    raise FileNotFoundError(f"No encontré la bóveda: {cleaned}")


def _validate_note_path(note_path: str) -> Path:
    vault_path = _get_obsidian_vault_path()
    if not vault_path.exists() or not vault_path.is_dir():
        raise FileNotFoundError(f"Vault de Obsidian no disponible: {vault_path}")

    cleaned = note_path.strip()
    if not cleaned:
        raise ValueError("Debes indicar la ruta de la nota.")

    relative = Path(cleaned)
    if relative.suffix == "":
        relative = relative.with_suffix(".md")

    candidate = (vault_path / relative).resolve()
    if vault_path not in candidate.parents and candidate != vault_path:
        raise ValueError("Ruta fuera del vault de Obsidian.")

    return candidate


def _get_default_vault_base_dir() -> Path:
    vault_path = _get_obsidian_vault_path()
    if vault_path.exists() and vault_path.is_dir():
        return vault_path.parent
    return Path.home() / "obsidean"


def _validate_base_dir(base_dir: str) -> Path:
    if base_dir.strip():
        candidate = Path(base_dir).expanduser().resolve()
    else:
        candidate = _get_default_vault_base_dir().resolve()

    allowed = _get_allowed_base_dirs()
    if not any(_is_within_dir(candidate, base) for base in allowed):
        allowed_msg = ", ".join(str(p) for p in allowed)
        raise ValueError(
            f"Base dir no permitida: {candidate}. Directorios permitidos: {allowed_msg}"
        )

    candidate.mkdir(parents=True, exist_ok=True)
    return candidate


def get_active_vault_info() -> str:
    """Devuelve información de la bóveda activa."""
    try:
        vault_path = _get_obsidian_vault_path()
        exists = vault_path.exists() and vault_path.is_dir()
        has_obsidian_dir = (vault_path / ".obsidian").exists() if exists else False
        note_count = len(list(vault_path.rglob("*.md"))) if exists else 0
        return (
            "Bóveda activa:\n"
            f"- Ruta: {vault_path}\n"
            f"- Existe: {'sí' if exists else 'no'}\n"
            f"- Tiene .obsidian: {'sí' if has_obsidian_dir else 'no'}\n"
            f"- Notas .md: {note_count}"
        )
    except Exception as e:
        logger.error(f"Error consultando bóveda activa: {e}")
        return f"Error: {e}"


def set_active_vault(vault_path: str) -> str:
    """Cambia la bóveda activa para la sesión actual del agente."""
    try:
        cleaned = vault_path.strip()
        if not cleaned:
            return "Error: debes indicar una ruta de bóveda."

        try:
            candidate = _resolve_vault_path(cleaned)
        except Exception as e:
            return f"Error: {e}"

        obsidian_dir = candidate / ".obsidian"
        if not obsidian_dir.exists() or not obsidian_dir.is_dir():
            return (
                f"Error: la ruta no parece una bóveda de Obsidian (falta .obsidian): {candidate}"
            )

        os.environ["OBSIDIAN_VAULT_PATH"] = str(candidate)
        return (
            "Bóveda activa actualizada para esta sesión del agente.\n"
            f"- Ruta activa: {candidate}\n"
            "Nota: este cambio no persiste tras reiniciar; para persistir, actualiza .env.local"
        )
    except Exception as e:
        logger.error(f"Error cambiando bóveda activa: {e}")
        return f"Error: {e}"


def _iter_markdown_files(vault_path: Path) -> List[Path]:
    return sorted(vault_path.rglob("*.md"))


def search_notes(query: str, limit: int = 5) -> str:
    """Busca notas Markdown dentro del vault de Obsidian por texto."""
    try:
        if not query.strip():
            return "Error: query vacía"

        vault_path = _get_obsidian_vault_path()
        if not vault_path.exists() or not vault_path.is_dir():
            return f"Error: Vault de Obsidian no disponible: {vault_path}"

        matches: List[Tuple[Path, int, str]] = []
        query_lower = query.lower()

        # 1) Priorizar coincidencias por nombre de archivo
        for note in _iter_markdown_files(vault_path):
            if query_lower in note.stem.lower() or query_lower in note.name.lower():
                rel = note.relative_to(vault_path)
                matches.append((rel, 0, "[coincidencia en nombre de archivo]"))
            if len(matches) >= max(1, limit):
                break

        # 2) Completar con coincidencias por contenido
        for note in _iter_markdown_files(vault_path):
            rel = note.relative_to(vault_path)
            if any(existing[0] == rel for existing in matches):
                continue
            try:
                content = note.read_text(encoding="utf-8")
            except Exception:
                continue

            for line_number, line in enumerate(content.splitlines(), start=1):
                if query_lower in line.lower():
                    matches.append((rel, line_number, line.strip()))
                    break

            if len(matches) >= max(1, limit):
                break

        if not matches:
            return f"No encontré notas para '{query}'."

        formatted_lines = []
        for path, line_number, snippet in matches:
            if line_number == 0:
                formatted_lines.append(f"- {path}: {snippet}")
            else:
                formatted_lines.append(f"- {path} (linea {line_number}): {snippet[:140]}")
        formatted = "\n".join(formatted_lines)
        return f"Resultados en Obsidian ({len(matches)}):\n{formatted}"
    except Exception as e:
        logger.error(f"Error buscando notas en Obsidian: {e}")
        return f"Error: {e}"


def list_tasks(note_path: str = "", status: str = "open", limit: int = 20) -> str:
    """Lista tareas de Obsidian en una nota concreta o en todo el vault."""
    try:
        vault_path = _get_obsidian_vault_path()
        if not vault_path.exists() or not vault_path.is_dir():
            return f"Error: Vault de Obsidian no disponible: {vault_path}"

        status_clean = status.lower().strip()
        if status_clean not in {"open", "done", "all"}:
            return "Error: status debe ser open, done o all"

        files: List[Path]
        if note_path.strip():
            note = _validate_note_path(note_path)
            if not note.exists():
                return f"Error: no existe la nota {note}"
            files = [note]
        else:
            files = _iter_markdown_files(vault_path)

        tasks: List[str] = []
        for note in files:
            try:
                lines = note.read_text(encoding="utf-8").splitlines()
            except Exception:
                continue

            rel = note.relative_to(vault_path)
            for idx, line in enumerate(lines, start=1):
                m = TASK_PATTERN.match(line)
                if not m:
                    continue

                marker = m.group(2).lower()
                is_done = marker == "x"
                if status_clean == "open" and is_done:
                    continue
                if status_clean == "done" and not is_done:
                    continue

                tasks.append(f"- [{marker}] {m.group(4).strip()} ({rel}:{idx})")
                if len(tasks) >= max(1, limit):
                    break

            if len(tasks) >= max(1, limit):
                break

        if not tasks:
            scope = note_path.strip() or "todo el vault"
            return f"No encontré tareas ({status_clean}) en {scope}."

        return f"Tareas ({status_clean}) encontradas:\n" + "\n".join(tasks)
    except Exception as e:
        logger.error(f"Error listando tareas de Obsidian: {e}")
        return f"Error: {e}"


def add_task(note_path: str, task: str) -> str:
    """Agrega una tarea abierta en una nota de Obsidian."""
    try:
        note = _validate_note_path(note_path)
        vault_path = _get_obsidian_vault_path()
        task_clean = task.strip()
        if not task_clean:
            return "Error: la tarea está vacía"

        note.parent.mkdir(parents=True, exist_ok=True)
        prefix = "\n" if note.exists() and note.read_text(encoding="utf-8").strip() else ""
        with note.open("a", encoding="utf-8") as f:
            f.write(f"{prefix}- [ ] {task_clean}\n")

        rel = note.relative_to(vault_path)
        return f"Tarea añadida en {rel}: {task_clean}"
    except Exception as e:
        logger.error(f"Error agregando tarea en Obsidian: {e}")
        return f"Error: {e}"


def complete_task(note_path: str, task_contains: str) -> str:
    """Marca como completada la primera tarea abierta que coincida por texto."""
    try:
        note = _validate_note_path(note_path)
        if not note.exists():
            return f"Error: no existe la nota {note}"

        needle = task_contains.strip().lower()
        if not needle:
            return "Error: task_contains está vacío"

        lines = note.read_text(encoding="utf-8").splitlines()
        updated = False
        completed_text = ""

        for idx, line in enumerate(lines):
            m = TASK_PATTERN.match(line)
            if not m:
                continue
            is_done = m.group(2).lower() == "x"
            text = m.group(4).strip()
            if is_done:
                continue
            if needle in text.lower():
                lines[idx] = f"{m.group(1)}x{m.group(3)}{text}"
                updated = True
                completed_text = text
                break

        if not updated:
            return f"No encontré una tarea abierta que contenga: '{task_contains}'."

        note.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return f"Tarea completada: {completed_text}"
    except Exception as e:
        logger.error(f"Error completando tarea en Obsidian: {e}")
        return f"Error: {e}"


def create_vault(vault_name: str, base_dir: str = "") -> str:
    """Crea una nueva bóveda de Obsidian con estructura mínima."""
    try:
        name = vault_name.strip()
        if not name:
            return "Error: vault_name está vacío"
        if not VAULT_NAME_PATTERN.match(name):
            return "Error: nombre de bóveda inválido. Usa letras, números, espacios, guiones o guion bajo."

        base = _validate_base_dir(base_dir)
        vault_path = (base / name).resolve()

        if vault_path.exists():
            return f"Error: ya existe una bóveda en {vault_path}"

        vault_path.mkdir(parents=True, exist_ok=False)
        (vault_path / ".obsidian").mkdir(parents=True, exist_ok=True)

        welcome = vault_path / "Bienvenido.md"
        welcome.write_text(
            "# Bienvenido\n\n"
            "Esta bóveda fue creada por OpenNemesis.\n"
            "- [ ] Primer tarea\n",
            encoding="utf-8",
        )

        return (
            "Bóveda creada correctamente.\n"
            f"- Ruta absoluta: {vault_path}\n"
            f"- Base usada: {base}\n"
            "Para usarla como bóveda activa, ejecuta obsidian_set_vault con esa ruta "
            "o actualiza OBSIDIAN_VAULT_PATH en .env.local."
        )
    except Exception as e:
        logger.error(f"Error creando bóveda Obsidian: {e}")
        return f"Error: {e}"


def list_tasks_in_vault(vault_path: str, status: str = "open", limit: int = 20) -> str:
    """Cambia a una bóveda y lista sus tareas en una sola operación."""
    change_result = set_active_vault(vault_path)
    if change_result.startswith("Error:"):
        return change_result
    tasks_result = list_tasks(note_path="", status=status, limit=limit)
    return f"{change_result}\n\n{tasks_result}"


@function_tool
async def obsidian_search(ctx: RunContext, query: str, limit: int = 5) -> str:
    """Busca notas en Obsidian por texto y devuelve coincidencias."""
    return search_notes(query, limit=limit)


@function_tool
async def obsidian_tasks(ctx: RunContext, note_path: str = "", status: str = "open", limit: int = 20) -> str:
    """Lista tareas de Obsidian.

    - Si note_path está vacío: lista tareas de toda la bóveda activa.
    - Si note_path tiene valor: filtra por esa nota.
    """
    return list_tasks(note_path=note_path, status=status, limit=limit)


@function_tool
async def obsidian_tasks_vault(ctx: RunContext, status: str = "open", limit: int = 20) -> str:
    """Lista tareas de toda la bóveda activa de Obsidian."""
    return list_tasks(note_path="", status=status, limit=limit)


@function_tool
async def obsidian_add(ctx: RunContext, note_path: str, task: str) -> str:
    """Agrega una nueva tarea en una nota de Obsidian."""
    return add_task(note_path=note_path, task=task)


@function_tool
async def obsidian_complete(ctx: RunContext, note_path: str, task_contains: str) -> str:
    """Marca como completada una tarea en Obsidian por coincidencia de texto."""
    return complete_task(note_path=note_path, task_contains=task_contains)


@function_tool
async def obsidian_get_vault(ctx: RunContext) -> str:
    """Devuelve información de la bóveda activa de Obsidian."""
    return get_active_vault_info()


@function_tool
async def obsidian_set_vault(ctx: RunContext, vault_path: str) -> str:
    """Cambia la bóveda activa de Obsidian para la sesión actual del agente."""
    return set_active_vault(vault_path=vault_path)


@function_tool
async def obsidian_create_vault(ctx: RunContext, vault_name: str, base_dir: str = "") -> str:
    """Crea una nueva bóveda de Obsidian con estructura mínima."""
    return create_vault(vault_name=vault_name, base_dir=base_dir)


@function_tool
async def obsidian_tasks_in_vault(
    ctx: RunContext, vault_path: str, status: str = "open", limit: int = 20
) -> str:
    """Lista tareas de una bóveda específica (por ruta o nombre)."""
    return list_tasks_in_vault(vault_path=vault_path, status=status, limit=limit)


OBSIDIAN_TOOLS = [
    obsidian_get_vault,
    obsidian_set_vault,
    obsidian_search,
    obsidian_tasks_vault,
    obsidian_tasks,
    obsidian_add,
    obsidian_complete,
    obsidian_create_vault,
    obsidian_tasks_in_vault,
]
