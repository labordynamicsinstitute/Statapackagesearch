import os
import tempfile
import unittest
import zipfile

from tools.build_keyword_crosswalk import files_in_pkg, keyword_for, read_candidates, select


class KeywordFor(unittest.TestCase):
    def test_plain_ado(self):
        self.assertEqual(keyword_for("reghdfe.ado"), ("reghdfe", "ado"))

    def test_underscores_and_case_are_kept(self):
        self.assertEqual(keyword_for("Mst_iter.ado"), ("Mst_iter", "ado"))

    def test_egen_function(self):
        self.assertEqual(keyword_for("_grany.ado"), ("rany", "ado"))

    def test_other_leading_underscore_is_kept(self):
        self.assertEqual(keyword_for("_binom.ado"), ("_binom", "ado"))

    def test_scheme(self):
        self.assertEqual(keyword_for("scheme-538.scheme"), ("538", "scheme"))

    def test_other_extensions_have_no_keyword(self):
        for name in ("reghdfe.sthlp", "x.dta", "noextension"):
            self.assertIsNone(keyword_for(name))

    def test_names_that_cannot_be_a_word_are_dropped(self):
        for name in ("WIN64 fren.ado", "ad-cmd-command.ado", "a.do.ado", "a" * 33 + ".ado"):
            self.assertIsNone(keyword_for(name))


class FilesInPkg(unittest.TestCase):
    def test_reads_f_lines_only(self):
        text = "d foo.ado is described here\nf ../r/reghdfe.ado\nF estfe.ado\ne\n"
        self.assertEqual(files_in_pkg(text), ["reghdfe.ado", "estfe.ado"])

    def test_windows_separator(self):
        self.assertEqual(files_in_pkg("f ..\\r\\reghdfe.ado\n"), ["reghdfe.ado"])


class Select(unittest.TestCase):
    def pick(self, *rows):
        return select(set(rows))

    def test_one_row_per_keyword(self):
        rows = self.pick(("a", "p1", "a.ado", "ado"), ("b", "p1", "b.ado", "ado"))
        self.assertEqual([row[0] for row in rows], ["a", "b"])

    def test_own_package_beats_alphabetical(self):
        rows = self.pick(("strip", "strip", "strip.ado", "ado"), ("strip", "aaa", "strip.ado", "ado"))
        self.assertEqual(rows[0][1], "strip")

    def test_otherwise_first_alphabetically(self):
        rows = self.pick(("k", "zed", "k.ado", "ado"), ("k", "abc", "k.ado", "ado"))
        self.assertEqual(rows[0][1], "abc")

    def test_ado_beats_scheme(self):
        rows = self.pick(("k", "k", "scheme-k.scheme", "scheme"), ("k", "other", "k.ado", "ado"))
        self.assertEqual(rows[0][3], "ado")


class ReadCandidates(unittest.TestCase):
    def test_reads_a_snapshot_zip(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "pkg.zip")
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("mirror/fmwww.bc.edu/repec/bocode/r/reghdfe.pkg", "f reghdfe.ado\nf reghdfe.sthlp\n")
                archive.writestr("mirror/fmwww.bc.edu/repec/bocode/r/readme.txt", "f ignored.ado\n")
            self.assertEqual(read_candidates(path), {("reghdfe", "reghdfe", "reghdfe.ado", "ado")})


if __name__ == "__main__":
    unittest.main()
