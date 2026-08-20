#!/usr/bin/env bash
# Spencer Butler <dev@tcos.us>
# audit-branch-states.sh
# Audits local branch states, tracking status, and uncommitted drift across all TCOS nodes.

set -euo pipefail

TARGET_ORG="Twin-Cities-Open-Systems"
WORKSPACE_DIR="${HOME}/git"

echo "================================================================================"
echo "                    TCOS FLEET BRANCH STATE AUDIT REPORT                       "
echo "================================================================================"
printf "%-30s | %-25s | %-15s\n" "REPOSITORY" "ACTIVE BRANCH" "LOCAL STATUS"
echo "--------------------------------------------------------------------------------"

if [ ! -f "${WORKSPACE_DIR}/.github/bin/manage-org-repos.sh" ]; then
    echo "[❌] Critical Error: manage-org-repos.sh utility not found."
    exit 1
fi

REPOS=$("${WORKSPACE_DIR}/.github/bin/manage-org-repos.sh" --names-only)

for repo in $REPOS; do
    repo_path="${WORKSPACE_DIR}/${repo}"
    if [ ! -d "$repo_path" ]; then
        printf "%-30s | %-25s | %-15s\n" "$repo" "[MISSING CLONE]" "⚠️ ACTION REQ"
        continue
    fi

    (
        cd "$repo_path"
        
        # Extract active branch name safely
        active_branch=$(git branch --show-current 2>/dev/null || echo "[DETACHED HEAD]")
        [ -z "$active_branch" ] && active_branch="[DETACHED HEAD]"
        
        # Check for uncommitted modifications or untracked file paths
        local_status="Clean"
        if ! git diff-index --quiet HEAD -- || [ -n "$(git status --porcelain)" ]; then
            local_status="DIRTY 📦"
        fi
        
        # Check tracking status against remote tracking branch if upstream is configured
        if git rev-parse --verify @{u} &>/dev/null; then
            local_commits=$(git rev-list --count @{u}..HEAD)
            remote_commits=$(git rev-list --count HEAD..@{u})
            
            if [ "$local_commits" -gt 0 ] && [ "$remote_commits" -gt 0 ]; then
                local_status="$local_status (Diverged 🔄)"
            elif [ "$local_commits" -gt 0 ]; then
                local_status="$local_status (Unpushed ⬆️)"
            elif [ "$remote_commits" -gt 0 ]; then
                local_status="$local_status (Outdated ⬇️)"
            fi
        fi

        printf "%-30s | %-25s | %-15s\n" "$repo" "$active_branch" "$local_status"
    )
done
echo "================================================================================"
