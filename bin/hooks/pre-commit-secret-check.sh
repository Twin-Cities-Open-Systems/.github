#!/usr/bin/env bash
# Spencer Butler <dev@tcos.us>
# pre-commit-secret-check.sh

set -euo pipefail

# --- RECURSION GUARD ---
if [ "${TCOS_HOOK_RUNNING:-0}" -eq 1 ]; then
    exit 0
fi
export TCOS_HOOK_RUNNING=1

WORKSPACE_DIR="${HOME}/git"
RULES_CONFIG="${WORKSPACE_DIR}/.github/profile/tcos-audit-rules.toml"

mkdir -p "$(dirname "$RULES_CONFIG")"

if [ ! -f "$RULES_CONFIG" ] || ! command -v gitleaks &> /dev/null; then
    exit 0
fi

if ! gitleaks protect --staged --config="$RULES_CONFIG" --verbose; then
    exit 1
fi
