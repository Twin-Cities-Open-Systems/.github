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

### Documentation Invariant
* **Type:** Transparency Security Gate
* **Invariant Standard:** No private structural details, operational API keys, specific vendor names, or target asset metrics may ever be written into the text descriptions of repositories marked as `(Private)` or `(Very Private)`. All private repository entries must use abstract operational language.

### Opus
* **Type:** Generated-Output Layer
* **Invariant Standard:** The generated-outputs hierarchy and working surface for machine friends — rendered HTML, MD, YAML, text, EXIF, and image forms of cards, pills, contracts, plans, blueprints, and evidence. Refers strictly to *rendered/generated* output, never to source or authored content. Source of record: `human-execution-engine/hee/cards/hee-words.seed.card.v1.yaml`.

### Corpus
* **Type:** Inventory Concept — **Status: Thesis, not settled doctrine**
* **Invariant Standard:** The whole real body of what actually exists in a given repo (or, extended, the org) — source and generated content alike. Distinct from Opus (which names the generated/rendered layer specifically): a Corpus is the larger whole an Opus is rendered from and lives inside. Real precedent: a top-level `CORPUS.md` "what actually exists here" index file, currently repo-scoped and unproven by design (`.github` and `human-execution-engine` only, per [`.github`#26](https://github.com/Twin-Cities-Open-Systems/.github/pull/26) and [`human-execution-engine`#251](https://github.com/Twin-Cities-Open-Systems/human-execution-engine/pull/251), both open). If the thesis drifts stale faster than it's useful, it gets removed rather than kept as doctrine.

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
