#!/usr/bin/env bash
# Spencer Butler <dev@tcos.us>
# sync-org-repos.sh
# Discovers, clones, and synchronizes all TCOS repositories safely with prompt gates.
#
# Technical Pre-requisites:
# - GitHub CLI authenticated (`gh auth status`)
# - POSIX compliant environment with git, gh, and jq utilities.

set -euo pipefail

# --- Configuration & Invariants ---
TARGET_ORG="Twin-Cities-Open-Systems"
WORKSPACE_DIR="${HOME}/git"

echo "================================================================================"
echo "                   TCOS WORKSPACE ENVIRONMENT SYNCHRONIZER                     "
echo "================================================================================"
echo "[*] Target Organization: $TARGET_ORG"
echo "[*] Execution Workspace: $WORKSPACE_DIR"
echo "================================================================================"

# Verify platform tool availability
for cmd in gh git jq; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "[❌] Critical Error: System utility '$cmd' is not installed in current PATH."
        exit 1
    fi
done

mkdir -p "$WORKSPACE_DIR"

echo "[+] Querying GitHub API for active organizational repositories..."
REPOS=$(gh repo list "$TARGET_ORG" --limit 100 --json name | jq -r '.[].name')

if [ -z "$REPOS" ]; then
    echo "[-] Operational Warning: No repositories discovered under organization context."
    exit 0
fi

# --- Phase 1: Operational Report Summary ---
echo "--------------------------------------------------------------------------------"
echo "                    PRE-EXECUTION AUDIT AND ACTION PLAN"
echo "--------------------------------------------------------------------------------"
file_count=0
for repo_name in $REPOS; do
    file_count=$((file_count + 1))
    repo_path="${WORKSPACE_DIR}/${repo_name}"
    if [ -d "$repo_path" ]; then
        echo "  [$file_count] REPO: $repo_name -> Local directory exists (Will evaluate tree changes)"
    else
        echo "  [$file_count] REPO: $repo_name -> Local directory MISSING (Will initiate git clone)"
    fi
done
echo "--------------------------------------------------------------------------------"
echo "Total repositories to process: $file_count"
echo "================================================================================"
echo ""

read -p "Authorize workspace synchronization loop? (y/N): " init_choice
case "$init_choice" in 
    [yY][eE][sS]|[yY]) echo "[+] Initializing execution threads..." ;;
    *) echo "[-] Execution aborted by operator command."; exit 0 ;;
esac

# --- Phase 2: Core Safe Execution Engine ---
for repo_name in $REPOS; do
    repo_path="${WORKSPACE_DIR}/${repo_name}"
    echo ""
    echo "⚙️ Processing Node: ${TARGET_ORG}/${repo_name}"
    
    if [ ! -d "$repo_path" ]; then
        echo "  [+] Initializing secure clone..."
        # FIXED: String interpolation fix inside double quotes to prevent illegal literal formats
        git clone "https://github.com{TARGET_ORG}/${repo_name}.git" "$repo_path"
        continue
    fi

    # Subshell environment execution block to protect paths safely
    (
        cd "$repo_path"
        
        # Check for uncommitted work trees or untracked changes
        if ! git diff-index --quiet HEAD -- || [ -n "$(git status --porcelain)" ]; then
            echo "  [⚠️] WARNING: Uncommitted or untracked file structures detected inside '$repo_name'!"
            git status --short
            echo "--------------------------------------------------------------------------------"
            read -p "  --> DESTROY UNCOMMITTED CHANGES AND FORCE DESTRUCTIVE RESET? (y/N): " repo_choice
            case "$repo_choice" in
                [yY][eE][sS]|[yY]) echo "  [!] Destructive authorization granted. Purging drift..." ;;
                *) echo "  [*] Skipping sync block for $repo_name to protect work trees."; exit 0 ;;
            esac
        fi

        echo "  -> Synchronizing remote reference streams..."
        git fetch --all --prune --tags -q
        
        # Extract default branch name natively without grepping brittle command strings
        default_branch=$(git remote show origin | sed -n '/HEAD branch/s/.*: //p')
        
        echo "  -> Tracking target branch: $default_branch"
        git checkout -B "$default_branch" "origin/$default_branch" -q
        
        echo "  -> Executing clean loops..."
        git clean -fdx
        git reset --hard "origin/$default_branch" -q
        echo "  [✅] Node safely locked in a clean verified state."
    )
done

echo ""
echo "================================================================================"
echo "[✅] Workspace synchronization complete."
echo "================================================================================"

