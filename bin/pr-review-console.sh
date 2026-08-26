#!/usr/bin/env bash
# pr-review-console.sh -- tmux bulk-PR-review console.
#
# Per Spencer: the gh Android app works but is awkward on a phone for
# bulk review. This is the desktop/terminal answer: one tmux window,
# two vertical panes -- left lists everything that needs your review
# across the org, right shows full detail (title/state/body/diff) for
# whatever's selected in the left pane.
#
# No fzf dependency -- plain numbered-list + read, works anywhere
# tmux + gh exist. (fzf, if present, would be a nicer left-pane
# picker; not assumed available.)
#
# Usage:
#   pr-review-console.sh [OWNER]   # defaults to Twin-Cities-Open-Systems
#
# Mechanism: left pane writes the selected "REPO NUMBER" to a state
# file; right pane polls that file and re-renders on change. Simple,
# no IPC beyond a shared file, easy to reason about.

set -euo pipefail

# Pane sub-invocations set PR_REVIEW_CONSOLE_PANE and pass OWNER/STATE_FILE
# via environment -- check this BEFORE touching $1, since $1 in that case
# is "left"/"right", not an owner name. Only the top-level (non-pane)
# invocation owns the state dir's lifecycle -- pane sub-invocations just
# use the STATE_FILE they were handed, never create or clean up their own.
if [ "${PR_REVIEW_CONSOLE_PANE:-}" = "left" ] || [ "${PR_REVIEW_CONSOLE_PANE:-}" = "right" ]; then
  : "${OWNER:?}" "${STATE_FILE:?}"
else
  OWNER="${1:-Twin-Cities-Open-Systems}"
  STATE_DIR="$(mktemp -d -t pr-review-console.XXXXXX)"
  STATE_FILE="$STATE_DIR/selected"
  SESSION="pr-review-$$"
  cleanup() { rm -rf "$STATE_DIR"; }
  trap cleanup EXIT
fi

left_pane() {
  while true; do
    clear
    echo "=== Open PRs needing review — $OWNER ==="
    echo "(r=refresh, q=quit, or type a number)"
    echo

    # gh search prs across the org, review-requested for the current user,
    # falls back to "all open PRs" if that search returns nothing (e.g.
    # running as someone with no pending review requests, or off-hours).
    mapfile -t prs < <(gh search prs --owner "$OWNER" --state open --review-requested=@me \
      --json repository,number,title,author -q '.[] | "\(.repository.name)\t\(.number)\t\(.title)\t\(.author.login)"' 2>/dev/null)

    if [ "${#prs[@]}" -eq 0 ]; then
      mapfile -t prs < <(gh search prs --owner "$OWNER" --state open \
        --json repository,number,title,author -q '.[] | "\(.repository.name)\t\(.number)\t\(.title)\t\(.author.login)"' 2>/dev/null)
      echo "(no PRs specifically waiting on your review -- showing all open PRs org-wide)"
      echo
    fi

    for i in "${!prs[@]}"; do
      IFS=$'\t' read -r repo num title author <<< "${prs[$i]}"
      printf "%3d) %-24s #%-5s %-50s [%s]\n" "$((i+1))" "$repo" "$num" "${title:0:50}" "$author"
    done

    echo
    read -r -p "> " choice
    case "$choice" in
      q) tmux kill-session -t "$SESSION" 2>/dev/null; exit 0 ;;
      r|"") continue ;;
      *)
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#prs[@]}" ]; then
          IFS=$'\t' read -r repo num _ _ <<< "${prs[$((choice-1))]}"
          echo "$repo $num" > "$STATE_FILE"
        fi
        ;;
    esac
  done
}

right_pane() {
  # Uses the REST API directly, not `gh pr view`/`gh pr diff` -- both
  # hit a broken GraphQL path (a deprecated Projects-Classic field)
  # that fails on most repos in this org. Confirmed live across
  # fleet-ops, human-execution-engine, .github (all fail identically);
  # the plain REST endpoints below don't touch that field at all.
  # Per OPERATOR_GUIDE.md's gh-first-then-fallback policy: this is the
  # documented fallback, not a permanent workaround to forget about.
  local last=""
  while true; do
    if [ -f "$STATE_FILE" ]; then
      current="$(cat "$STATE_FILE")"
      if [ "$current" != "$last" ]; then
        last="$current"
        read -r repo num <<< "$current"
        clear
        echo "=== $OWNER/$repo #$num ==="
        gh api "repos/$OWNER/$repo/pulls/$num" \
          --jq '"\(.title)\n\(.state) | +\(.additions)/-\(.deletions) | \(.changed_files) file(s)\n\n\(.body // "(no description)")"' \
          2>&1 || echo "(failed to fetch PR details -- $repo #$num)"
        echo
        echo "--- diff (first 150 lines) ---"
        gh api "repos/$OWNER/$repo/pulls/$num" -H "Accept: application/vnd.github.v3.diff" 2>&1 | head -150 \
          || echo "(failed to fetch diff)"
      fi
    fi
    sleep 1
  done
}

if [ "${PR_REVIEW_CONSOLE_PANE:-}" = "left" ]; then
  left_pane
  exit 0
elif [ "${PR_REVIEW_CONSOLE_PANE:-}" = "right" ]; then
  right_pane
  exit 0
fi

# Top-level invocation: set up the tmux session with two vertical panes.
export PR_REVIEW_CONSOLE_STATE_FILE="$STATE_FILE"
tmux new-session -d -s "$SESSION" -x 220 -y 50
tmux send-keys -t "$SESSION" "PR_REVIEW_CONSOLE_PANE=left STATE_FILE='$STATE_FILE' OWNER='$OWNER' bash '$0' left" C-m
tmux split-window -h -l 62% -t "$SESSION"
tmux send-keys -t "$SESSION" "PR_REVIEW_CONSOLE_PANE=right STATE_FILE='$STATE_FILE' OWNER='$OWNER' bash '$0' right" C-m
tmux select-pane -t "$SESSION.0"
tmux attach-session -t "$SESSION"
