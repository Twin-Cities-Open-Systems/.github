#!/usr/bin/env bash
# Spencer Butler <dev@tcos.us>
# init-org.sh
# Initializes, registers hooks, and bootstraps TCOS workspace repository clusters.

set -euo pipefail

TARGET_ORG="Twin-Cities-Open-Systems"
WORKSPACE_DIR="${HOME}/git"
HOOKS_SOURCE="${WORKSPACE_DIR}/.github/bin/hooks/pre-commit-link-check.sh"

echo "================================================================================"
echo "                    TCOS BOOTSTRAP AND ENVIRONMENT INITIALIZER                   "
echo "================================================================================"

# Verify central controller availability
if [ ! -f "$HOOKS_SOURCE" ]; then
    echo "[❌] Critical Error: Central repository hook source missing at: $HOOKS_SOURCE"
    echo "     Please ensure the '.github' repository is cloned and updated first."
    exit 1
fi

# Fetch list of all repositories using the names-only layout
if [ -f "${WORKSPACE_DIR}/.github/bin/manage-org-repos.sh" ]; then
    REPOS=$("${WORKSPACE_DIR}/.github/bin/manage-org-repos.sh" --names-only)
else
    echo "[❌] Critical Error: System repository manager utility not found."
    exit 1
fi

echo "[+] Activating local git policy guardrails across workspace nodes..."

for repo in $REPOS; do
    repo_path="${WORKSPACE_DIR}/${repo}"
    if [ -d "$repo_path" ]; then
        echo "  -> Configuring hooks for node: $repo"
        mkdir -p "${repo_path}/.git/hooks"
        
        # Symlink the central link guardian script to the local repository's hooks folder
        ln -sf "$HOOKS_SOURCE" "${repo_path}/.git/hooks/pre-commit"
        chmod +x "${repo_path}/.git/hooks/pre-commit"
    fi
done

echo "================================================================================"
echo "[✅] Initialization sweep complete. All workspace nodes are secure."
echo "================================================================================"
