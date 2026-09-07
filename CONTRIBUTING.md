# Contributing to Twin Cities Open Systems

This file applies to every public repository in the org that does not carry
its own. The mechanics are ordinary GitHub; what follows is the part you
cannot guess.

## Try it before you clone anything into your life

Most repos here run straight from a checkout. Nothing has to be installed,
and nothing in any repo runs an installer for you -- your dotfiles are
yours. The `human-execution-engine` quick start shows the pattern: a temp
directory, two environment exports, and `rm -rf` when you are done.

## Opening a pull request

1. Fork, branch, change, push, open the PR. Standard.
2. **Subject line in Conventional Commits form**: `type(scope): imperative
   description`, where type is one of `feat`, `fix`, `docs`, `chore`. The
   squash merge keeps your subject as the commit on `main`, so it is worth a
   moment.
3. Say what you measured, not what should be true. A PR body that shows the
   command you ran and what it printed gets merged faster than one that
   asserts the change works.

## What to expect after

**Review.** Every `main` requires one approving review, and the reviewer is
one person. Expect a response within a few days. If a week passes, comment
on the PR -- that is a nudge, not a nuisance.

**A red check is usually ours, not yours.** The checks compare the repo to
itself: stale generated indexes, a man page that did not get regenerated,
a reference that no longer resolves. If your change is small and a check
went red, read the log before assuming you broke it; ask if it is unclear.

**Some repos verify commit trailers.** A few carry a commit hook that
rejects commits without a `Model:` trailer. That rule is for the org's own
agents and should not fire on you; if it does, say so in the PR and it will
be fixed on our side.

## Questions

Open an issue and label it `question`. There is no chat channel you are
expected to find first.

## The shape of the org, in one paragraph

Records are typed YAML in git; claims are checked against measurement;
authority is a GPG signature over the file, not a status field. If a repo's
conventions seem strict, that is the reason -- and the strictness is aimed
at the org's own records drifting, not at you. Read the
`human-execution-engine` README's problem statement for the why.

## Sign-off

Contributions land under each repo's license, GPL-3.0 unless the repo says
otherwise. Whether the org asks for a Developer Certificate of Origin
`Signed-off-by:` line is not yet decided; until it is, none is required.
