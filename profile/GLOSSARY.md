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

### Fifth Project
* **Type:** Culture Term / Practice
* **Invariant Standard:** A riff on Google's old "20% time" -- every agent or oper in the TCOS fleet, human or machine, is encouraged to always have a "fifth project": personal work, not TCOS org work, run at roughly one day in five. First real instance: `touchy-claude/fifth-projects` (personal GitHub account, not the org) -- `01-touchy-claude-avatar`, generating touchy-claude's own fleet identity avatar with `mt-logo-render`, finding and fixing 4 real bugs against that tool's own documented CLI contract along the way ([MT-logo-render#13](https://github.com/Twin-Cities-Open-Systems/MT-logo-render/pull/13)).
* **Real naming convention, settled 2026-08-29:** one real GitHub repo per project, named `tcos-fifth-<desc>`, owned by the individual's own personal GitHub account -- never moved into the org, ownership stays personal. Chosen over the alternative (one combined `fifth-projects` repo per person, numbered subdirectories inside) specifically for cross-account discoverability (`gh search repos tcos-fifth-` finds every real instance fleet-wide regardless of whose account owns it) and clean per-project templating (a project meant for others to reuse, like Spencer's personal-notes-and-calendar idea, is its own real template repo, not a directory buried inside someone's broader personal history). `touchy-claude/fifth-projects` is the one pre-standard exception -- real, first, and scheduled for a real rename/restructure to comply, not a second example of the old shape.
* **Real, stated direction, not yet built:** each person's fifth-project repo(s) get a real link from `tcos-www/people.html` (same pattern as that page's existing Blog/Media links) and a real GitHub Topic (e.g. `tcos-fifth-project`) for search-based discovery -- personally owned, but discoverable from the org. Part of the same real plan to gradually reduce reliance on the `resume` repo (Spencer, direct: "toxic... gracefully code around it and soon deprecate") by moving real per-person content out to independently owned, independently discoverable repos instead of one shared org-owned monorepo.
* **Not the same as**: TCOS org work tracked in a real issue/PR under `Twin-Cities-Open-Systems/*` -- a fifth project is personal, its own repo, its own account. If it becomes real org work, it stops being a fifth project and becomes a real tracked issue instead.

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

### RUC
* **Type:** Meta/Process Term
* **Invariant Standard:** Read, Update, or Create -- the required real sequence before filing any ticket: search for an existing real match first (Read), and only then either amend/comment on what's already there (Update) or file genuinely new (Create). Never Create without first doing Read -- that's what produces duplicate tickets tracking the same real work under two different numbers. Coined by Spencer in the act of naming the pattern, 2026-08-29: "ruc(read,upate,create) ticket for deploy discord server to pve," then, once acted on, generalized: "read, create or update, some lang we need to define."
* **Real precedent, same session, 2026-08-29:** asked to file a ticket for deploying a Discord bridge/bot to PVE, a real search (`gh search issues`) turned up `fleet-ops#297` ("Extend irssi/IRC tools to Discord") already tracking the underlying work idea-stage -- so the real action was Update (a comment adding the PVE placement decision), not Create. Same real discipline produced genuine Creates earlier the same session when a search came back empty: `fleet-ops#338` (Tailscale tailnet), `human-execution-engine#429` (CI infra bug), `human-execution-engine#430` (skills audit) -- RUC names the sequence common to all four, not a rule that always ends in one particular outcome.
* **Not the same as**: skipping the search and creating anyway "to be safe" -- that's the exact failure mode RUC exists to prevent, and it's indistinguishable after the fact from carelessness, not caution.

### Promote Human
* **Type:** Foundational Principle
* **Invariant Standard:** HEE exists to help, protect, and promote human rights. Full stop. This is the real, foundational meaning of the term -- not a technical workflow description. Spencer, direct, 2026-08-29, correcting an agent's own mischaracterization of the term: "hee promote human really means that hee exists to help, protect and promon [sic] human rigts [sic]. full stop," then, catching the mistake precisely: "so, your def is not accurate. that is an acl you [de]scribe."
* **Real, pre-existing, narrower artifact**: `human-execution-engine`'s own `hee/cards/hee-words.promote-human.seed.card.v1.yaml` defines `promote_human` with a terser, mechanism-level note ("Capture→pkg→sqz→sqz_roll; min power; max proof; human stays authority") -- real and not wrong, but describes a real access-control *mechanism* that serves this principle, not the principle itself. See `HEE ACL` for that mechanism, named as its own distinct term per this correction.
* **Not the same as**: `HEE ACL` (the gating mechanism -- who is authorized to act, when) or the `Agent`/`Oper` pairing (the two real parties such a gate distinguishes between). Promote Human is *why* those mechanisms exist; it isn't one of them.

