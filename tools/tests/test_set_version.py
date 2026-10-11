"""Unit tests for tools/set_version.py, and the drift check on this repo."""
import contextlib
import io
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.set_version import main
from tools.stamp import check
from tools.tests.test_stamp import make_repo

REPO_ROOT = Path(__file__).resolve().parents[2]

# Identity for throwaway test commits only, passed through the environment
# so no git configuration is written anywhere.
GIT_ENV = dict(os.environ,
               GIT_AUTHOR_NAME="test", GIT_AUTHOR_EMAIL="test@example.invalid",
               GIT_COMMITTER_NAME="test",
               GIT_COMMITTER_EMAIL="test@example.invalid")


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True,
                   capture_output=True, env=GIT_ENV)


def make_git_repo(tmp: Path, tags=()) -> Path:
    repo = make_repo(tmp)
    git(repo, "init", "-q")
    if tags:
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "fixture")
        for tag in tags:
            # Annotated and unsigned, whatever the user's git config says.
            git(repo, "-c", "tag.gpgSign=false", "tag", "-a", "-m", tag, tag)
    return repo


def run(*argv: str) -> tuple:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = main(list(argv))
    return rc, out.getvalue(), err.getvalue()


class TestThisRepository(unittest.TestCase):
    def test_stamped_files_agree_with_version_file(self):
        """The drift check. If this fails, do not hand-edit version
        strings: see AGENTS.md and docs/RELEASING.md."""
        self.assertEqual(check(REPO_ROOT), [])


class TestCLI(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        os.environ.pop("GITHUB_OUTPUT", None)

    def tearDown(self):
        os.environ.pop("GITHUB_OUTPUT", None)
        self._tmp.cleanup()

    def test_bump_patch_by_default(self):
        repo = make_git_repo(self.tmp)
        rc, out, _ = run("--repo", str(repo), "--date", "2026-05-10")
        self.assertEqual(rc, 0)
        self.assertEqual((repo / "VERSION").read_text(), "1.0.1\n")
        self.assertIn("v1.0.1", out)
        self.assertEqual(check(repo), [])

    def test_bump_minor(self):
        repo = make_git_repo(self.tmp)
        run("--repo", str(repo), "--bump", "minor", "--date", "2026-05-10")
        self.assertEqual((repo / "VERSION").read_text(), "1.1.0\n")

    def test_explicit_version_may_equal_current(self):
        repo = make_git_repo(self.tmp)
        rc, _, _ = run("--repo", str(repo), "--version", "1.0.0",
                       "--date", "2026-05-10")
        self.assertEqual(rc, 0)
        self.assertIn("2026-05-10", (repo / "stata.toc").read_text())

    def test_writes_github_outputs(self):
        repo = make_git_repo(self.tmp)
        gh_out = self.tmp / "gh_output"
        os.environ["GITHUB_OUTPUT"] = str(gh_out)
        run("--repo", str(repo), "--version", "2.0.0", "--date", "2026-05-10")
        written = gh_out.read_text()
        self.assertIn("version=2.0.0\n", written)
        self.assertIn("tag=v2.0.0\n", written)

    def test_refuses_existing_tag_and_leaves_files_alone(self):
        repo = make_git_repo(self.tmp, tags=["v1.0.1"])
        rc, _, err = run("--repo", str(repo), "--date", "2026-05-10")
        self.assertEqual(rc, 1)
        self.assertIn("v1.0.1 already exists", err)
        self.assertEqual((repo / "VERSION").read_text(), "1.0.0\n")

    def test_legacy_bare_tags_are_ignored(self):
        repo = make_git_repo(self.tmp, tags=["1.0.1"])
        rc, _, _ = run("--repo", str(repo), "--date", "2026-05-10")
        self.assertEqual(rc, 0)
        self.assertEqual((repo / "VERSION").read_text(), "1.0.1\n")

    def test_invalid_version_fails(self):
        repo = make_git_repo(self.tmp)
        rc, _, err = run("--repo", str(repo), "--version", "v2.0.0")
        self.assertEqual(rc, 1)
        self.assertIn("not a valid version", err)

    def test_outside_a_git_repository_fails_cleanly(self):
        repo = make_repo(self.tmp)   # no `git init`
        os.environ["GIT_CEILING_DIRECTORIES"] = str(self.tmp)
        try:
            rc, _, err = run("--repo", str(repo), "--date", "2026-05-10")
        finally:
            del os.environ["GIT_CEILING_DIRECTORIES"]
        self.assertEqual(rc, 1)
        self.assertIn("could not list git tags", err)
        self.assertEqual((repo / "VERSION").read_text(), "1.0.0\n")

    def test_check_passes_on_consistent_tree(self):
        repo = make_git_repo(self.tmp)
        run("--repo", str(repo), "--version", "1.0.0", "--date", "2026-05-10")
        rc, out, _ = run("--repo", str(repo), "--check")
        self.assertEqual(rc, 0)
        self.assertIn("1.0.0", out)

    def test_check_fails_on_drift(self):
        repo = make_git_repo(self.tmp)
        run("--repo", str(repo), "--version", "1.0.0", "--date", "2026-05-10")
        (repo / "VERSION").write_text("1.0.5\n")
        rc, _, err = run("--repo", str(repo), "--check")
        self.assertEqual(rc, 1)
        self.assertIn("packagesearch.ado", err)


if __name__ == "__main__":
    unittest.main()
