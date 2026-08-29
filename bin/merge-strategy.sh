#!/usr/bin/env bash
# Manage and enforce TCOS org repo merge strategy
# Spencer Butler <dev@tcos.us>

# TODO(@touchy-claude)
# - Manage
# - auth check and ACLs for use

# Enforce
#
# Real trigger (2026-08-29): same-day survey of shell for-loops as
# GNU-parallel candidates flagged this as a real, independent
# gh-repo-edit-per-repo candidate. Capped at -j4 (not unbounded fanout)
# deliberately -- this mutates via GitHub's REST API, and a burst of
# concurrent repo-settings edits risks tripping GitHub's own secondary
# rate limiting, unlike the pure-local git operations bootstrap.mk
# parallelizes. Falls back to the original sequential loop when GNU
# parallel isn't installed.
REPOS="$(gh repo list Twin-Cities-Open-Systems --limit 200 --json name --jq '.[].name')"
if command -v parallel >/dev/null 2>&1; then
  echo "$REPOS" | parallel -j4 'echo "Updating settings for: {}..."; gh repo edit "Twin-Cities-Open-Systems/{}" --enable-squash-merge=true --enable-merge-commit=false --enable-rebase-merge=false'
else
  for repo in $REPOS; do
    echo "Updating settings for: $repo..."
    gh repo edit "Twin-Cities-Open-Systems/$repo" \
      --enable-squash-merge=true \
      --enable-merge-commit=false \
      --enable-rebase-merge=false
  done
fi

# Manage
# Note(@spencerbutler): Code will allow modifications to the default rules.
