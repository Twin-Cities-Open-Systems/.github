# `sync-roadmap-status.py` — real run, including a real correction

Real trigger, 2026-08-21: Spencer wants a ticket's `Status` (Todo /
Near Future Todo / In Future) to auto-derive from its date, not require
hand-flipping a dropdown — "shit just auto updates the right shit."
Dogfoods `roadmap`'s "in future" bucket concept using today's real date
as the epoch-0 stand-in, since HEE's own `heeEpoch` isn't ratified
anywhere real yet.

## A real mistake, caught before it stuck

The first version of this tool created its own `Date`/`Effort` custom
fields directly on the `TCOS Roadmap` Project (`manage-project.py`'s
new `fields:` support). That was wrong — Spencer was already using a
different, real GitHub feature: repo/org-level **Issue Type custom
fields** (`Priority`/`Start date`/`Target date`/`Effort`, visible in
the issue sidebar's "Fields" section — a newer feature, not a Projects
v2 custom field). Confirmed by a screenshot on
[fleet-ops#201](https://github.com/Twin-Cities-Open-Systems/fleet-ops/issues/201)
showing `Priority: High`, `Target date: Aug 21, 2026`, `Effort: High`
already set there.

Once caught: deleted the unused Project fields
(`deleteProjectV2Field`), reverted `manage-project.py`'s `fields:`
addition entirely (no real dogfooded use for it once the actual target
turned out to be a different API), and rewrote this tool to read the
real `issueFieldValues`/`Target date` field instead. Recorded here
rather than quietly dropped, per this org's own "verify, don't
fabricate" standard applying to its own tools too.

## Real run against the live `TCOS Roadmap` project

```
$ python3 bin/sync-roadmap-status.py Twin-Cities-Open-Systems 1
=== sync-roadmap-status: Twin-Cities-Open-Systems#1, threshold=59d, today=2026-08-21 ===

7 item(s) need a Status change:
  https://github.com/Twin-Cities-Open-Systems/human-execution-engine/issues/216  Todo -> Near Future Todo  [IMPLEMENTATION_MANUAL]
  https://github.com/Twin-Cities-Open-Systems/fleet-ops/issues/201  Todo -> Near Future Todo  [Squarespace domain-invite acceptance blocked: glas]
  https://github.com/Twin-Cities-Open-Systems/fleet-ops/issues/200  Todo -> Near Future Todo  [Idea: Board Ops — hardware hacking projects, first]
  https://github.com/Twin-Cities-Open-Systems/tcos-www/issues/25  Todo -> Near Future Todo  [Feature: Smooth UI/UX in the www]
  https://github.com/Twin-Cities-Open-Systems/tcos-www/issues/15  Todo -> Near Future Todo  [Idea: competing epoch counters on tcos.us -- which]
  https://github.com/Twin-Cities-Open-Systems/human-execution-engine/issues/248  Todo -> Near Future Todo  [Epic: OWNER-ROOT-MIB (PEN 66550) — fleet governanc]
  https://github.com/Twin-Cities-Open-Systems/human-execution-engine/issues/210  Todo -> Near Future Todo  [Idea: kernel-level HEE verification (IMA/EVM first]

36 item(s) in the Todo/Near/In-Future family have no Target date set (left alone, not guessed):
  ... (36 real items, not reproduced here)

21 item(s) not in scope (In Progress/Done/other, or a PR -- Target date is Issues-only) -- untouched

Dry run -- no writes made. Re-run with --apply to actually update Status.
```

Applied for real (`--apply`) — all 7 confirmed via a second dry-run
immediately after, which correctly reported 0 remaining changes.

## Open question this doesn't resolve

`--threshold-days` defaults to 59 (the `roadmap` repo README's
repo-creation-cadence mean+1stdev candidate) — flagged there as not yet
confirmed. Spencer's own preferred methodology (a commits-per-period
"slumber" measure, the real precedent for which is
`tcos-www`'s `story.html` "The other timeline" section — 92 commits
Jan, 60 Feb–Mar, 0 Apr–Jul, a real 5-month gap) hasn't been reconciled
with this tool's default yet. See `roadmap`'s README for the live state
of that question.
