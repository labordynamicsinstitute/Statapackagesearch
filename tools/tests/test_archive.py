"""Release archives hold exactly the installed files plus their description.

.gitattributes marks everything export-ignore and re-includes a list by
name. This checks that list against the f/F lines of packagesearch.pkg, so
a file added to the package cannot be left out of the release archive (and
nothing else creeps in).
"""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Not installed, but shipped with every release.
EXTRAS = {"packagesearch.pkg", "stata.toc", "LICENSE", "CITATION.cff", "README.md"}


def installed_files() -> set[str]:
    pkg = (ROOT / "packagesearch.pkg").read_text(encoding="utf-8")
    return {line.split(None, 1)[1].strip()
            for line in pkg.splitlines()
            if line[:2] in ("f ", "F ")}


def git(*args: str, stdin: str = "") -> str:
    return subprocess.run(["git", *args], cwd=ROOT, input=stdin, text=True,
                          capture_output=True, check=True).stdout


@unittest.skipUnless(shutil.which("git") and (ROOT / ".git").exists(),
                     "needs a git checkout")
class ArchiveContents(unittest.TestCase):
    def test_archive_holds_installed_files_and_extras(self):
        tracked = git("ls-files")
        attrs = git("check-attr", "--stdin", "export-ignore", stdin=tracked)
        exported = {line.split(": ", 1)[0]
                    for line in attrs.splitlines()
                    if not line.endswith(": set")}
        self.assertEqual(exported, installed_files() | EXTRAS)


if __name__ == "__main__":
    unittest.main()
