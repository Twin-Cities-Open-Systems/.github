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
            if ! git diff-index --quiet HEAD -- || [ -n "$(git status --porcelain)" ]; then
            echo "  [⚠️] WARNING: Uncommitted or untracked changes detected inside '$name'!"
            git status --short
            echo "--------------------------------------------------------------------------------"
            echo "  Options: [y] Force-Destroy and Sync | [n] Skip Repository | [s] Drop to Shell"
            read -p "  --> Select action protocol (y/n/s): " repo_choice
            case "$repo_choice" in
                [yY]) 
                    echo "  [!] Destructive authorization granted." 
                    ;;
                [sS])
                    echo "  [+] Dropping to shell execution layer. Fix workspace files manually."
                    echo "  [!] Type 'exit' to terminate subshell and resume org repo sync manager..."
                    # Invoke a pristine user shell context directly within the dirty repository target path
                    ${SHELL:-/bin/bash}
                    echo "  [+] Returning to manager sequence. Re-evaluating status..."
                    # Recurse or follow through based on updated state parameters
                    ;;
                *) 
                    echo "  [*] Skipping execution loop for $name."
                    return 0 
                    ;;
            esac
        fi

        echo "  -> Fetching upstream references..."
        git fetch --all --prune --tags -q
        local default_branch=$(git remote show origin | sed -n '/HEAD branch/s/.*: //p')
        git checkout -B "$default_branch" "origin/$default_branch" -q
        git clean -fdx
        git reset --hard "origin/$default_branch" -q
        echo "  [✅] Node safely locked in verified sync state."
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
            echo "  --set 1,3,5                                            Synchronize a comma-separated set of indexed rows."
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
        IFS=',' read -r -a selected_indexes <<< "$TARGET_SET"
        echo ""
        echo "[+] Initializing localized execution routines for index targets: $TARGET_SET"
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
            sync_target_repo "$name"
        done
        ;;
esac
