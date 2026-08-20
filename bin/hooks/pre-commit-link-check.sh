#!/usr/bin/env bash
# Spencer Butler <dev@tcos.us>
# pre-commit-link-check.sh

set -euo pipefail

# --- RECURSION GUARD ---
if [ "${TCOS_HOOK_RUNNING:-0}" -eq 1 ]; then
    exit 0
fi
export TCOS_HOOK_RUNNING=1

TARGET_ORG="Twin-Cities-Open-Systems"
VIOLATIONS=0
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.md$' || true)

if [ -z "$STAGED_FILES" ]; then
    exit 0
fi

for file in $STAGED_FILES; do
    if [ -f "$file" ] && grep -qE "https://github\\.com/${TARGET_ORG}/" "$file"; then
        echo "  [❌] Compliance Failure in '$file': Use relative repo paths."
        VIOLATIONS=$((VIOLATIONS + 1))
    fi
done

if [ "$VIOLATIONS" -gt 0 ]; then
    exit 1
fi
