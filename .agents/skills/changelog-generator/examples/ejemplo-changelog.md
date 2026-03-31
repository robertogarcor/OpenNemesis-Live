# Ejemplo: Generar Changelog

## Uso Básico

```bash
# Ejecutar el script
.agents/skills/changelog-generator/scripts/update_changelog.sh
```

Esto generará un `CHANGELOG.md` con todos los commits del repositorio.

## Salida

El script genera un archivo con el formato:

```markdown
# Changelog

## [2026-03-24]
- commit message (hash)

## [2026-03-23]
- commit message (hash)
```

## Personalizar Archivo de Salida

```bash
# Generar con nombre diferente
.agents/skills/changelog-generator/scripts/update_changelog.sh HISTORY.md
```

## Notas

- El script usa `git log` para obtener los commits
- Formato: `hash|fecha|commit message`
- Organiza por fecha (más reciente primero)
