#!/usr/bin/env bash
# Spencer Butler <dev@tcos.us>
# commit-msg-model-trailer.sh
# Rejects a commit whose message lacks a "Model: <id>" trailer.

set -euo pipefail

MSG_FILE="$1"

if ! grep -qE '^Model: .+' "$MSG_FILE"; then
    echo "  [❌] Commit rejected: missing a 'Model: <id>' trailer." >&2
    echo "       Add a line like 'Model: claude-sonnet-5' to the commit message." >&2
    exit 1
fi
