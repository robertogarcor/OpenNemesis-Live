---
name: gog
description: Google Workspace CLI for Gmail, Calendar, Drive, Contacts, Sheets, and Docs.
homepage: https://gogcli.sh
metadata:
  {
    "openclaw":
      {
        "emoji": "🎮",
        "requires": { "bins": ["gog"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "steipete/tap/gogcli",
              "bins": ["gog"],
              "label": "Install gog (brew)",
            },
          ],
      },
  }
---

# gog

Use `gog` for Gmail/Calendar/Drive/Contacts/Sheets/Docs. Requires OAuth setup.

Setup (once)

- `gog auth credentials /path/to/client_secret.json`
- `gog auth add you@gmail.com --services gmail,calendar,drive,contacts,docs,sheets`
- `gog auth list`

Common commands

- Gmail search: `gog gmail search 'newer_than:7d' --max 10`
- Gmail messages search (per email, ignores threading): `gog gmail messages search "in:inbox from:ryanair.com" --max 20 --account you@example.com`
- Gmail send (plain): `gog gmail send --to a@b.com --subject "Hi" --body "Hello"`
- Gmail send (multi-line): `gog gmail send --to a@b.com --subject "Hi" --body-file ./message.txt`
- Gmail send (stdin): `gog gmail send --to a@b.com --subject "Hi" --body-file -`
- Gmail send (HTML): `gog gmail send --to a@b.com --subject "Hi" --body-html "<p>Hello</p>"`
- Gmail draft: `gog gmail drafts create --to a@b.com --subject "Hi" --body-file ./message.txt`
- Gmail send draft: `gog gmail drafts send <draftId>`
- Gmail reply: `gog gmail send --to a@b.com --subject "Re: Hi" --body "Reply" --reply-to-message-id <msgId>`
- Calendar list events: `gog calendar events <calendarId> --from <iso> --to <iso>`
- Calendar create event: `gog calendar create <calendarId> --summary "Title" --from <iso> --to <iso>`
- Calendar create with color: `gog calendar create <calendarId> --summary "Title" --from <iso> --to <iso> --event-color 7`
- Calendar update event: `gog calendar update <calendarId> <eventId> --summary "New Title" --event-color 4`
- Calendar show colors: `gog calendar colors`
- Drive search: `gog drive search "query" --max 10`
- Contacts: `gog contacts list --max 20`
- Sheets get: `gog sheets get <sheetId> "Tab!A1:D10" --json`
- Sheets update: `gog sheets update <sheetId> "Tab!A1:B2" --values-json '[["A","B"],["1","2"]]' --input USER_ENTERED`
- Sheets append: `gog sheets append <sheetId> "Tab!A:C" --values-json '[["x","y","z"]]' --insert INSERT_ROWS`
- Sheets clear: `gog sheets clear <sheetId> "Tab!A2:Z"`
- Sheets metadata: `gog sheets metadata <sheetId> --json`
- Docs export: `gog docs export <docId> --format txt --out /tmp/doc.txt`
- Docs cat: `gog docs cat <docId>`

Calendar Colors

- Use `gog calendar colors` to see all available event colors (IDs 1-11)
- Add colors to events with `--event-color <id>` flag
- Event color IDs (from `gog calendar colors` output):
  - 1: #a4bdfc
  - 2: #7ae7bf
  - 3: #dbadff
  - 4: #ff887c
  - 5: #fbd75b
  - 6: #ffb878
  - 7: #46d6db
  - 8: #e1e1e1
  - 9: #5484ed
  - 10: #51b749
  - 11: #dc2127

Email Formatting

- Prefer plain text. Use `--body-file` for multi-paragraph messages (or `--body-file -` for stdin).
- Same `--body-file` pattern works for drafts and replies.
- `--body` does not unescape `\n`. If you need inline newlines, use a heredoc or `$'Line 1\n\nLine 2'`.
- Use `--body-html` only when you need rich formatting.
- HTML tags: `<p>` for paragraphs, `<br>` for line breaks, `<strong>` for bold, `<em>` for italic, `<a href="url">` for links, `<ul>`/`<li>` for lists.
- Example (plain text via stdin):

  ```bash
  gog gmail send --to recipient@example.com \
    --subject "Meeting Follow-up" \
    --body-file - <<'EOF'
  Hi Name,

  Thanks for meeting today. Next steps:
  - Item one
  - Item two

  Best regards,
  Your Name
  EOF
  ```

- Example (HTML list):
  ```bash
  gog gmail send --to recipient@example.com \
    --subject "Meeting Follow-up" \
    --body-html "<p>Hi Name,</p><p>Thanks for meeting today. Here are the next steps:</p><ul><li>Item one</li><li>Item two</li></ul><p>Best regards,<br>Your Name</p>"
  ```

Notes

