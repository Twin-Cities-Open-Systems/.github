---
organization: Twin-Cities-Open-Systems
version: 1.0.0
last_updated: 2026-08-24
type: Organizational-Invariant-Declaration
---

# TCOS Global Glossary & Invariant Declaration

This document serves as the immutable, single source of truth (SSoT) for terminology, acronym definitions, and systemic invariants across all Twin-Cities-Open-Systems (TCOS) codebases, documentation files, and narrative engines.

---

## 1. Core Dictionary & Invariants

### Twin Cities Open Systems
* **Type:** Organization Name
* **Invariant Standard:** Must always be written as `Twin-Cities-Open-Systems` in configuration files or hyphenated/capitalized as `Twin Cities Open Systems` in prose. Never abbreviate to lowercase `tcos` in formal external communications.
* **Legal-entity form:** In any public-facing context that needs the legal entity, not just the org name, use `Twin Cities Open Systems (TCOS), LLC` or the short form `TCOS (LLC)`. Authority for the entity's real identifiers (EIN, filing details, formation dates) lives in `tcos-plan-private`, never here.
* **Identifier redaction (real invariant, not just a style note):** EIN, tax IDs, and legacy/superseded entity identifiers must never appear in this repo or any other public-facing surface -- state that they're tracked privately instead of naming or partially redacting them.

### TCOS Private Enterprise Number (PEN)
* **Type:** Real, externally-registered technical identifier
* **Invariant Standard:** TCOS's real IANA-assigned Private Enterprise Number is **66550**, registered to "Twin Cities Open Systems - Operations LLC." Unlike an EIN or tax ID, a PEN is meant to be public -- it's the base OID arc (`1.3.6.1.4.1.66550`) any TCOS tooling uses when it needs a real, globally-unique identifier (SNMP MIBs, X.509 extensions, or similar namespaced metadata). Independently verifiable at any time against IANA's own registry: `https://www.iana.org/assignments/enterprise-numbers.txt`. Never invent or guess a substitute number -- 66550 is the one real, assigned value.

### Determinism
* **Type:** Core Execution Principle
* **Invariant Standard:** One of `human-execution-engine`'s three explicit top-level priorities, stated directly in its own README: "correctness over consensus, structure over vibes, **determinism over convenience**." Means the same real inputs produce the same real outputs and the same real decisions, reproducibly -- not "usually," not "close enough." Concretely enforced today as **deterministic identity** (doctrine objects use a `seed` + derived `id`, never a randomly-assigned one, so identity survives re-runs and stays auditable/merge-safe) and **deterministic scheduling/orchestration** (work is scheduled and evaluated by explicit rules, not left to incidental ordering). Real, heavily-used term across the codebase -- not aspirational language.

### Pedigree
* **Type:** Organizational Paradigm
* **Invariant Standard:** Refers exclusively to the proven track record, core credentials, and structural lineage of system owners or foundational intellectual property within the `human-execution-engine`.

### Glass
* **Type:** Architectural Layer
* **Invariant Standard:** Refers strictly to bare-metal hardware monitor displays managed by `glass-ops`. Never use to describe cloud dashboards or web-based frontend browser views.

### Logic Loop
* **Type:** Governance Failure Mode
* **Invariant Standard:** A rule that still reads as active, absolute policy on paper but has no real bearing on actual practice -- either because practice quietly diverged from it, or because it was never actually enforced. Named for the shape of the failure: the rule points at itself ("this is the policy") without a live edge back to real behavior, so it loops rather than governs. Real, confirmed instances, found 2026-08-26 auditing `docs/doctrine/HEE_POLICY.md` after a heavy merge session: §2 (Branch Management Policy) requires `feature/`-prefixed branch names deleted immediately post-merge -- real practice is 71 `touchy/`-prefixed branches kept post-merge as an audit trail, vs. 5 real `feature/` branches, and `touchy/` is undocumented anywhere; §6 (Command Safety Policy) requires `bash -n` syntax validation "for all shell commands" -- not actually run before most one-off commands in real sessions. Confirmed, Spencer directly: §§1-6 read as legacy/template boilerplate predating the fleet's real established practice, not live-authored policy like §7 onward. Per the Canonization Policy (`docs/doctrine/HEE_POLICY.md` §19): finding a logic loop means surfacing the tension and getting a real human call on which side wins -- formalize practice into doctrine, or start actually enforcing the written rule -- never silently picking one or leaving it unremarked.

