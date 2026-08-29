#!/usr/bin/env bash
# Spencer Butler <dev@tcos.us>
# sync-org-repos.sh
# Discovers every real TCOS org repo, reports what's missing/dirty/out
# of sync, and (only with --force) actually clones missing repos and
# hard-resets clean-but-diverged ones to match origin exactly.
#
# Technical Pre-requisites:
# - GitHub CLI authenticated (`gh auth status`)
# - POSIX compliant environment with git, gh, and jq utilities.
#
# Real redesign, 2026-08-29 (Spencer direct: redesign to match
# bootstrap.mk's real health/pull split, same day as the GNU-parallel
# survey that found this script). The original conflated a dry-run
# report with a destructive git clean -fdx + git reset --hard behind a
# per-repo interactive y/N prompt -- fundamentally incompatible with
# parallel fanout (no sane way to run concurrent interactive stdin
# prompts). Default mode here is a real dry-run report, never touches
# anything; --force actually executes, with no per-repo prompts (same
# convention as `rm -f`) -- that's what makes parallelizing this safe.
# A dirty repo (real uncommitted changes to tracked files) is NEVER
# touched, in either mode -- same invariant already established in
# bootstrap.mk's pull-all-repos. Real per-repo logic lives in
# sync-org-repo.sh, shared by the parallel path and the sequential
# fallback (same pattern already proven in human-execution-engine's
# hee-repo-refresh and this repo's own audit-repo-branch-state.sh).
#
# Also fixes a real, separate bug found reading the original: its
# clone line was `git clone "https://github.com{TARGET_ORG}/..."` --
# missing both the `/` before the org name and the `$` to actually
# expand the variable, so `{TARGET_ORG}` was literal text, not a real
# substitution. That path had never worked.
#
# Usage: sync-org-repos.sh [--force]
#   (no args)  dry-run report -- what would happen, touches nothing
#   --force    actually clones missing repos and resets diverged ones

set -euo pipefail

TARGET_ORG="Twin-Cities-Open-Systems"
WORKSPACE_DIR="${HOME}/git"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORCE="${1:-}"

if [ -n "$FORCE" ] && [ "$FORCE" != "--force" ]; then
    echo "Usage: sync-org-repos.sh [--force]" 1>&2
    exit 2
fi

echo "================================================================================"
echo "                   TCOS WORKSPACE ENVIRONMENT SYNCHRONIZER                     "
echo "================================================================================"
echo "[*] Target Organization: $TARGET_ORG"
echo "[*] Execution Workspace: $WORKSPACE_DIR"
echo "[*] Mode: $([ "$FORCE" = "--force" ] && echo "FORCE (will clone/reset for real)" || echo "dry-run (reports only, touches nothing)")"
echo "================================================================================"

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

echo ""
if command -v parallel >/dev/null 2>&1; then
    echo "$REPOS" | parallel --keep-order "$SCRIPT_DIR/sync-org-repo.sh" {} "${WORKSPACE_DIR}/{}" "$FORCE"
else
    for repo in $REPOS; do
        "$SCRIPT_DIR/sync-org-repo.sh" "$repo" "${WORKSPACE_DIR}/${repo}" "$FORCE"
    done
fi

echo ""
echo "================================================================================"
echo "[✅] Workspace synchronization $([ "$FORCE" = "--force" ] && echo "complete" || echo "dry-run complete -- re-run with --force to actually apply")."
echo "================================================================================"
