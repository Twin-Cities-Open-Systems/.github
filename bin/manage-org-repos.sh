#!/usr/bin/env bash
# Spencer Butler <dev@tcos.us>
# manage-org-repos.sh
# Discovers, indexes, filters, and synchronizes TCOS repositories with strict protection gates.

set -euo pipefail

TARGET_ORG="Twin-Cities-Open-Systems"
WORKSPACE_DIR="${HOME}/git"

# Verify tool availability
for cmd in gh git jq; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "[❌] Critical Error: System utility '$cmd' is not installed in current PATH."
        exit 1
    fi
done

# Fetch fresh repo information
REPOS_JSON=$(gh repo list "$TARGET_ORG" --limit 100 --json name,visibility)
readarray -t REPO_NAMES < <(echo "$REPOS_JSON" | jq -r '.[].name' | sort)

# Helper function to print a clean indexed report
print_summary_report() {
    echo "================================================================================"
    echo "                    TCOS REPOSITORY MASTER INDEX SUMMARY                        "
    echo "================================================================================"
    printf "%-5s | %-35s | %-20s\n" "INDEX" "REPOSITORY NAME" "LOCAL SYSTEM STATUS"
    echo "--------------------------------------------------------------------------------"
    local idx=0
    for name in "${REPO_NAMES[@]}"; do
        idx=$((idx + 1))
        local repo_path="${WORKSPACE_DIR}/${name}"
        local status="[Missing From Local]"
        if [ -d "$repo_path" ]; then
            status="[Local Path Present]"
        fi
        printf "%-5d | %-35s | %-20s\n" "$idx" "$name" "$status"
    done
    echo "================================================================================"
}

# Helper function to run the sync workflow safely
sync_target_repo() {
    local name="$1"
    local repo_path="${WORKSPACE_DIR}/${name}"
    echo ""
    echo "⚙️ Processing Target Node: ${TARGET_ORG}/${name}"
    
    if [ ! -d "$repo_path" ]; then
        echo "  [+] Direct directory missing. Initializing secure clone..."
        git clone "https://github.com{TARGET_ORG}/${name}.git" "$repo_path"
        return 0
    fi

    (
        cd "$repo_path"
        
        # --- AUTOMATED COMPLIANCE & DRIFT PROTECTION ---
        local HAS_DRIFT=0
        if ! git diff-index --quiet HEAD -- || [ -n "$(git status --porcelain)" ]; then
            echo "  [📦] Uncommitted changes detected inside '$name'. Stashing local work tree..."
            git stash push -m "tcos-auto-cleanup-checkpoint-$(date +%s)" -q
            HAS_DRIFT=1
        fi

        echo "  -> Fetching upstream references..."
        git fetch --all --prune --tags -q
        local default_branch=$(git remote show origin | sed -n '/HEAD branch/s/.*: //p')
        
        # --- SAFE UPDATE WORKFLOW ---
        if [ "$HAS_DRIFT" -eq 1 ]; then
            echo "  -> Fast-forwarding local tracking structures with upstream..."
            git checkout "$default_branch" -q
            git pull origin "$default_branch" --rebase -q
            
            echo "  [💥] Re-applying your local modifications on top of current updates..."
            if git stash pop -q; then
                echo "  [✅] Workspace updated safely. Local modifications preserved."
            else
                echo "  [❌] Merge Conflict Detected! Keeping your work safe in stash registry."
                echo "       Action Required: Resolve manually inside: $repo_path"
            fi
        else
            # If the node is completely clean, it is safe to fast-forward the branch pointer directly
            git checkout -B "$default_branch" "origin/$default_branch" -q
            echo "  [✅] Node safely synchronized to fresh baseline state."
        fi
    )
}

# --- Action Modes Evaluation ---
MODE="SUMMARY"
TARGET_SET=""

if [ $# -gt 0 ]; then
    case "$1" in
        --names-only)
            MODE="NAMES_ONLY"
            ;;
        --set)
            if [ -z "${2:-}" ]; then
                echo "[❌] Error: --set flag requires a comma-separated list of indexes."
                exit 1
            fi
            MODE="SET"
            TARGET_SET="$2"
            ;;
        --dangerously-force-destructive-sync-all-repositories)
            MODE="SYNC_ALL"
            ;;
        *)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  (No arguments)                                         Display indexed visual report summary."
            echo "  --names-only                                           List raw repository names (one per line)."
            echo "  --set 1-4,6,10-12                                      Synchronize a comma-separated set of indexes or ranges."
            echo "  --dangerously-force-destructive-sync-all-repositories  Force global destructive overwrite on all repos."
            exit 1
            ;;
    esac
fi

# --- Execution Router ---
case "$MODE" in
    NAMES_ONLY)
        for name in "${REPO_NAMES[@]}"; do
            echo "$name"
        done
        ;;
    SUMMARY)
        print_summary_report
        echo "Tip: Run with '--set <indexes>' or '--names-only' to drive automation matrices."
        ;;
    SET)
        print_summary_report
        declare -a selected_indexes
        IFS=',' read -r -a raw_tokens <<< "$TARGET_SET"
        
        for token in "${raw_tokens[@]}"; do
            if [[ "$token" =~ ^([0-9]+)-([0-9]+)$ ]]; then
                start_range="${BASH_REMATCH[1]}"
                end_range="${BASH_REMATCH[2]}"
                for ((i=start_range; i<=end_range; i++)); do
                    selected_indexes+=("$i")
                done
            elif [[ "$token" =~ ^([0-9]+)$ ]]; then
                selected_indexes+=("$token")
            else
                echo "[❌] Error: Invalid set notation token discovered: '$token'"
                exit 1
            fi
        done

        echo ""
        echo "[+] Initializing localized execution routines for expanded range targets..."
        for idx in "${selected_indexes[@]}"; do
            if [ "$idx" -le 0 ] || [ "$idx" -gt "${#REPO_NAMES[@]}" ]; then
                echo "[❌] Error: Index value '$idx' falls outside current boundaries."
                exit 1
            fi
            target_name="${REPO_NAMES[$((idx - 1))]}"
            sync_target_repo "$target_name"
        done
        ;;
    SYNC_ALL)
        echo "================================================================================"
        echo "❗ CRITICAL WARNING: DESTRUCTIVE OVERWRITE AUTHORIZATION ENCOUNTERED ❗"
        echo "================================================================================"
        echo "This action will systematically force-reset every workspace repository under"
        echo "path: $WORKSPACE_DIR."
        echo "All uncommitted changes across ALL active folders will be permanently deleted."
        echo "--------------------------------------------------------------------------------"
        read -p "Type 'CONFIRM' to trigger this global routine: " destructive_confirm
        if [ "$destructive_confirm" != "CONFIRM" ]; then
            echo "[-] Routine aborted by user protection block."
            exit 0
        fi
        for name in "${REPO_NAMES[@]}"; do
            repo_path="${WORKSPACE_DIR}/${name}"
            if [ -d "$repo_path" ]; then
                (
                    cd "$repo_path"
                    git fetch --all --prune --tags -q
                    local default_branch=$(git remote show origin | sed -n '/HEAD branch/s/.*: //p')
                    git checkout -B "$default_branch" "origin/$default_branch" -q
                    git clean -fdx
                    git reset --hard "origin/$default_branch" -q
                    echo "  [💥 DESTRUCTIVE CLEAN COMPLETE] Node $name completely wiped and synchronized."
                )
            fi
        done
        ;;
esac