### Ratify
* **Type:** Governance Action
* **Invariant Standard:** The real verb for a Contract moving from `status: proposed` to `status: ratified` -- an authorized OPER's real GPG signature, never a GitHub approve-click (self-approval can't be enforced when proposer and approver share an account) and never a majority vote. Covers both flows that produce this outcome: the per-contract path (`tools/hee/ratify-contract.sh`, documented in the `ratify-contract-v1` Skill) and the batch/mass-decision path (`hee-contract-review --action sign`, which loops every `status: proposed` contract in priority order for the same real signature). "Sign" names the mechanical GPG act inside that flow; "ratify" names the governance outcome it produces -- use "ratify" when describing what happened to the contract, "sign" only when describing the specific GPG step. Never "promote" -- that verb is already real and distinct (`deploy.sh promote`, lab-to-prod deployment) and using it for contracts collides with that meaning. Never "vote" -- HEE contract ratification is single-authorized-signer verification, not multi-party consensus; "vote" implies a mechanism the system doesn't have. Canonized 2026-08-26, Spencer: "yes, canonize."

### Hacking
* **Type:** Culture Term — **Status: Stub, pending Spencer's review, not settled**
* **Invariant Standard (draft):** Hacker-culture sense only — real, fast, hands-on building/tinkering/improving on a real machine (e.g. "raising the tempo on hacking kiosk," 2026-08-26). Never the intrusion/exploitation sense. Drafted as a stub per Spencer's direct instruction ("a stub I will review as p2") rather than a full canonized entry — content here is provisional until he reviews it.

### Block
* **Type:** Governance Action
* **Invariant Standard:** To block an Issue or PR means submitting a real, GitHub-native `gh pr review --request-changes` with the concrete technical reason documented in the review body -- never just a comment saying "don't merge," which carries no real enforcement and can be scrolled past. On any repo with `required_approving_review_count >= 1` (check via `gh api repos/<owner>/<repo>/branches/<branch>/protection`), a `CHANGES_REQUESTED` review decision actively disables the merge button for a normal merge -- verify the block landed via `gh pr view <n> --json reviewDecision`, don't just trust the command exited clean. Real precedent: [thesis-engine#15](https://github.com/Twin-Cities-Open-Systems/thesis-engine/pull/15), blocked 2026-08-26 with the exact `npm ci` failure output in the review body, not a vague objection. Note the real limit, honestly: `enforce_admins: false` on most repos in this org means an admin can still force-merge past a block -- the review makes the objection real and visible, it doesn't make bypass impossible, and bypassing a documented block is a deliberate act, not an accident.
* **Not the same as**: closing an Issue/PR (ends it), a `wontfix`/`invalid` label (a status, not an active gate), or a plain comment (no enforcement).