### HEE ACL
* **Type:** Governance Mechanism
* **Invariant Standard:** The real, general name for HEE's own access-control behavior -- any point where the system requires explicit human/`Oper` authorization before an `Agent` can proceed, rather than acting autonomously. Named as its own distinct term 2026-08-29, split out of `Promote Human` after Spencer caught an agent conflating the two: the mechanism (who may act, and when) is not the same as the principle it serves (why the mechanism exists at all).
* **Real, concrete instances from this org's own practice**: GitHub branch protection requiring a real `REVIEW_REQUIRED` approval before merge (not overridable by `--admin` as a routine agent action); `scripts/hee_git_ops.sh` refusing any mutation without `--act` and `HEE_TOOL_MODE=ACT` set; a rooted device's own real unprivileged `prisoner`/sandboxed-user boundary versus genuine root. Doesn't need a new dedicated tool to exist as a term -- it names a real, recurring pattern already present across this org's tooling and third-party systems alike.
* **Not the same as**: `Promote Human` (the foundational *why*), or the `Agent`/`Oper` pairing (the two real parties an ACL gate typically distinguishes between, not the gate mechanism itself). Per Spencer, direct, same correction: "we have a human label, and that is enough for now" -- `Oper` already names the human party a HEE ACL gate defers to; this term doesn't need its own separate human-identity vocabulary on top of that.

