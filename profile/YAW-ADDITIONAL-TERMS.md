# YAW Additional Terms — DRAFT, not yet in force

**Status: draft for review. Not applied to any repository. Not legal advice —
this needs a lawyer's eye before it is relied on.**

This is the YAW layer: **GPL-3.0 plus additional terms under section 7**, not a
new license and not modified GPL text. Every repository stays GPL-3.0. A repo
that adopts this adds one file and one line to its `README`; nothing about the
GPL grant changes.

## Why it is built this way

The GPL's own terms permit copying its text and **not modifying it**. A
"GPL-ish" file edited to taste is neither the GPL nor enforceable as what it
claims to be. Section 7 exists precisely so a project can add house terms
without forking the license, and anything built this way stays GPL-compatible
and stays free software.

Section 7 is deliberately asymmetric, and the asymmetry decides what a YAW layer
can say:

- **Additional permissions** — anything that *relaxes* the license. Unbounded.
- **Additional restrictions** — only the closed list in §7(a)–(f).

Anything outside that list is a "further restriction" under §10: **void**, and
it would make the result non-free and GPL-incompatible. Every clause below cites
the subsection it stands on, so the conformance is checkable rather than
asserted.

## The terms

> The following additional terms apply to this work under section 7 of the GNU
> General Public License, version 3.
>
> **1. Attribution and notices. (§7(b))**
> You must preserve the copyright notices, this file, and the author
> attributions carried in the source and in any Appropriate Legal Notices the
> work displays.
>
> **2. Mark what you changed. (§7(c))**
> You may not misrepresent the origin of this material. If you modify it, you
> must mark your modified version in a reasonable way as different from the
> original — a changed name, a version suffix, a notice in the README, any of
> these will do. Say which claims are yours.
>
> **3. Names are not granted. (§7(e))**
> This license grants no rights in the trade names, trademarks or service marks
> of Twin Cities Open Systems (TCOS), LLC, including "TCOS", "YAW", "YAW!" and
> "Human Execution Engine", except as required for the attribution in term 1.
>
> **4. No implied endorsement. (§7(d))**
> You may not use the names of the licensors or authors for publicity, or in a
> way that states or implies they endorse your modified version.
>
> As section 7 provides, a recipient may remove these additional terms from any
> copy they convey, or from any part of it.

## What this deliberately does not say

The original ask (brain dump, 2026-09-11) was for a "you are wrong" license, and
asked to **fail fast if it turned out to be an impossible task**. Half of it is
impossible, and this is the fail-fast answer.

A clause restricting **who may use the software, or what they may use it for**
cannot be written here. Not by better drafting, not at greater length. It is a
further restriction under §10, so it is void where it appears, and attempting it
would make the work non-free and incompatible with the GPL it sits on — the
opposite of what a house license is for.

What survives is the half that was always the real point. "You are wrong" as a
*licensing* idea is not a ban on anyone; it is the insistence that claims stay
attached to whoever made them. Term 2 is that: change what you like, and mark it
as yours so nobody inherits credit or blame they did not earn. That is §7(c),
and it is enforceable.

## Adopting it

1. Keep `LICENSE` exactly as it is — verbatim GPL-3.0,
   `sha256 3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986`.
2. Add this file to the repo as `LICENSE-YAW.md`.
3. Add one line to the `README` license section: *"Licensed under GPL-3.0 with
   additional terms under section 7 — see `LICENSE` and `LICENSE-YAW.md`."*

## Open questions for the operator

- **Does this get adopted anywhere, or stay a draft?** Nothing needs it today;
  every repo is fine on plain GPL-3.0. Adding terms has a real cost — every
  downstream user has one more document to read.
- **Is "TCOS" the right legal name to assert in term 3?** `GLOSSARY.md` gives
  the entity as `Twin Cities Open Systems (TCOS), LLC`; a trademark claim should
  match whatever is actually registered, and nothing here checked that.
- **Does this want a lawyer before it goes anywhere near a public repo?** The
  §7 mapping is read straight from the license text and cited clause by clause,
  but "reads correctly to an engineer" is not the same standard as "holds up".
