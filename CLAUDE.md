# .github (TCOS org meta-repo)

This repo administers the GitHub org itself -- issue templates, org-wide CI,
the fallback CODEOWNERS, the org profile page. That GitHub-coupling is
correct and expected *here*, unlike `human-execution-engine`, which is the
platform-independent doctrine root.

@profile/GLOSSARY.md
@~/git/human-execution-engine/prompts/PROMPTING_RULES.md

**The import above is real, required, and assumes a specific machine
layout: this org's own convention (`bin/init-org.sh`'s `WORKSPACE_DIR="${HOME}/git"`)
that every repo is checked out under `~/git/<repo>`.** `~` (not a hardcoded
username) is the most decoupled form Claude Code's `@import` actually
supports -- verified: tilde-expands, but does **not** expand `$HOME` or any
other env var, and there's no workspace-relative import mechanism. On any
machine that doesn't follow the `~/git/` layout, this import silently fails
to resolve and the rulebook below won't be in context -- if that ever
happens, read `human-execution-engine/prompts/PROMPTING_RULES.md` directly
instead of assuming it loaded.

For the full repo map, see `profile/ARCHITECTURE.md`. For one-time org/repo
bootstrap steps (branch rulesets, CODEOWNERS centralization, GitHub admin
gotchas), see `profile/ORG_SETUP.md` -- read on demand, not every session.
