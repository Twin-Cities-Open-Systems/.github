# `pr-review-console.sh` — real run

Captured 2026-08-21 against the live org (22 real open PRs at the
time). No interactive TTY exists in this sandbox, so the run was
driven the same way the tool itself was debugged: a detached tmux
session, a simulated state-file write standing in for a keypress, and
`tmux capture-pane -p` to read the result. That's a limitation of this
environment, not the tool — a human at a real terminal just runs
`bin/pr-review-console.sh` and types.

```
$ bin/pr-review-console.sh
```

## Left pane — org-wide open-PR list

No PRs were pending specifically on `@me`'s review at capture time, so
the tool fell back to "all open PRs org-wide" (documented fallback
behavior, not a bug):

```
  1) .github                  #26    docs: CORPUS.md                              [touchy-claude]
  2) tcos-www                 #31    docs: OPERATORS.md + real example for generate-pub [touchy-claude]
  3) fleet-ops                #207   docs: OPERATORS.md + real example for diagnose-con [touchy-claude]
  4) human-execution-engine   #252   docs: OPERATORS.md + real example for scan-hee-car [touchy-claude]
  5) .github                  #25    feat(bin): survey-github-org.py -- external org su [touchy-claude]
  6) .github                  #24    docs: OPERATORS.md -- repo-specific operator doc   [touchy-claude]
  7) human-execution-engine   #251   docs(guides): OPERATOR_GUIDE.md -- central human-o [touchy-claude]
  8) .github                  #23    feat(bin): create-epic.py -- one command instead o [touchy-claude]
  9) tcos-www                 #29    fix(docs): restore real README (bulk-template wipe [touchy-claude]
 10) resume                   #12    fix(docs): restore real README (bulk-template wipe [touchy-claude]
 11) market-thesis-news       #7     fix(docs): restore real README (bulk-template wipe [touchy-claude]
 12) tcos-audit               #4     fix(docs): restore real README (bulk-template wipe [touchy-claude]
 13) tick-task                #22    fix(docs): restore real README (bulk-template wipe [touchy-claude]
 14) thesis-engine            #13    fix(docs): restore real README (bulk-template wipe [touchy-claude]
 15) tcos-plan-private        #33    fix(docs): restore real README (bulk-template wipe [touchy-claude]
 16) human-execution-engine   #249   fix(deps): bump markdownlint-cli2, resolve 5 Depen [touchy-claude]
 17) human-execution-engine   #245   feature/MIB 66550                                  [spencerbutler]
 18) glass-ops                #6     glass-browser: disable Chrome's crash-restore info  [touchy-claude]
 19) hee-epoch                #2     Add CODEOWNERS -- require_code_owner_reviews was a  [touchy-claude]
 20) tcos-audit               #1     Add real incident: third-party private conversatio  [touchy-claude]
 21) glass-ops                #2     Propose touchy -> Sway migration plan               [touchy-claude]
 22) glass-ops                #1     Add glass-access: permission-checked display/works  [touchy-claude]
```

## Right pane — selecting `#6` (`.github` PR #24, this doc's own PR)

```
=== Twin-Cities-Open-Systems/.github #24 ===
docs: OPERATORS.md -- repo-specific operator doc
open | +58/-0 | 1 file(s)

...

--- diff (first 150 lines) ---
diff --git a/OPERATORS.md b/OPERATORS.md
new file mode 100644
index 0000000..xxxxxxx
--- /dev/null
+++ b/OPERATORS.md
@@ -0,0 +1,58 @@
...
+## Org-wide repo scripts
+
+- **`bin/manage-org-repos.sh`** -- sync/report across every org repo.
+  `--set 1-4,6` to sync specific indexes (by the numbered list it
+  prints with no args). **Known bugs, not yet fixed** (fleet-ops#196):
...
```

Real title, state, additions/deletions/file-count, body, and diff --
sourced from the REST API (`gh api repos/OWNER/REPO/pulls/NUM`), not
`gh pr view`/`gh pr diff`. See `OPERATORS.md`'s entry for why: both of
those `gh` subcommands hit a broken GraphQL path (a deprecated
Projects-Classic field) that fails on most repos in this org.
