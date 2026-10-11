"""Unit tests for tools/stamp.py."""
import datetime
import tempfile
import unittest
from pathlib import Path

from tools.stamp import TARGETS, check, stamp, stata_date

WHEN = datetime.date(2026, 5, 10)

# A minimal stand-in for every stamped file, at an old version and date.
FIXTURE = {
    "VERSION": "1.0.0\n",
    "packagesearch.ado":
        "program packagesearch \n*! version 1.0.0  01jan2020\n    version 14\nend\n",
    "p_whatshot.ado":
        "program p_whatshot\n*! version 1.0.0  01jan2020\n    version 14\nend\n",
    "packagesearch.sthlp":
        "{smcl}\n{* *! version 1.0.0  01jan2020}{...}\n{cmd:help packagesearch}\n",
    "packagesearch.pkg":
        "v 3\nd Packagesearch: blurb\nd Version: 1.0.0\n"
        "d Distribution-Date: 20200101\nf packagesearch.ado\n",
    "stata.toc":
        "v 3\nd Version 1.0.0 (2020-01-01)\np packagesearch blurb\n",
    "CITATION.cff":
        "cff-version: 1.2.0\nversion: 1.0.0\ndate-released: 2020-01-01\n"
        "license: BSD-3-Clause\n",
}


def make_repo(tmp: Path) -> Path:
    for rel, text in FIXTURE.items():
        (tmp / rel).write_text(text, encoding="utf-8")
    return tmp


def read(repo: Path, rel: str) -> str:
    return (repo / rel).read_text(encoding="utf-8")


class TestStataDate(unittest.TestCase):
    def test_english_lowercase_zero_padded(self):
        self.assertEqual(stata_date(WHEN), "10may2026")
        self.assertEqual(stata_date(datetime.date(2026, 10, 9)), "09oct2026")


class TestFixtureCoversTargets(unittest.TestCase):
    def test_every_target_has_a_fixture(self):
        self.assertEqual(set(TARGETS), set(FIXTURE))


class TestStamp(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = make_repo(Path(self._tmp.name))
        stamp(self.repo, "1.2.3", WHEN)

    def tearDown(self):
        self._tmp.cleanup()

    def test_version_file(self):
        self.assertEqual(read(self.repo, "VERSION"), "1.2.3\n")

    def test_ado_headers(self):
        for rel in ("packagesearch.ado", "p_whatshot.ado"):
            with self.subTest(file=rel):
                self.assertIn("\n*! version 1.2.3  10may2026\n",
                              read(self.repo, rel))

    def test_sthlp_header(self):
        self.assertIn("\n{* *! version 1.2.3  10may2026}{...}\n",
                      read(self.repo, "packagesearch.sthlp"))

    def test_pkg(self):
        text = read(self.repo, "packagesearch.pkg")
        self.assertIn("\nd Version: 1.2.3\n", text)
        self.assertIn("\nd Distribution-Date: 20260510\n", text)

    def test_toc(self):
        self.assertIn("\nd Version 1.2.3 (2026-05-10)\n",
                      read(self.repo, "stata.toc"))

    def test_citation(self):
        text = read(self.repo, "CITATION.cff")
        self.assertIn("\nversion: 1.2.3\n", text)
        self.assertIn("\ndate-released: 2026-05-10\n", text)
        self.assertTrue(text.startswith("cff-version: 1.2.0\n"))

    def test_other_lines_untouched(self):
        self.assertEqual(read(self.repo, "packagesearch.ado"),
                         FIXTURE["packagesearch.ado"].replace(
                             "1.0.0  01jan2020", "1.2.3  10may2026"))

    def test_check_is_clean_after_stamp(self):
        self.assertEqual(check(self.repo), [])

    def test_stamp_is_idempotent(self):
        before = {rel: read(self.repo, rel) for rel in FIXTURE}
        stamp(self.repo, "1.2.3", WHEN)
        self.assertEqual({rel: read(self.repo, rel) for rel in FIXTURE},
                         before)


class TestStampErrors(unittest.TestCase):
    def test_missing_header_raises_and_names_the_file(self):
        with tempfile.TemporaryDirectory() as t:
            repo = make_repo(Path(t))
            (repo / "stata.toc").write_text("v 3\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "stata.toc"):
                stamp(repo, "1.2.3", WHEN)

    def test_rejects_invalid_version(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError):
                stamp(make_repo(Path(t)), "v1.2.3", WHEN)


class TestCheck(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = make_repo(Path(self._tmp.name))
        stamp(self.repo, "1.2.3", WHEN)

    def tearDown(self):
        self._tmp.cleanup()

    def _edit(self, rel, old, new):
        path = self.repo / rel
        path.write_text(read(self.repo, rel).replace(old, new),
                        encoding="utf-8")

    def test_reports_version_drift(self):
        self._edit("p_whatshot.ado", "1.2.3", "1.2.2")
        problems = check(self.repo)
        self.assertEqual(len(problems), 1)
        self.assertIn("p_whatshot.ado", problems[0])
        self.assertIn("1.2.2", problems[0])

    def test_reports_date_drift(self):
        self._edit("packagesearch.pkg", "20260510", "20260511")
        problems = check(self.repo)
        self.assertEqual(len(problems), 1)
        self.assertIn("packagesearch.pkg", problems[0])

    def test_reports_missing_header(self):
        self._edit("packagesearch.sthlp", "{* *! version 1.2.3  10may2026}{...}\n", "")
        problems = check(self.repo)
        self.assertEqual(len(problems), 1)
        self.assertIn("packagesearch.sthlp", problems[0])

    def test_reports_unparseable_date(self):
        self._edit("packagesearch.ado", "10may2026", "10mai2026")
        problems = check(self.repo)
        self.assertTrue(any("packagesearch.ado" in p for p in problems))

    def test_reports_bad_version_file(self):
        (self.repo / "VERSION").write_text("1.2\n", encoding="utf-8")
        self.assertTrue(any("VERSION" in p for p in check(self.repo)))

    def test_reports_unregistered_ado_and_sthlp(self):
        (self.repo / "p_newhelper.ado").write_text(
            "program p_newhelper\nend\n", encoding="utf-8")
        (self.repo / "p_newhelper.sthlp").write_text(
            "{smcl}\n", encoding="utf-8")
        problems = check(self.repo)
        self.assertEqual(len(problems), 2)
        self.assertTrue(all("tools/stamp.py" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
