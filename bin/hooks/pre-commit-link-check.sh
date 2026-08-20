#!/usr/bin/env bash
# Spencer Butler <dev@tcos.us>
# pre-commit-link-check.sh
# Validates that staged markdown assets utilize safe relative repo paths.

set -euo pipefail

TARGET_ORG="Twin-Cities-Open-Systems"
VIOLATIONS=0

# Locate files staged for commit matching the markdown asset class
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.md$' || true)

if [ -z "$STAGED_FILES" ]; then
    exit 0
fi

echo "[*] TCOS Audit: Scanning staged markdown nodes for absolute URL violations..."

for file in $STAGED_FILES; do
    if [ -f "$file" ]; then
        # Check for absolute link patterns pointing to organization repos
        if grep -qE "https://github\\.com/${TARGET_ORG}/" "$file"; then
            echo "  [❌] Compliance Failure in '$file': Absolute repo URL pattern detected."
            echo "       Rule Invariant: Use relative paths (e.g., '../repo-name') to ensure permission masking."
            VIOLATIONS=$((VIOLATIONS + 1))
        fi
    fi
done

if [ "$VIOLATIONS" -gt 0 ]; then
    echo "================================================================================"
    echo "[❌] Commit rejected: $VIOLATIONS documentation formatting invariant broken."
    echo "================================================================================"
    exit 1
fi

exit 0

