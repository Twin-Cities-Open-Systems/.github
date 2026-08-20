#!/usr/bin/env bash
# Spencer Butler <dev@tcos.us>
# merge-org-prs.sh
# Discovers, processes, and auto-squashes compliance Pull Requests organization-wide.

set -euo pipefail

TARGET_ORG="Twin-Cities-Open-Systems"
WORKSPACE_DIR="${HOME}/git"
TARGET_BRANCH="feature/tcos-compliance-alignment"

echo "================================================================================"
echo "                     TCOS AUTOMATED BULK MERGE UTILITY                         "
echo "================================================================================"

if [ ! -f "${WORKSPACE_DIR}/.github/bin/manage-org-repos.sh" ]; then
    echo "[❌] Critical Error: System repository manager utility not found."
    exit 1
fi

REPOS=$("${WORKSPACE_DIR}/.github/bin/manage-org-repos.sh" --names-only)

# --- Processing Engine Function ---
process_repo_merge() {
    local repo="$1"
    local repo_path="${WORKSPACE_DIR}/${repo}"
    
    if [ -d "$repo_path" ]; then
        cd "$repo_path"
        
        # Check for an open PR matching our specific target feature branch
        local pr_info
        pr_info=$(gh pr list --head "$TARGET_BRANCH" --json number,title --jq '.[0]' 2>/dev/null || true)
        
        if [ -n "$pr_info" ] && [ "$pr_info" != "null" ]; then
            local pr_num
            pr_num=$(echo "$pr_info" | jq -r '.number')
            local pr_title
            pr_title=$(echo "$pr_info" | jq -r '.title')
            
            echo ""
            echo "🚀 Found PR #$pr_num inside [${repo}]: '$pr_title'"
            echo "  -> Executing automated compliance audit override..."
            
            # Execute a squash-merge, delete the remote tracking branch,
            # and use administrative tokens to bypass manual gate bottlenecks
            if gh pr merge "$pr_num" --squash --delete-branch --admin -y; then
                echo "  [✅] PR #$pr_num successfully integrated into mainline trunk."
                
                # Return local working tree back to pristine tracking status
                local default_branch
                default_branch=$(git remote show origin | sed -n '/HEAD branch/s/.*: //p')
                git checkout "$default_branch" -q
                git pull origin "$default_branch" --rebase -q
            else
                echo "  [❌] Failed to execute auto-merge on PR #$pr_num. Check repository permissions."
            fi
        fi
    fi
}

echo "[+] Querying fleet repositories for open alignment tracking PRs..."

# Run the processing loop across all repositories safely
for repo in $REPOS; do
    # Wrap in a subshell to ensure directory state transitions don't pollute parent track
    ( process_repo_merge "$repo" )
done

echo ""
echo "================================================================================"
echo "[✅] Mass merge operations sequence completed."
echo "================================================================================"
