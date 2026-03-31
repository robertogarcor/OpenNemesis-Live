---
name: changelog-generator
description: Mantiene automáticamente un archivo CHANGELOG.md basado en el historial de commits de Git.
---

# ChangeLog Generator

Esta habilidad permite generar y mantener actualizado un archivo `CHANGELOG.md` extrayendo la información directamente de los commits del repositorio Git.

## Cuándo usar esta habilidad
- Después de realizar uno o varios commits para reflejar los cambios en el historial.
- Cuando el usuario solicite ver un resumen de los cambios recientes.
- Al preparar una nueva versión o entrega del proyecto.

## Cómo usarla
1. **Actualizar el Changelog**: Ejecuta el script de Bash proporcionado.
   ```bash
   bash .agents/skills/changelog-generator/scripts/update-changelog.sh
   ```
## Estructura del Changelog
El archivo generado sigue un formato simple y legible:
- Encabezados de nivel 2 con la fecha del commit `## [YYYY-MM-DD]`.
- Lista de cambios con el mensaje del commit y el hash corto `- Mensaje (hash)`.

## Consideraciones
- La habilidad asume que el repositorio utiliza Git.
- Los mensajes de commit descriptivos mejoran la calidad del `CHANGELOG.md`.
