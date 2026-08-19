#!/usr/bin/env bash
# Manage and enforce TCOS org repo merge strategy
# Spencer Butler <dev@tcos.us>

# TODO(@touchy-claude)
# - Manage
# - auth check and ACLs for use

# Enforce
for repo in $(gh repo list Twin-Cities-Open-Systems --limit 200 --json name --jq '.[].name'); do
  echo "Updating settings for: $repo..."
  gh repo edit "Twin-Cities-Open-Systems/$repo" \
    --enable-squash-merge=true \
    --enable-merge-commit=false \
    --enable-rebase-merge=false
done

# Manage
# Note(@spencerbutler): Code will allow modifications to the default rules.
