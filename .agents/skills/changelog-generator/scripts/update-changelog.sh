#!/bin/bash

# update_changelog.sh - Genera CHANGELOG.md desde el historial de Git
# Uso: ./update_changelog.sh [archivo_changelog]
# Por defecto: CHANGELOG.md

CHANGELOG_FILE="${1:-CHANGELOG.md}"

commits=$(git log --pretty=format:"%h|%ad|%s" --date=short 2>/dev/null)

if [ -z "$commits" ]; then
    echo "No commits found."
    exit 1
fi

echo "# Changelog" > "$CHANGELOG_FILE"
echo "" >> "$CHANGELOG_FILE"

current_date=""

while IFS='|' read -r hash date subject; do
    if [ "$date" != "$current_date" ]; then
        echo "## [$date]" >> "$CHANGELOG_FILE"
        current_date="$date"
    fi
    echo "- $subject ($hash)" >> "$CHANGELOG_FILE"
done <<< "$commits"

count=$(echo "$commits" | wc -l)
echo "Updated $CHANGELOG_FILE with $count commits."