---
name: github-committer
description: Estandariza la creación de commits en GitHub usando Conventional Commits y un límite de 50 caracteres.
---

# GitHub Committer

Esta habilidad asegura que todos los commits en el repositorio sigan un estándar profesional, legible y consistente.
La rama por defecto es **main**.

## Cuándo usar esta habilidad
- Siempre que necesites realizar un commit de cambios en Git.
- Al colaborar en proyectos que requieran mensajes de commit estructurados.

## Formato del Mensaje de Commit
El formato obligatorio es:
`tipo(ámbito): descripción`

### Tipos
| Tipo | Descripción |
| :--- | :--- |
| **feat** | Una nueva funcionalidad |
| **fix** | Una corrección de error |
| **docs** | Cambios en la documentación |
| **style** | Cambios que no afectan al significado del código (espaciado, formato) |
| **refactor** | Cambio de código que ni corrige un error ni añade una funcionalidad |
| **test** | Añadir o corregir pruebas |
| **chore** | Cambios en el proceso de construcción o herramientas auxiliares |

### Reglas Críticas
1. **Longitud**: La descripción (después del tipo y ámbito) no debe exceder los **50 caracteres**.
2. **Imperativo**: Usa el tiempo imperativo en la descripción (ej: "añadir botón" en lugar de "añadido botón").

## Ejemplo Correcto
`feat(ui): añadir botón de guardado rápido`

## Herramientas
Usa el script `scripts/git-commit-helper.sh` para generar mensajes válidos automáticamente.
