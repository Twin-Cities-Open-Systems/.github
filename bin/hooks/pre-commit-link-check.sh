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
    if [ -f "$file" ]; then
        # Narrowed 2026-08-27 after a real conflict with HEE_POLICY.md's
        # Real-Link Requirement (HEE Policy section 5): a same-repo doc
        # cross-reference can reasonably use a relative path, but a real
        # issue/PR reference or a versioned file link (/blob/) has no
        # sensible relative form and must stay a full URL -- exempt those
        # instead of blocking them.
        HITS=$(grep -E "https://github\\.com/${TARGET_ORG}/" "$file" | grep -vE '/(issues|pull|blob)/' || true)
        if [ -n "$HITS" ]; then
            echo "  [❌] Compliance Failure in '$file': Use relative repo paths."
            VIOLATIONS=$((VIOLATIONS + 1))
        fi
    fi
done

if [ "$VIOLATIONS" -gt 0 ]; then
    exit 1
fi
