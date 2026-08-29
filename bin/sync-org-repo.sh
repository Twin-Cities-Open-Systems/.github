#!/usr/bin/env bash
# Spencer Butler <dev@tcos.us>
# sync-org-repo.sh
# Real per-repo worker for sync-org-repos.sh, extracted so the
# GNU-parallel fanout and the sequential fallback share one real
# implementation (same pattern already proven in
# human-execution-engine's tooling/bin/hee-repo-refresh and
# .github/bin/audit-repo-branch-state.sh).
#
# Real redesign, 2026-08-29 (Spencer direct: redesign to match
# bootstrap.mk's real health/pull split): the original sync-org-repos.sh
# conflated a dry-run report with a destructive git clean -fdx +
# git reset --hard behind a per-repo interactive y/N prompt --
# fundamentally incompatible with parallel fanout (no sane way to run
# concurrent interactive stdin prompts). Split here into a real
# dry-run default (reports what WOULD happen, never touches anything)
# and an explicit --force flag that actually executes, with no
# per-repo prompts under --force -- same convention as `rm -f`, and
# what actually makes parallelizing this safe. A dirty repo (real
# uncommitted changes to tracked files) is NEVER touched, in either
# mode -- same real invariant already established in bootstrap.mk's
# pull-all-repos.
#
# Also fixes a real, separate bug found reading the original script:
# its clone line read `git clone "https://github.com{TARGET_ORG}/..."`
# -- missing both the `/` before the org name and the `$` to actually
# expand the variable, so `{TARGET_ORG}` was literal text, not a real
# substitution. The clone path had never worked.
#
# Usage: sync-org-repo.sh <repo-name> <repo-path> [--force]
# Prints one real status line to stdout.

set -euo pipefail

TARGET_ORG="Twin-Cities-Open-Systems"

repo="$1"
repo_path="$2"
force="${3:-}"

if [ ! -d "$repo_path" ]; then
    if [ "$force" = "--force" ]; then
        if git clone --quiet "https://github.com/${TARGET_ORG}/${repo}.git" "$repo_path" 2>/dev/null; then
            echo "🟢 $repo: cloned"
        else
            echo "🔴 $repo: clone failed"
        fi
    else
        echo "🟡 $repo: MISSING -- would clone (dry-run, use --force to actually clone)"
    fi
    exit 0
fi

cd "$repo_path"

tracked_dirty=$(git status --porcelain 2>/dev/null | grep -v '^??' | grep -c . || true)
if [ "$tracked_dirty" != "0" ]; then
    echo "🟠 $repo: dirty ($tracked_dirty uncommitted) -- never touched, resolve by hand first"
    exit 0
fi

git fetch --quiet 2>/dev/null || true
default_branch=$(git remote show origin | sed -n '/HEAD branch/s/.*: //p')

if [ -z "$default_branch" ]; then
    echo "🔴 $repo: could not determine default branch -- skipped"
    exit 0
fi

current_head=$(git rev-parse HEAD 2>/dev/null || echo "")
origin_head=$(git rev-parse "origin/$default_branch" 2>/dev/null || echo "")

if [ -n "$current_head" ] && [ "$current_head" = "$origin_head" ]; then
    echo "🟢 $repo: in sync with origin/$default_branch"
    exit 0
fi

if [ "$force" = "--force" ]; then
    git checkout -B "$default_branch" "origin/$default_branch" -q
    git clean -fdx -q
    git reset --hard "origin/$default_branch" -q
    echo "🟢 $repo: reset to origin/$default_branch"
else
    echo "🟡 $repo: would reset to origin/$default_branch (dry-run, use --force to actually reset)"
fi
