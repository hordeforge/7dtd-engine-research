#!/usr/bin/env bash
# Cut a release: checks, DLL-free gates, annotated tag, GitHub release.
#
#   tools/release.sh v3.2.0 --notes docs/releases/release-v3.2.0.md
#   tools/release.sh v3.2.0 --dry-run        # print every step, change nothing
#   tools/release.sh v3.2.0 --resume         # finish a run that stopped halfway
#
# Refuses on a dirty worktree, a tag that already exists locally or on origin, a
# branch behind origin/main, an unauthenticated gh, and a missing notes file.
# Under --dry-run the worktree, behind-main and gh checks are notes, not
# refusals, since a dry run changes nothing.
# Runs `make lint` and `make test-docs` before tagging (the DLL-free half of the
# gate suite; CI runs the rest on the push) unless --skip-gates is given. A
# --dry-run skips them too, for the same reason.
#
# A release is several irreversible steps, and a run that dies between them
# (a push that lands and a gh that does not, a laptop lid closed on the tag
# push) leaves a half-published version. Re-running then dies on "tag already
# exists" and the version cannot be finished. --resume continues such a run: the
# tag must already exist and name HEAD, the steps it already completed are
# skipped, and the GitHub release is created only when it does not exist yet.
#
# Version scheme follows the history: v3.x.0 for a game-version corpus release,
# v0.x.0 for the tooling series (next tooling release: v0.4.0; v0.3.0 was tagged
# and deleted without a release). Full policy and tag history:
# docs/releases/release-contract.md. The notes file is required: release prose
# is not generated, it is reviewed.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

usage() { sed -n '2,/^[^#]/ { /^#/ { s/^#[[:space:]]\{0,1\}//; p; } }' "$0"; }
die() { echo "release: $*" >&2; exit 2; }

VERSION=""; NOTES=""; DRY=0; GATES=1; RESUME=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --notes) NOTES="${2:?--notes needs a file}"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    --skip-gates) GATES=0; shift ;;
    --resume) RESUME=1; shift ;;
    -*) die "unknown option: $1; try 'release.sh --help' for the supported arguments" ;;
    *) [[ -z "$VERSION" ]] || die "one version at a time"; VERSION="$1"; shift ;;
  esac
done
[[ -n "$VERSION" ]] || die "usage: release.sh <vX.Y.Z> [--notes FILE] [--dry-run] [--skip-gates] [--resume]"
[[ "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] || die "version must look like v3.2.0, got $VERSION"
[[ -n "$NOTES" ]] || NOTES="docs/releases/release-$VERSION.md"
[[ -f "$NOTES" ]] || die "notes file not found: $NOTES (write it, then re-run; --notes overrides)"
TITLE="7dtd-engine-research $VERSION - HordeForge Release"

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not a git worktree"
if [[ "$DRY" -eq 0 ]]; then
  [[ -z "$(git status --porcelain)" ]] || die "worktree is dirty; commit or stash first"
else
  [[ -z "$(git status --porcelain)" ]] || echo "release: note: worktree is dirty (fine for --dry-run)"
fi
# Where the tag already is, and what commit it names. A --resume run continues
# a version that was already tagged; a normal run refuses it, because a live tag
# is a published version (release-contract.md: never reuse one).
tag_local_commit="$(git rev-list -n1 "$VERSION" 2>/dev/null || true)"
tag_remote_commit="$(git ls-remote --tags origin "refs/tags/$VERSION^{}" 2>/dev/null | awk 'NR==1{print $1}')"
[[ -n "$tag_remote_commit" ]] ||
  tag_remote_commit="$(git ls-remote --tags origin "refs/tags/$VERSION" 2>/dev/null | awk 'NR==1{print $1}')"
head_commit="$(git rev-parse HEAD)"
if [[ "$RESUME" -eq 1 ]]; then
  resumed_commit="${tag_local_commit:-$tag_remote_commit}"
  [[ -n "$resumed_commit" ]] ||
    die "--resume needs tag $VERSION to exist locally or on origin; there is nothing to resume"
  [[ "$resumed_commit" == "$head_commit" ]] ||
    die "tag $VERSION names ${resumed_commit:0:12}, not HEAD (${head_commit:0:12}); cut the release at the tagged commit or use a new version"
else
  [[ -z "$tag_local_commit" ]] || die "tag $VERSION already exists"
  [[ -z "$tag_remote_commit" ]] || die "tag $VERSION already exists on origin"
fi
# gh is only needed to publish, so a dry run must not consult it: CI has gh
# installed but unauthenticated, and the plan is still worth printing there.
if [[ "$DRY" -eq 0 ]]; then
  command -v gh >/dev/null 2>&1 || die "gh not on PATH (needed for the GitHub release)"
  gh auth status >/dev/null 2>&1 || die "gh is not authenticated"
else
  command -v gh >/dev/null 2>&1 || echo "release: note: gh not on PATH (needed for the real run)"
fi

echo "release: $VERSION from $(git rev-parse --short HEAD), notes $NOTES"
if [[ "$DRY" -eq 0 ]]; then
  git fetch --quiet origin main
  behind="$(git rev-list --count HEAD..origin/main)"
  [[ "$behind" -eq 0 ]] || die "branch is $behind commit(s) behind origin/main; pull first"
fi

if [[ "$GATES" -eq 1 && "$DRY" -eq 0 ]]; then
  echo "release: make lint"
  make -s lint
  echo "release: make test-docs"
  make -s test-docs
fi

if [[ "$DRY" -eq 1 ]]; then
  if [[ "$RESUME" -eq 1 ]]; then
    [[ -n "$tag_local_commit" ]] || echo "would: (resume) tag $VERSION already on origin; fetch it locally to recreate the local ref"
    [[ -n "$tag_remote_commit" ]] || echo "would: (resume) push origin $VERSION   # the tag exists locally only"
  else
    echo "would: git tag -a $VERSION -m \"$TITLE\""
    echo "would: git push origin $VERSION"
  fi
  echo "would: git push origin main   # if ahead of origin"
  echo "would: gh release create $VERSION --title \"$TITLE\" --notes-file $NOTES   # unless it exists"
  echo "release: dry run, nothing changed"
  exit 0
fi

ahead="$(git rev-list --count origin/main..HEAD)"
if [[ "$ahead" -gt 0 ]]; then
  echo "release: pushing $ahead commit(s) to origin/main"
  git push origin main
fi
# Each step below is one that a killed run may already have completed, so each
# asks first. Tag and push are the recorded version; the release is what a
# half-finished run left out, and gh refuses to create it twice.
if [[ -z "$tag_local_commit" && -z "$tag_remote_commit" ]]; then
  echo "release: tagging $VERSION at HEAD"
  git tag -a "$VERSION" -m "$TITLE"
elif [[ -z "$tag_local_commit" ]]; then
  echo "release: tag $VERSION exists on origin only; leaving the local ref alone"
else
  echo "release: tag $VERSION already at HEAD (resume)"
fi
if [[ -z "$tag_remote_commit" ]]; then
  echo "release: pushing $VERSION to origin"
  git push origin "$VERSION"
fi
if gh release view "$VERSION" >/dev/null 2>&1; then
  echo "release: $VERSION already has a GitHub release; leaving it as it is"
else
  gh release create "$VERSION" --title "$TITLE" --notes-file "$NOTES"
fi
echo "release: $VERSION published"