### Green
* **Type:** Org-Wide State
* **Invariant Standard:** The real, org-wide pre-condition for a tagged release -- CI clean across repos, real backlog fields filled (Type/Priority/Effort, per HEE Policy §18), no stale/cruft issues, open PRs at or near zero. Not a per-repo CI status color (that's just "passing"/"failing") -- Green names the whole-org state itself. Fits the org's own established 🔴🟡🟢 status-dot convention rather than inventing new vocabulary. Canonized 2026-08-26, Spencer: "green it is," coined in his own words earlier the same session ("so close to being fully green and stable, then we can do tagged release").

### Heuristics
* **Type:** Practice/Method
* **Invariant Standard:** Real, named judgment-call reasoning used when full independent verification isn't possible -- checking internal consistency and plausibility (does the content match what a real instance of this thing should look like) rather than asserting confirmation that doesn't exist. Real precedent, 2026-08-26: verifying [inbound#13](https://github.com/Twin-Cities-Open-Systems/inbound/issues/13) (a real application submission) by checking whether the name/email were plausible and whether the body content read as a genuine message vs. placeholder text ("Qwerty / Wizzy wig") -- not claiming identity was confirmed, since it wasn't, just reporting what the heuristic actually showed and flagging the gap explicitly ("I can't independently verify identity from a name+email alone"). The discipline is in the honesty: heuristics narrow uncertainty, they don't manufacture certainty -- state which one you got, never claim the other.

### Gloss It Up
* **Type:** Meta/Process Term
* **Invariant Standard:** The real verb for adding a new term to this glossary -- coined by Spencer in the act of doing it ("what they call heuristics, add to gloss / 'gloss it up'"), self-referential by design (glossary -> gloss it up). Every real entry in this document should be grounded in a concrete, dated precedent from an actual session, not an abstract definition invented in isolation -- that's been true of every entry canonized 2026-08-26 (Ratify, Hacking, Block, Green, Heuristics) and is the real standard "gloss it up" names going forward.

### Documentation Invariant
* **Type:** Transparency Security Gate
* **Invariant Standard:** No private structural details, operational API keys, specific vendor names, or target asset metrics may ever be written into the text descriptions of repositories marked as `(Private)` or `(Very Private)`. All private repository entries must use abstract operational language.

### Opus
* **Type:** Generated-Output Layer
* **Invariant Standard:** The generated-outputs hierarchy and working surface for machine friends — rendered HTML, MD, YAML, text, EXIF, and image forms of cards, pills, contracts, plans, blueprints, and evidence. Refers strictly to *rendered/generated* output, never to source or authored content. Source of record: `human-execution-engine/hee/cards/hee-words.seed.card.v1.yaml`.

### Corpus
* **Type:** Inventory Concept — **Status: Thesis, not settled doctrine**
* **Invariant Standard:** The whole real body of what actually exists in a given repo (or, extended, the org) — source and generated content alike. Distinct from Opus (which names the generated/rendered layer specifically): a Corpus is the larger whole an Opus is rendered from and lives inside. Real precedent, tested in two repos, one result each: `.github`'s top-level `CORPUS.md` (proposed [`.github`#26](https://github.com/Twin-Cities-Open-Systems/.github/pull/26)) drifted into near-total duplication of that repo's own `README.md`/`OPERATORS.md` and was removed as part of the 2026-08-27 instruction-set consolidation, per this thesis's own stated exit condition -- exactly the "if it drifts stale faster than it's useful, remove it" case. `human-execution-engine`'s `CORPUS.md` (proposed [`human-execution-engine`#251](https://github.com/Twin-Cities-Open-Systems/human-execution-engine/pull/251)) is still open and, unlike the removed copy, points at real auto-generated indexes (`docs/THESIS_INDEX.md`, `docs/history/PILL_INDEX.md`) it doesn't itself duplicate -- unproven, not yet judged either way.

### Agent
* **Type:** Role — **Machine-Rights Party**
* **Invariant Standard:** The machine-rights party in any process/documentation prose that distinguishes who is doing something -- as opposed to `Oper`, the human-rights party. Same shape of rule as the org's existing "no vendor names in generic docs" convention (say `agent`, never `claude`/`Claude Code`/etc., in generic prose) -- extended one level further: generic, unqualified "agent(s)" language that's actually trying to distinguish a human from a machine is itself now imprecise; use the real pair (`agent`/`Oper`) instead. Vendor-neutral naming in code/config/identity labels (preferring `agent` over a vendor-specific name) is a separate, unaffected concern at a different layer -- see `docs/DOCUMENTATION_POLICY.md` rule 2, which this entry sharpens into a concrete required pair rather than just a prohibition. Canonized 2026-08-27, Spencer: "similar to 'no vendors' no 'agents' in generic documentation or process. prefer agent(machineRights) oper(humanRights)."
* **Not the same as**: the dead `COG`/`OPER`/`AGENT` three-role split that used to live in `human-execution-engine`'s `docs/doctrine/FROZEN_CONTRACTS.md` (removed 2026-08-27 as dead vocabulary matching nothing in real practice) or the equally-dead two-role `AGENT`/`OPERATOR` split from the same repo's `HEE_EXECUTION_ATTRIBUTION.md` (also removed) -- both used "AGENT" to mean something else (a party that never executes, or one role among three), not the machine-rights party this entry defines. This is a real, live, deliberately re-introduced pair, not a revival of either dead one.

### Oper
* **Type:** Role — **Human-Rights Party**
* **Invariant Standard:** The human-rights party, paired with `Agent` (the machine-rights party) -- see that entry for the full rule and canonization citation. Already real, pre-existing usage across the org before this pairing was made explicit (`SRO` = *Single Responsible Operator*; `hee_git_ops.sh`'s own comments distinguish agent mutation gating from human/oper action) -- this entry doesn't introduce the word, it canonizes the distinction it draws against `Agent`.

### Gold
* **Type:** Design/UX System
* **Invariant Standard:** The real UX/UI system originated on `view.lab.tcos.us` (og:site_name literally "TCOS View") -- teal accent (`#0d7d78` light / `#3fd4c8` dark), IBM Plex Sans (body) + JetBrains Mono (mono/labels), light/dark/auto toggle defaulting dark, card-based `section`/`.link-card` layout. Named for what everyone was already calling it in real conversation, 2026-08-28: "view.lab is the gold standard." Canonized as the org's adopted default for reskinning any real surface -- concrete precedent: resume#32 (blog-hub.html/media-hub.html) and fleet-ops#330 (foo/man gopher pages) both ported off it verbatim, replacing an unrelated green-terminal look. Distinct from `tcos-www`'s own separate `tc-shell`/`tc-grid`/`tc-theme` system (amber accent, no named webfont) -- the two are not yet reconciled; see the still-open question of whether tcos-www itself adopts Gold.
* **Not the same as**: `Opus` (the generated-output layer), or "gold standard" used as a plain English phrase elsewhere -- capitalized `Gold` names this specific design system.
* **Naming convention, established here**: a real design system's font pairing is its defining, identifying signature -- Gold *is* "IBM Plex Sans - JetBrains Mono" (Spencer, direct, 2026-08-28: "this is the name... the next one will follow suite in future"). `check_gold_og.py`'s font check already treats this as the adoption signal, not just a style detail. Any future named system in this org should be identified the same way: by its own font pairing, not a generic label.

---

## 2. Acronym Expander

| Shorthand | Expanded Meaning | Associated Core Repository |
| :--- | :--- | :--- |
| **TCOS** | Twin Cities Open Systems | `Twin-Cities-Open-Systems/.github` |
| **NLP** | Natural Language Processing | `market-thesis-news` |
| **HEE** | Human Execution Engine | `human-execution-engine` |
| **MT** | Market Thesis | `market-thesis` |
| **PII** | Personally Identifiable Information | `tcos-audit` |
| **IP** | Intellectual Property | `tcos-plan-private` / `thesis-engine` |
| **SSoT** | Single Source of Truth | Global Platform |
| **PEN** | Private Enterprise Number (IANA-assigned) | Global Platform |
| **SRO** | Single Responsible Operator -- one named human (Spencer Butler) has sole approval authority for a given scope, no committee/multi-party vote. Currently the real authority model for `human-execution-engine`'s CI governance rules (`docs/governance/operations/GOVERNANCE_OPERATIONS.md`) | `human-execution-engine` |
| **RFC** | Request for Comment -- an open question needing real discussion before action, not yet a decision. Real doc type (`docs/rfc/`, per `docs/DOCUMENTATION_POLICY.md`) and a real GitHub label, both in active use | `human-execution-engine` |

Added 2026-08-27 (SRO, RFC) after a real sweep of the core doctrine files
prompted by Spencer catching `SRO` undefined mid-review. **Not resolved by
that sweep**: `HEER` appears three times in `HEE_POLICY.md` §4/§7 with no
expansion anywhere in the repo -- those sections are part of the same
generic/undated authorial-voice pattern already flagged as suspect (unlike
§2/§6, not yet confirmed as drifted-from-practice, so not silently
rewritten or removed here) -- needs a real answer from Spencer, not an
invented one. This wasn't an exhaustive audit of every acronym in every
file org-wide, just the core always-loaded doctrine set — a wider sweep is
still open (see `view.lab.tcos.us/follow-up.html` #6).

---

## 3. Systematic Thesaurus (Context Mapper)

* **Instead of:** `credentials`, `resume profile`, `history`
  * **Use TCOS Standard:** `Pedigree` (when referring to founder backgrounds) or `Track Record` (when referring to repository execution history).
* **Instead of:** `cron job`, `task manager`, `script loop`
  * **Use TCOS Standard:** `Tick-Task Event` (when running high-frequency sub-millisecond execution loops via `tick-task`).
* **Instead of:** `frontend`, `ui layout`, `desktop setup`
  * **Use TCOS Standard:** `Glass Operations` or `Monitor Glass Interface` (handled natively by `glass-ops`).
* **Instead of:** `secrets scan`, `leak check`
  * **Use TCOS Standard:** `Custodian Custody Review` (enforced via `tcos-audit`).
* **Instead of:** `file a bug`, `report a bug`, `log a defect`
  * **Use TCOS Standard:** open a real GitHub issue in the affected repo with `issue-type-bug` (the repo's real bug-type label or issue-type field, whichever that repo uses) -- not a chat message, a card, or a doc note. "File a bug" always means this concrete action.

---

## 4. Scripting & Code Header Invariants

### Mandatory Execution Block (First 4 Lines)
Every script executing inside a userland shell layer must match this structural signature across its initial 4 lines without exception:

1. **Line 1:** Portable Shebang Directive (`#!/usr/bin/env <tool_name>`)
2. **Line 2:** Author Attribute & Target Domain (`# Developer Name <email@tcos.us>`)
3. **Line 3:** Exact Base Filename (`# filename.extension`)
4. **Line 4:** High-Level Functional Abstract (`# This script executes foo, bar, and baz.`)

### Library & Mixin Invariant (Non-Executable Scripts)
* **Type:** Structural Code Paradigm
* **Invariant Standard:** Code assets containing reusable function blocks, hooks, or environment wrappers (e.g., `cron_sweep_repo.bash`) that are designed exclusively to be sourced by other runtime controllers must not contain a shebang line and must remain non-executable (`chmod -x`).
