# CHANGELOG.md - OpenNemesis-Live

## Formato de Commits
`:emoji: tipo(ámbito): descripción` (máx 50 caracteres)

### Tipos y Emojis
| Tipo | Emoji | Descripción |
| :--- | :--- | :--- |
| feat | ✨ | Nueva funcionalidad |
| fix | 🐛 | Corrección de error |
| docs | 📝 | Documentación |
| style | 🎨 | Formato (sin cambio de significado) |
| refactor | ♻️ | Refactorización |
| test | ✅ | Pruebas |
| chore | 🔧 | Herramientas/proceso |

## Historial de Cambios

### [2026-03-31]

- ✨ **feat**: Agente LiveKit operativo
  - 4 tools: weather, time, search, command
  - GOG autenticado para Gmail y Calendar

- 🔧 **fix**: Corregir GOGCLI_PATH
  - Cambiado de `bin/gogcli/gog` a `bin/gogcli`
  - Actualizado status.py para detectar binario correctamente

- 🔧 **fix**: Resolver autenticación GOG
  - Token OAuth expirado
  - Reautenticado con `gog login fontflorida1093@gmail.com --services=gmail,calendar`

- 📝 **docs**: Actualizar documentación
  - SPEC.md con protocolo de Engram
  - Crear MEMORIA.md y CHANGELOG.md
  - Actualizar AGENTS.md

### Pendiente
- Crear cliente web basado en agent-starter-embed
- Desplegar en Vercel
