# Example: manage-project.py

Real run, 2026-08-20 — dumping the actual live TCOS Roadmap project,
then applying that same dump back to prove idempotency. Verbatim from
that session.

## dump

```bash
$ python3 bin/manage-project.py dump Twin-Cities-Open-Systems 1
```

```yaml
project:
  owner: Twin-Cities-Open-Systems
  number: 1
  title: TCOS Roadmap
views:
- name: View 1
  layout: TABLE_LAYOUT
- name: Kanban
  layout: BOARD_LAYOUT
- name: Roadmap
  layout: ROADMAP_LAYOUT
items:
- https://github.com/Twin-Cities-Open-Systems/.github/pull/18
- https://github.com/Twin-Cities-Open-Systems/.github/pull/19
- https://github.com/Twin-Cities-Open-Systems/fleet-ops/issues/196
- https://github.com/Twin-Cities-Open-Systems/fleet-ops/issues/199
- https://github.com/Twin-Cities-Open-Systems/fleet-ops/issues/200
- https://github.com/Twin-Cities-Open-Systems/fleet-ops/issues/201
- https://github.com/Twin-Cities-Open-Systems/fleet-ops/issues/202
# (truncated -- real dump had 22 items at the time; full example
# trimmed here for length, see the tool's own output for the current
# live list)
```

## apply (idempotency check — re-running the exact dump just taken)

```bash
$ python3 bin/manage-project.py apply roadmap.yaml
```

```
=== TCOS Roadmap (owner=Twin-Cities-Open-Systems #1) ===
  view 'View 1': already exists, skipping
  view 'Kanban': already exists, skipping
  view 'Roadmap': already exists, skipping
  item https://github.com/Twin-Cities-Open-Systems/.github/pull/18: already present, skipping
  item https://github.com/Twin-Cities-Open-Systems/.github/pull/19: already present, skipping
  ... (every item: already present, skipping)
```

Zero duplicate creates — confirms the tool is safe to re-run.
