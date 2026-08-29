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

# Real trigger (2026-08-29): same-day survey of shell for-loops as
# GNU-parallel candidates. Per-repo logic extracted to
# audit-repo-branch-state.sh (now also does a real `git fetch` first --
# a real correctness gap the old inline version had, judging
# Diverged/Outdated off whatever @{u} happened to already be cached
# locally). Fans out via GNU parallel, --keep-order so the table still
# reads in the same real repo-list order; falls back to the original
# sequential loop when parallel isn't installed.
if command -v parallel >/dev/null 2>&1; then
    parallel --keep-order "${WORKSPACE_DIR}/.github/bin/audit-repo-branch-state.sh" {} "${WORKSPACE_DIR}/{}" ::: $REPOS
else
    for repo in $REPOS; do
        "${WORKSPACE_DIR}/.github/bin/audit-repo-branch-state.sh" "$repo" "${WORKSPACE_DIR}/${repo}"
    done
fi
echo "================================================================================"
