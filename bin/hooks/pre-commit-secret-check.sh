#!/usr/bin/env bash
# Spencer Butler <dev@tcos.us>
# pre-commit-secret-check.sh
# Scans staged workspace file increments against centralized TCOS leak definitions.

set -euo pipefail

WORKSPACE_DIR="${HOME}/git"
RULES_CONFIG="${WORKSPACE_DIR}/.github/profile/tcos-audit-rules.toml"

# Ensure target configuration parent directory structures exist cleanly
mkdir -p "$(dirname "$RULES_CONFIG")"

if [ ! -f "$RULES_CONFIG" ]; then
    echo "[⚠️] Audit Warning: Centralized rules block missing at $RULES_CONFIG. Skipping scan."
    exit 0
fi

# Verify Gitleaks engine presence on system
if ! command -v gitleaks &> /dev/null; then
    echo "[⚠️] Audit Warning: 'gitleaks' binary not detected in PATH."
    echo "    Install via your system manager (e.g., 'brew install gitleaks' or 'apt install gitleaks')."
    echo "    Skipping runtime checks to preserve loop execution."
    exit 0
fi

echo "[*] TCOS Audit: Running static credential compliance validation loop..."

# Execute gitleaks natively against staged assets only to optimize performance
if ! gitleaks protect --staged --config="$RULES_CONFIG" --verbose; then
    echo "================================================================================"
    echo "[❌] CRITICAL COMPLIANCE FAILURE: Secret or protected identity signature detected!"
    echo "     Commit rejected by organizational custodian policy rules."
    echo "================================================================================"
    exit 1
fi

echo "  [✅] No credential leaks or signature violations detected in staged blocks."
exit 0