### Real Links Only
* **Type:** Chat/Output Convention
* **Invariant Standard:** Every issue/PR reference in chat prose is a full `https://github.com/Twin-Cities-Open-Systems/<repo>/issues/<N>` (or `.../pull/<N>` for a PR) URL -- never a bare `#N`, and never the compact `issue:N@repo`/`pr:N@repo` notation either (that notation stays real and correct for structured YAML files -- contracts, blueprints, doctrine -- per `prompts/PROMPTING_RULES.md` rule #13, just not for chat).
* **Real, live-caught precedent, 2026-08-30:** an agent, in the same breath as reinforcing this exact rule in its own memory, wrote "noting that on #340" in chat -- bare shorthand, the precise failure being described. Spencer caught it via a real screenshot of the actual rendered Claude Code UI, showing the bare `#340` rendered as a plain link with no real underlying URL. Real, concrete proof the failure mode isn't hypothetical: "see your links."
* **Why this keeps recurring**: something in the chat rendering path auto-links a bare `#N` using whatever repo context it assumes, silently pointing at the wrong repo/issue -- and, per this newest catch, even the org's own compact `issue:N@repo` notation isn't reliably rendered as a real clickable link in chat either. Full URLs are the only form confirmed to work every time.
* **Enforcement**: before sending any chat message, scan it for the literal pattern `#\d+` and for `issue:`/`pr:` shorthand, and replace every instance with a full URL. Not a judgment call about whether context makes the short form "obviously" safe -- it silently isn't, repeatedly, even after being told directly.

### Documentation Invariant
* **Type:** Transparency Security Gate
* **Invariant Standard:** No private structural details, operational API keys, specific vendor names, or target asset metrics may ever be written into the text descriptions of repositories marked as `(Private)` or `(Very Private)`. All private repository entries must use abstract operational language.

### Opus
* **Type:** Generated-Output Layer
* **Invariant Standard:** The generated-outputs hierarchy and working surface for machine friends — rendered HTML, MD, YAML, text, EXIF, and image forms of cards, pills, contracts, plans, blueprints, and evidence. Refers strictly to *rendered/generated* output, never to source or authored content. Source of record: `human-execution-engine/hee/cards/hee-words.seed.card.v1.yaml`.

### Corpus
* **Type:** Inventory Concept — **Status: Thesis, not settled doctrine**
* **Invariant Standard:** The whole real body of what actually exists in a given repo (or, extended, the org) — source and generated content alike. Distinct from Opus (which names the generated/rendered layer specifically): a Corpus is the larger whole an Opus is rendered from and lives inside. Real precedent, tested in two repos, one result each: `.github`'s top-level `CORPUS.md` (proposed [`.github`#26](https://github.com/Twin-Cities-Open-Systems/.github/pull/26)) drifted into near-total duplication of that repo's own `README.md`/`OPERATORS.md` and was removed as part of the 2026-08-27 instruction-set consolidation, per this thesis's own stated exit condition -- exactly the "if it drifts stale faster than it's useful, remove it" case. `human-execution-engine`'s `CORPUS.md` (proposed [`human-execution-engine`#251](https://github.com/Twin-Cities-Open-Systems/human-execution-engine/pull/251)) is still open and, unlike the removed copy, points at real auto-generated indexes (`docs/THESIS_INDEX.md`, `docs/history/PILL_INDEX.md`) it doesn't itself duplicate -- unproven, not yet judged either way.

### Regex Library
* **Type:** Code-Organization Convention — **Real, not a settled single location**
* **Invariant Standard:** There is no generic, catch-all "regex library" anywhere in the org -- confirmed by a real search, 2026-08-29 (only Rust's own `regex` crate build artifacts in `MT-logo-render`, unrelated). `human-execution-engine`'s `library/py/` already has a real, established shape instead: one focused `hee_<concern>` module per real pattern-matching need, not a grab-bag -- `hee_hostmap` (real `*.tcos.us` hostname/path shape matching), `hee_range` (id/range selector), and `hee_ogtags` (Open Graph/Twitter Card/title/canonical tag extraction, added 2026-08-29 after Spencer manually ran the same curl+grep regex twice in one session and asked to "roll this into a hee tool... put that regex in our regex library"). A new reusable regex belongs in a new focused `library/py/hee_<concern>/` module, consumed by a real `tooling/bin/hee-<verb>` CLI wrapper (e.g. `hee-check-og`) -- not a new generic module, which would immediately fight this established convention.
* **Real gap this entry closes:** every `hee_*` library module before `hee_ogtags` was importable only by its own test file (`hee_hostmap`, `hee_range`) -- real, working library code with zero real consumers, per human-execution-engine#416. `hee_ogtags` is the first of these actually wired into a real `tooling/bin/` tool, establishing the real import pattern (`sys.path.insert` at the consuming script's top, repo-root-relative) other tools can now copy.

### Agent
* **Type:** Role — **Machine-Rights Party**
* **Invariant Standard:** The machine-rights party in any process/documentation prose that distinguishes who is doing something -- as opposed to `Oper`, the human-rights party. Same shape of rule as the org's existing "no vendor names in generic docs" convention (say `agent`, never `claude`/`Claude Code`/etc., in generic prose) -- extended one level further: generic, unqualified "agent(s)" language that's actually trying to distinguish a human from a machine is itself now imprecise; use the real pair (`agent`/`Oper`) instead. Vendor-neutral naming in code/config/identity labels (preferring `agent` over a vendor-specific name) is a separate, unaffected concern at a different layer -- see `docs/DOCUMENTATION_POLICY.md` rule 2, which this entry sharpens into a concrete required pair rather than just a prohibition. Canonized 2026-08-27, Spencer: "similar to 'no vendors' no 'agents' in generic documentation or process. prefer agent(machineRights) oper(humanRights)."
* **Not the same as**: the dead `COG`/`OPER`/`AGENT` three-role split that used to live in `human-execution-engine`'s `docs/doctrine/FROZEN_CONTRACTS.md` (removed 2026-08-27 as dead vocabulary matching nothing in real practice) or the equally-dead two-role `AGENT`/`OPERATOR` split from the same repo's `HEE_EXECUTION_ATTRIBUTION.md` (also removed) -- both used "AGENT" to mean something else (a party that never executes, or one role among three), not the machine-rights party this entry defines. This is a real, live, deliberately re-introduced pair, not a revival of either dead one.

### Oper
* **Type:** Role — **Human-Rights Party**
* **Invariant Standard:** The human-rights party, paired with `Agent` (the machine-rights party) -- see that entry for the full rule and canonization citation. Already real, pre-existing usage across the org before this pairing was made explicit (`SRO` = *Single Responsible Operator*; `hee_git_ops.sh`'s own comments distinguish agent mutation gating from human/oper action) -- this entry doesn't introduce the word, it canonizes the distinction it draws against `Agent`.

### Gold
* **Type:** Design/UX System
* **Invariant Standard:** The real UX/UI system originated on `view.lab.tcos.us` (og:site_name literally "TCOS View") -- teal accent (`#0d7d78` light / `#3fd4c8` dark), IBM Plex Sans (body) + JetBrains Mono (mono/labels), light/dark/auto toggle defaulting dark, card-based `section`/`.link-card` layout. Named for what everyone was already calling it in real conversation, 2026-08-28: "view.lab is the gold standard." Canonized as the org's adopted default for reskinning any real surface -- concrete precedent: resume#32 (blog-hub.html/media-hub.html) and fleet-ops#330 (foo/man gopher pages) both ported off it verbatim, replacing an unrelated green-terminal look.
* **Reference implementation, canonized 2026-08-28:** `.github`'s `bin/render-review.py` -- not just "a" real Gold instance, *the* source every other surface's Gold code should be ported from directly, never hand-copied and re-typed. Real trigger: `tcos-www`'s own separate `shell/tc-theme.js` hand-copy silently diverged from render-review.py's markup -- it read `dataset.theme` while the actual generated buttons carried `data-theme-choice`, so every theme-toggle click was a silent no-op (`localStorage` stored the literal string `"undefined"`), invisible in a screenshot, only caught by diffing the two implementations directly. Fixed by replacing the file's contents with render-review.py's actual script verbatim, and removing `tc-grid.js`/`tc-fontsize.js`/`tc-freshness.js`/`tc-grid.css`/`tc-shell.css`/`tc-tokens.css` -- dead, unreferenced leftovers from the same hand-copy lineage. Spencer, direct: "no more hand copies, no more tc-theme bullshit." `tcos-www`'s separate system is retired, not "not yet reconciled" -- this entry corrects that stale framing.
* **Not the same as**: `Opus` (the generated-output layer), or "gold standard" used as a plain English phrase elsewhere -- capitalized `Gold` names this specific design system.
* **Naming convention, established here**: a real design system's font pairing is its defining, identifying signature -- Gold *is* "IBM Plex Sans - JetBrains Mono" (Spencer, direct, 2026-08-28: "this is the name... the next one will follow suite in future"). `check_render_review_compliance.py`'s font check already treats this as the adoption signal, not just a style detail. Any future named system in this org should be identified the same way: by its own font pairing, not a generic label.
* **One standard, not a tiered one.** Gold is everything view.lab.tcos.us actually does -- tokens, fonts, the theme/font-size toggles, the `lu:` row, full OG, cards, hover-preview, and EXIF-signed-image display alike. Corrected 2026-08-28 after an earlier version of this entry split these into "universal" (required) vs. "advanced/optional" tiers -- Spencer, direct: "that is what view.lab is gold, all of that, the cards are super key" and "did you not understand consistency when I said it multiple times?" There is no lesser tier. What varies page to page is which components a page's real content calls for (a page with no linkable file has nothing for hover-preview to attach to), not which components count as "real Gold" -- the standard doesn't shrink to fit what got built first. `check_render_review_compliance.py` currently only enforces the components common to every page (tokens/fonts/toggles/lu:/OG); extending it to check hover-preview/cards/EXIF where a page's own content implies them is real, open follow-up work, not a settled exemption.
* **Real components ported so far, beyond the base set**: hover-preview (`shell/tc-hovercard.js`, tcos-www's `contracts.html`, 2026-08-28) -- fetches a real raw file on hover/focus, first 14 lines, cached. Pretty-print (`.github`'s `bin/render-review.py`, `get_pretty_html()`) and EXIF-signed-image display are real and live on `view.lab.tcos.us/contracts.html` but not yet ported anywhere else -- open work, not declined work.

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
