# bin/cron_sweep_repo.bash
 
# Append this function pattern or run condition into your bin/manage-org-repos.sh
# when invoked with a newly declared '--cron-sweep' switch:

cron_sweep_repo() {
    local name="$1"
    local repo_path="${WORKSPACE_DIR}/${name}"
    
    if [ ! -d "$repo_path" ]; then
        # Missing folders are safely cloned automatically
        git clone "https://github.com{TARGET_ORG}/${name}.git" "$repo_path" &>/dev/null
        return 0
    fi

    (
        cd "$repo_path"
        # CRON GUARD: If changes are present, do NOT freeze or prompt. Log error and skip.
        if ! git diff-index --quiet HEAD -- || [ -n "$(git status --porcelain)" ]; then
            echo "[⚠️ CRON ALERT] Node '${name}' has uncommitted drift. Skipping to preserve workspace data." >> "${WORKSPACE_DIR}/.tcos-cron-drift.log"
            exit 0
        fi

        # Safely fast-forward if pristine
        git fetch --all --prune --tags -q
        local default_branch=$(git remote show origin | sed -n '/HEAD branch/s/.*: //p')
        git checkout -B "$default_branch" "origin/$default_branch" -q
        git reset --hard "origin/$default_branch" -q
    )
}

