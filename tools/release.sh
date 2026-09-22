#!/usr/bin/env bash
# Cut a release: checks, DLL-free gates, annotated tag, GitHub release.
#
#   tools/release.sh v3.2.0 --notes docs/releases/release-v3.2.0.md
#   tools/release.sh v3.2.0 --dry-run        # print every step, change nothing
#
# Refuses on a dirty worktree, a tag that already exists locally or on origin, a
# branch behind origin/main, an unauthenticated gh, and a missing notes file.
# Runs `make lint` and `make test-docs` before tagging (the DLL-free half of the
# gate suite; CI runs the rest on the push) unless --skip-gates is given.
#
# Version scheme follows the history: v3.x.0 for a game-version corpus release,
# v0.x.0 for the tooling series. The notes file is required: release prose is not
# generated, it is reviewed.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

usage() { sed -n '2,13p' "$0"; }
die() { echo "release: $*" >&2; exit 2; }

VERSION=""; NOTES=""; DRY=0; GATES=1
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --notes) NOTES="${2:?--notes needs a file}"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    --skip-gates) GATES=0; shift ;;
    -*) die "unknown option: $1" ;;
    *) [[ -z "$VERSION" ]] || die "one version at a time"; VERSION="$1"; shift ;;
  esac
done
[[ -n "$VERSION" ]] || die "usage: release.sh <vX.Y.Z> [--notes FILE] [--dry-run] [--skip-gates]"
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
git rev-parse -q --verify "refs/tags/$VERSION" >/dev/null && die "tag $VERSION already exists"
if git ls-remote --exit-code --tags origin "refs/tags/$VERSION" >/dev/null 2>&1; then
  die "tag $VERSION already exists on origin"
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
  echo "would: git push origin main   # if ahead of origin"
  echo "would: git tag -a $VERSION -m \"$TITLE\""
  echo "would: git push origin $VERSION"
  echo "would: gh release create $VERSION --title \"$TITLE\" --notes-file $NOTES"
  echo "release: dry run, nothing changed"
  exit 0
fi

ahead="$(git rev-list --count origin/main..HEAD)"
if [[ "$ahead" -gt 0 ]]; then
  echo "release: pushing $ahead commit(s) to origin/main"
  git push origin main
fi
git tag -a "$VERSION" -m "$TITLE"
git push origin "$VERSION"
gh release create "$VERSION" --title "$TITLE" --notes-file "$NOTES"
echo "release: $VERSION published"
