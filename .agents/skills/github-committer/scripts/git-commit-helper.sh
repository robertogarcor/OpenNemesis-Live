#!/bin/bash

# git-commit-helper.sh - Genera mensajes de commit con formato Conventional Commits
# Uso: ./git-commit-helper.sh [tipo] [ambito] [mensaje]
# Sin argumentos: modo interactivo

TYPE="$1"
SCOPE="$2"
MESSAGE="$3"

if [ -z "$TYPE" ]; then
    echo "Seleccione el tipo de commit:"
    types=("feat" "fix" "docs" "style" "refactor" "test" "chore")
    i=1
    for t in "${types[@]}"; do
        echo "$i) $t"
        ((i++))
    done
    read -p "Opción: " choice
    TYPE="${types[$((choice-1))]}"
fi

if [ -z "$SCOPE" ]; then
    read -p "Ámbito (opcional, ej: ui, core, deps): " SCOPE
fi

if [ -z "$MESSAGE" ]; then
    read -p "Descripción (máx 50 caracteres): " MESSAGE
fi

if [ ${#MESSAGE} -gt 50 ]; then
    echo "Error: La descripción es demasiado larga (${#MESSAGE} caracteres). Máximo 50."
    exit 1
fi

FINAL_MESSAGE="$TYPE"

if [ -n "$SCOPE" ]; then
    FINAL_MESSAGE+="($SCOPE)"
fi

FINAL_MESSAGE+=": $MESSAGE"

echo ""
echo "Commit sugerido:"
echo "$FINAL_MESSAGE"
echo ""
echo "Comando git sugerido:"
echo "git commit -m \"$FINAL_MESSAGE\""