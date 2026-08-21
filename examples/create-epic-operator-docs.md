# Example: create-epic.py

Real run, 2026-08-21 — creating the actual operator-documentation
epic during the same work that built this tool. Command and output
copied verbatim from that session, not reconstructed.

## Command

```bash
python3 bin/create-epic.py \
  --repo Twin-Cities-Open-Systems/human-execution-engine \
  --title "Epic: Operator documentation (central + per-repo)" \
  --body-file epic-body.md \
  --label documentation \
  --sub-issue Twin-Cities-Open-Systems/glass-ops#7 \
  --project Twin-Cities-Open-Systems/1
```

## Output

```
=== 1. Creating issue in Twin-Cities-Open-Systems/human-execution-engine ===
  https://github.com/Twin-Cities-Open-Systems/human-execution-engine/issues/250
=== 2. Linking 1 sub-issue(s) ===
  Twin-Cities-Open-Systems/glass-ops#7: linked
=== 3. Adding to project Twin-Cities-Open-Systems/1 ===
  added

Done: https://github.com/Twin-Cities-Open-Systems/human-execution-engine/issues/250
```

## Verification (not just trusting the tool's own success message)

```bash
$ gh api graphql -f query='query { repository(owner:"Twin-Cities-Open-Systems", name:"human-execution-engine") { issue(number:250) { subIssuesSummary { total } } } }' -q '.data.repository.issue.subIssuesSummary.total'
1
```

Result: [human-execution-engine#250](https://github.com/Twin-Cities-Open-Systems/human-execution-engine/issues/250) — real issue, real linked sub-issue, on the real Roadmap project.