- Set `GOG_ACCOUNT=you@gmail.com` to avoid repeating `--account`.
- For scripting, prefer `--json` plus `--no-input`.
- Sheets values can be passed via `--values-json` (recommended) or as inline rows.
- Docs supports export/cat/copy. In-place edits require a Docs API client (not in gog).
- Confirm before sending mail or creating events.
- `gog gmail search` returns one row per thread; use `gog gmail messages search` when you need every individual email returned separately.

## Fechas y Horas (IMPORTANT)

### IMPORTANTE: Antes de crear eventos, usa get_time()

SIEMPRE usa la función get_time() para obtener la fecha y hora actual antes de crear o consultar eventos de calendario.

### Formato de fechas para calendario

- **Timezone**: Europe/Madrid (UTC+1 en invierno, UTC+2 en verano)
- **Formato ISO con timezone**: `YYYY-MM-DDTHH:MM:SS+HH:MM`
- **Para hoy a las 13:00h (Madrid)**: `2026-03-12T13:00:00+01:00`
- **Para hoy a las 15:00h (Madrid)**: `2026-03-12T15:00:00+01:00`

### NO uses UTC (Z)

- **INCORRECTO**: `2026-03-12T13:00:00Z` (esto es UTC)
- **CORRECTO**: `2026-03-12T13:00:00+01:00` (esto es Madrid)

### Ejemplos prácticos

```bash
# Crear evento para hoy 12 de marzo, 13:00-15:00h (Madrid)
gog calendar create primary --summary "Desarrollo OpenNemesis" --from 2026-03-12T13:00:00+01:00 --to 2026-03-12T15:00:00+01:00

# Ver eventos de hoy
gog calendar events primary --from 2026-03-12 --to 2026-03-13

# Ver eventos de esta semana
gog calendar events primary --from 2026-03-12 --to 2026-03-19
```

### Verificación de Conflictos (ANTES de crear eventos)

IMPORTANTE: Antes de crear un evento, SIEMPRE verifica disponibilidad:

1. Verificar si hay eventos en la hora solicitada:
   ```bash
   gog calendar events <calendarId> --from 2026-03-19T15:00:00+01:00 --to 2026-03-19T16:00:00+01:00 --json
   ```

2. Si hay eventos (conflicto):
   - Listar eventos del día completo:
     ```bash
     gog calendar events <calendarId> --from 2026-03-19 --to 2026-03-19 --json
     ```
   - Parsear JSON para calcular horas libres (09:00-20:00, slots de 1h)
   - Informar al usuario del conflicto
   - Proponer horas disponibles
   - Ofrecer actualizar evento existente

3. Si no hay conflicto: crear directamente

### Actualización de Eventos

Para actualizar un evento existente (reutilizar en vez de duplicar):
```bash
gog calendar update <calendarId> <eventId> --summary "Nuevo título" --from <iso> --to <iso> --event-color <id>
```

Para obtener el eventId, busca en la respuesta JSON del comando listar eventos.

### Año actual

**IMPORTANTE**: El año actual es 2026. NO uses 2025 ni otros años.

### Búsqueda de correos ENVIADOS (IMPORTANT)

Para buscar correos que TÚ enviaste:

**USA "from:me" - esto busca correos DESDE tu cuenta**

IMPORTANT: Para obtener los DESTINATARIOS (campo "to"), SIGUE ESTOS PASOS:

**PASO 1 - Buscar mensajes (obtener IDs):**
```bash
gog gmail messages search "from:me after:2026-03-10 before:2026-03-12" --max 10 --json
```

El resultado contendrá una lista de mensajes con: id, threadId, date, from, subject

**PASO 2 - Obtener detalle de cada mensaje (para ver destinatario):**
Para CADA mensaje, ejecuta:
```bash
gog gmail get <message_id> --json
```

Del resultado JSON, busca "To" en: payload.headers

**Ejemplo completo:**
1. `gog gmail messages search "from:me after:2026-03-10 before:2026-03-12" --max 10 --json`
2. `gog gmail get 19cdd363106df43b --json`
3. Del JSON del paso 2, busca: payload.headers -> "To" -> valor

**ERROR COMÚN**: No confundas la búsqueda:
- `from:fontflorida1093@gmail.com` = busca correos DESDE esa persona (no los que tú enviaste)
- `from:me` = busca correos que TÚ enviaste

### Cómo responder "A quién envié"

Cuando el usuario pregunte "A quién envié" o "a quien envié":

1. Ejecuta messages search para obtener IDs
2. Para cada ID, ejecuta "gog gmail get <id> --json"
3. Extrae "To" de payload.headers en cada resultado
4. La respuesta debe ser: "enviaste correos a: [destinatario1], [destinatario2]..."
5. NO digas "desde tu cuenta" - eso no tiene sentido
6. NO digas "te enviaste a ti mismo" - eso es incorrecto

### Búsqueda de correos RECIBIDOS

Para buscar correos que RECIBISTE:

```bash
# Buscar correos no leídos recientes
gog gmail search "is:unread newer_than:1d"

# Buscar correos de un remitente específico
gog gmail search "from:remitente@ejemplo.com"
```
