# `manage-project.py` field support + `sync-roadmap-status.py` — real run

Real trigger, 2026-08-21: Spencer wants Date/Effort tracked on Project
items so "shit just auto updates the right shit" instead of a human
hand-flipping the Status dropdown. Dogfoods `roadmap`'s "in future"
bucket concept using today's real date as the epoch-0 stand-in, since
HEE's own `heeEpoch` isn't ratified anywhere real yet.

## 1. Creating the fields (declarative, idempotent)

```
$ cat roadmap-fields.yaml
project:
  owner: Twin-Cities-Open-Systems
  number: 1
fields:
  - name: Date
    dataType: DATE
  - name: Effort
    dataType: NUMBER

$ python3 bin/manage-project.py apply roadmap-fields.yaml
=== TCOS Roadmap (owner=Twin-Cities-Open-Systems #1) ===
  field 'Date' (DATE): created
  field 'Effort' (NUMBER): created

$ python3 bin/manage-project.py apply roadmap-fields.yaml   # re-run, idempotent
=== TCOS Roadmap (owner=Twin-Cities-Open-Systems #1) ===
  field 'Date': already exists, skipping
  field 'Effort': already exists, skipping
```

## 2. Dry-run report against the real, live project

```
$ python3 bin/sync-roadmap-status.py Twin-Cities-Open-Systems 1
=== sync-roadmap-status: Twin-Cities-Open-Systems#1, threshold=59d, today=2026-08-21 ===

0 item(s) need a Status change:

43 item(s) in the Todo/Near/In-Future family have no Date set (left alone, not guessed):
  https://github.com/Twin-Cities-Open-Systems/fleet-ops/issues/69  status=Todo  [Track: LLM agent output degradation over long sing]
  ... (42 more, real items, real titles)

21 item(s) not in scope (In Progress/Done/other) -- untouched
```

Correctly does nothing when no Date values exist yet -- reports what's
missing instead of guessing.

## 3. Real write-path proof (disposable test, cleaned up after)

Set a test date 10 days out on a real, low-stakes item
(`primitives#3`), ran with `--apply`, confirmed the flip, then used
`clearProjectV2ItemFieldValue` to remove the test date and reverted
Status back to `Todo` -- no fabricated data left on any real ticket.

```
$ python3 bin/sync-roadmap-status.py Twin-Cities-Open-Systems 1 --apply
1 item(s) need a Status change:
  https://github.com/Twin-Cities-Open-Systems/primitives/issues/3  Todo -> Near Future Todo  [Set up CODEOWNERS + branch protection for primitiv]
    applied

# ... cleanup: cleared the test Date, reverted Status to Todo ...

$ python3 bin/sync-roadmap-status.py Twin-Cities-Open-Systems 1
0 item(s) need a Status change:
```

## Open question this doesn't resolve

`--threshold-days` defaults to 59 (the `roadmap` repo README's
repin-creation-cadence mean+1stdev candidate) -- flagged there as not
yet confirmed by Spencer, whose own math (a "5m slumber" cadence graph
for tcos.us, requested via AI Mode) may be the better real dataset.
Not yet reconciled with this tool's default -- see `roadmap`'s README
for the live state of that question.
