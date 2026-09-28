#!/usr/bin/env python3
"""release.sh: the dry-run contract, the refusals, and --resume, without
touching the checkout.

The release script is the one tool that publishes; its checks are what keep a
release honest, so they are pinned here. Every case runs with `--dry-run`, or in
a throwaway git repository under the scratch tree, or fails before any write,
and the test asserts afterwards that no tag appeared.

Usage: python3 tools/tests/test_release_script.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

RELEASE = _common.TOOLS / "release.sh"

# A stub gh: `auth status` passes, `release view` reports a release only once
# `release create` has recorded one, and every call is logged so the test can
# count how often a step ran.
GH_STUB = """#!/usr/bin/env bash
printf '%s\\n' "$*" >> "$GH_LOG"
case "$1" in
  auth) exit 0 ;;
  release)
    case "$2" in
      view) [[ -f "$GH_MARKER" ]]; exit $? ;;
      create) : > "$GH_MARKER" ;;
    esac
    ;;
esac
exit 0
"""


def git(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def make_sandbox(tmp: Path) -> tuple[Path, Path, Path]:
    """A throwaway repo with an origin remote, release.sh in it, and a gh stub.

    The script resolves its own root from its own path, so copying it under
    `<tmp>/repo/tools/` is what makes it operate on the throwaway repository
    instead of the checkout this test runs from.
    """
    repo = tmp / "repo"
    (repo / "tools").mkdir(parents=True)
    copy = repo / "tools" / "release.sh"
    copy.write_text(RELEASE.read_text(encoding="utf-8"), encoding="utf-8")
    copy.chmod(0o755)
    git("init", "-q", "-b", "main", ".", cwd=repo)
    git("config", "user.email", "test@example.invalid", cwd=repo)
    git("config", "user.name", "test", cwd=repo)
    git("commit", "-q", "--allow-empty", "-m", "init", cwd=repo)
    git("init", "-q", "--bare", str(tmp / "origin.git"), cwd=tmp)
    git("remote", "add", "origin", str(tmp / "origin.git"), cwd=repo)
    git("push", "-q", "-u", "origin", "main", cwd=repo)
    stub_dir = tmp / "bin"
    stub_dir.mkdir()
    stub = stub_dir / "gh"
    stub.write_text(GH_STUB, encoding="utf-8")
    stub.chmod(0o755)
    notes = repo / "notes.md"
    notes.write_text("fixture notes\n", encoding="utf-8")
    # The script refuses a dirty tree, and untracked files are dirt: the
    # sandbox has to look like a release-ready checkout.
    git("add", "-A", cwd=repo)
    git("commit", "-q", "-m", "release.sh and notes", cwd=repo)
    return repo, stub_dir, notes


def run_in(repo: Path, stub_dir: Path, tmp: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ | {
        "PATH": f"{stub_dir}:{os.environ['PATH']}",
        "GH_LOG": str(tmp / "gh.log"),
        "GH_MARKER": str(tmp / "gh.marker"),
    }
    return subprocess.run(
        [str(repo / "tools" / "release.sh"), *args],
        cwd=repo,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
        env=env,
    )


def gh_calls(tmp: Path) -> list[str]:
    log = tmp / "gh.log"
    return log.read_text(encoding="utf-8").splitlines() if log.exists() else []


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(RELEASE), *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def tag_exists(name: str) -> bool:
    return (
        subprocess.run(
            ["git", "rev-parse", "-q", "--verify", f"refs/tags/{name}"],
            cwd=_common.REPO,
            capture_output=True,
        ).returncode
        == 0
    )


def main() -> None:
    help_run = run("--help")
    assert help_run.returncode == 0, help_run
    assert "--dry-run" in help_run.stdout, help_run.stdout

    assert run().returncode == 2
    assert run("1.2.3").returncode == 2
    assert "version must look like" in run("1.2.3").stderr
    assert run("v9.9.9", "--notes", "/nope/notes.md", "--dry-run").returncode == 2
    assert run("v9.9.9", "--bad-flag").returncode == 2

    with tempfile.TemporaryDirectory(prefix="release_", dir=_common.scratch_dir()) as dry_tmp:
        notes = Path(dry_tmp) / "notes.md"
        notes.write_text("fixture notes\n", encoding="utf-8")

        # --dry-run skips the dirty-tree check, so an existing tag is reached on
        # any worktree state (a test must not depend on the checkout being clean).
        existing = run("v3.2.0", "--notes", str(notes), "--dry-run")
        assert existing.returncode == 2, existing.stdout
        assert "already exists" in existing.stderr, existing.stderr

        dry = run("v9.9.9", "--notes", str(notes), "--dry-run")
        assert dry.returncode == 0, (dry.stdout, dry.stderr)
        for step in ("git tag -a v9.9.9", "gh release create v9.9.9", "dry run, nothing changed"):
            assert step in dry.stdout, (step, dry.stdout)
        assert not tag_exists("v9.9.9"), "a dry run created a tag"

        # A dry run must not consult gh at all: CI has gh installed but
        # unauthenticated, and a failing stub earlier on PATH proves the plan is
        # printed without asking it anything.
        stub_dir = Path(dry_tmp) / "bin"
        stub_dir.mkdir()
        stub = stub_dir / "gh"
        stub.write_text("#!/usr/bin/env bash\nexit 1\n", encoding="utf-8")
        stub.chmod(0o755)
        env = os.environ | {"PATH": f"{stub_dir}:{os.environ['PATH']}"}
        stubbed = subprocess.run(
            [str(RELEASE), "v9.9.8", "--notes", str(notes), "--dry-run"],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
            env=env,
        )
        assert stubbed.returncode == 0, (stubbed.stdout, stubbed.stderr)
        assert "gh release create v9.9.8" in stubbed.stdout, stubbed.stdout
        assert not tag_exists("v9.9.8"), "a dry run with a stub gh created a tag"

    with tempfile.TemporaryDirectory(
        prefix="release_resume_", dir=_common.scratch_dir()
    ) as resume_tmp:
        tmp = Path(resume_tmp)
        repo, stub_dir, notes = make_sandbox(tmp)
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout.strip()

        # Nothing tagged: --resume has nothing to continue, and a plain run
        # would be the first cut, not a resume.
        empty = run_in(
            repo, stub_dir, tmp, "v0.0.1", "--notes", str(notes), "--skip-gates", "--resume"
        )
        assert empty.returncode == 2, (empty.stdout, empty.stderr)
        assert "nothing to resume" in empty.stderr, empty.stderr
        assert gh_calls(tmp) == [], gh_calls(tmp)

        # A run that tagged and pushed but died before the GitHub release.
        git("tag", "-a", "v0.0.1", "-m", "v0.0.1", cwd=repo)
        git("push", "-q", "origin", "v0.0.1", cwd=repo)
        again = run_in(repo, stub_dir, tmp, "v0.0.1", "--notes", str(notes), "--skip-gates")
        assert again.returncode == 2, (again.stdout, again.stderr)
        assert "already exists" in again.stderr, again.stderr
        assert gh_calls(tmp) == [], gh_calls(tmp)

        resumed = run_in(
            repo, stub_dir, tmp, "v0.0.1", "--notes", str(notes), "--skip-gates", "--resume"
        )
        assert resumed.returncode == 0, (resumed.stdout, resumed.stderr)
        assert any("release create v0.0.1" in call for call in gh_calls(tmp)), gh_calls(tmp)
        after = subprocess.run(
            ["git", "rev-parse", "v0.0.1^{commit}"],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout.strip()
        assert after == head, "the resume re-tagged"

        # Second resume: the release exists, so gh is not asked to create it
        # again. Two runs leave the same state as one.
        (tmp / "gh.log").unlink()
        twice = run_in(
            repo, stub_dir, tmp, "v0.0.1", "--notes", str(notes), "--skip-gates", "--resume"
        )
        assert twice.returncode == 0, (twice.stdout, twice.stderr)
        assert not any("release create" in call for call in gh_calls(tmp)), gh_calls(tmp)
        assert "already has a GitHub release" in twice.stdout, twice.stdout

        # A tag on another commit is not this release; resuming it would
        # publish the wrong tree under a live version.
        git("commit", "-q", "--allow-empty", "-m", "later", cwd=repo)
        drifted = run_in(
            repo, stub_dir, tmp, "v0.0.1", "--notes", str(notes), "--skip-gates", "--resume"
        )
        assert drifted.returncode == 2, (drifted.stdout, drifted.stderr)
        assert "not HEAD" in drifted.stderr, drifted.stderr

    print(
        "OK: release.sh refuses bad input and existing tags, its dry run writes "
        "nothing, and --resume finishes a half-cut release without repeating it"
    )


if __name__ == "__main__":
    main()
