#!/usr/bin/env bash
# Spencer Butler <dev@tcos.us>
# audit-repo-branch-state.sh
# Real per-repo worker for audit-branch-states.sh, extracted so the
# GNU-parallel fanout and the sequential fallback share one real
# implementation instead of two that can drift (same pattern already
# proven in human-execution-engine's tooling/bin/hee-repo-refresh).
#
# Real fix alongside the extraction: the original inline loop judged
# "Diverged"/"Outdated"/"Unpushed" off whatever @{u} happened to already
# have cached locally, with no git fetch first -- a real correctness
# gap (could report a repo as up to date when origin has since moved).
# Fetches first now, matching hee-repo-refresh's own discipline.
#
# Usage: audit-repo-branch-state.sh <repo-name> <repo-path>
# Prints one real formatted table row to stdout.

set -euo pipefail

repo="$1"
repo_path="$2"

if [ ! -d "$repo_path" ]; then
    printf "%-30s | %-25s | %-15s\n" "$repo" "[MISSING CLONE]" "⚠️ ACTION REQ"
    exit 0
fi

(
    cd "$repo_path"

    git fetch --quiet 2>/dev/null || true

    active_branch=$(git branch --show-current 2>/dev/null || echo "[DETACHED HEAD]")
    [ -z "$active_branch" ] && active_branch="[DETACHED HEAD]"

    local_status="Clean"
    if ! git diff-index --quiet HEAD -- 2>/dev/null || [ -n "$(git status --porcelain)" ]; then
        local_status="DIRTY 📦"
    fi

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
