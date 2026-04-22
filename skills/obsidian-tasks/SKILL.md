---
name: obsidian-tasks
description: Gestión local de notas y tareas Markdown en Obsidian.
homepage: https://obsidian.md
metadata:
  {
    "openclaw":
      {
        "emoji": "🧠",
        "requires": { "env": ["OBSIDIAN_VAULT_PATH"] },
      },
  }
---

# obsidian-tasks

Consulta y gestiona tareas Markdown en un vault local de Obsidian.

## Configuración

- Variable requerida: `OBSIDIAN_VAULT_PATH`
- Debe apuntar al directorio raíz del vault.
- Variable opcional: `OBSIDIAN_ALLOWED_BASE_DIRS` (separada por `:` en Linux/macOS)
  - Limita dónde se pueden crear nuevas bóvedas.

Ejemplo:

```bash
export OBSIDIAN_VAULT_PATH="$HOME/Documents/Obsidian"
export OBSIDIAN_ALLOWED_BASE_DIRS="$HOME/obsidean:$HOME/Documents"
```

## Herramientas disponibles

- `obsidian_search(query, limit=5)`
  - Busca notas por texto y devuelve coincidencias con ruta y línea.

- `obsidian_get_vault()`
  - Devuelve información de la bóveda activa (ruta, estado, número de notas).

- `obsidian_set_vault(vault_path)`
  - Cambia la bóveda activa para la sesión actual del agente.
  - No persiste tras reinicio si no se actualiza `.env.local`.

- `obsidian_tasks(note_path="", status="open", limit=20)`
  - Lista tareas en una nota concreta o en todo el vault.
  - `status`: `open`, `done`, `all`.

- `obsidian_add(note_path, task)`
  - Añade una tarea `- [ ]` en la nota indicada.
  - Crea la nota si no existe.

- `obsidian_complete(note_path, task_contains)`
  - Marca como completada la primera tarea abierta que coincida por texto.

- `obsidian_create_vault(vault_name, base_dir="")`
  - Crea una nueva bóveda con estructura mínima (`.obsidian/` + `Bienvenido.md`).
  - Si `base_dir` está vacío, usa el directorio padre del vault actual.
  - Respeta `OBSIDIAN_ALLOWED_BASE_DIRS`.

## Convenciones

- `note_path` es relativo al vault (ejemplo: `daily/2026-04-22.md`).
- Si no se indica extensión, se añade `.md` automáticamente.

## Seguridad

- Todas las rutas se validan dentro del vault.
- No se permite leer o escribir fuera de `OBSIDIAN_VAULT_PATH`.
- No se permite borrar bóvedas ni notas con esta skill.
