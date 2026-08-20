#!/usr/bin/env bash
# Spencer Butler <dev@tcos.us>
# init-org.sh
# Initializes, registers hooks, and bootstraps TCOS workspace repository clusters.

set -euo pipefail

TARGET_ORG="Twin-Cities-Open-Systems"
WORKSPACE_DIR="${HOME}/git"
HOOKS_SOURCE_DIR="${WORKSPACE_DIR}/.github/bin/hooks"

echo "================================================================================"
echo "                    TCOS BOOTSTRAP AND ENVIRONMENT INITIALIZER                   "
echo "================================================================================"

# Verify central repository manager utility exists
if [ ! -f "${WORKSPACE_DIR}/.github/bin/manage-org-repos.sh" ]; then
    echo "[❌] Critical Error: System repository manager utility not found."
    exit 1
fi

# Fetch list of all repositories using the names-only driver
REPOS=$("${WORKSPACE_DIR}/.github/bin/manage-org-repos.sh" --names-only)

echo "[+] Activating multi-gate pre-commit policy guardrails across workspace nodes..."

for repo in $REPOS; do
    repo_path="${WORKSPACE_DIR}/${repo}"
    if [ -d "$repo_path" ]; then
        echo "  -> Configuring multi-gate hooks for node: $repo"
        
        # Ensure the repository local git hooks folder path exists cleanly
        mkdir -p "${repo_path}/.git/hooks"
        
        # Write the multi-driver wrapper script into the individual repo git configurations folder
        cat << 'INNER_EOF' > "${repo_path}/.git/hooks/pre-commit"
#!/usr/bin/env bash
# Automated Multi-Gate Pre-Commit Driver for TCOS

set -e
"${HOME}/git/.github/bin/hooks/pre-commit-link-check.sh"
"${HOME}/git/.github/bin/hooks/pre-commit-secret-check.sh"
INNER_EOF

        # Make the wrapper executable
        chmod +x "${repo_path}/.git/hooks/pre-commit"
    fi
done

echo "================================================================================"
echo "[✅] Initialization sweep complete. All workspace nodes are secured and linked."
echo "================================================================================"
