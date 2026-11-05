import os
import tempfile
import unittest
import zipfile

from tools.build_keyword_crosswalk import add_previous, files_in_pkg, keyword_for, read_snapshots, select


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
        self.assertEqual(files_in_pkg(text), ["../r/reghdfe.ado", "estfe.ado"])

    def test_windows_separator(self):
        self.assertEqual(files_in_pkg("f ..\\r\\reghdfe.ado\n"), ["../r/reghdfe.ado"])


class Select(unittest.TestCase):
    def pick(self, *rows):
        return select({row: "2026-01-01" for row in rows})

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

    def test_recent_package_beats_alphabetical(self):
        old, new = ("k", "abc", "k.ado", "ado"), ("k", "zed", "k.ado", "ado")
        self.assertEqual(select({old: "2025-01-01", new: "2026-01-01"})[0][1], "zed")

    def test_own_package_beats_recent(self):
        own, new = ("k", "k", "k.ado", "ado"), ("k", "zed", "k.ado", "ado")
        self.assertEqual(select({own: "2025-01-01", new: "2026-01-01"})[0][1], "k")


class AddPrevious(unittest.TestCase):
    def run_on(self, last_seen, text):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "previous.csv")
            with open(path, "w") as handle:
                handle.write("keyword,package,filename,extension\n" + text)
            add_previous(last_seen, path)
        return last_seen

    def test_a_keyword_from_before_the_snapshots_stays(self):
        rows = self.run_on({}, "old,oldpkg,old.ado,ado\n")
        self.assertEqual(select(rows), [("old", "oldpkg", "old.ado", "ado")])

    def test_counts_as_older_than_any_snapshot(self):
        now = ("k", "zed", "k.ado", "ado")
        rows = self.run_on({now: "2025-03-21"}, "k,abc,k.ado,ado\n")
        self.assertEqual(select(rows), [now])

    def test_a_row_also_in_a_snapshot_keeps_its_date(self):
        now = ("k", "k", "k.ado", "ado")
        rows = self.run_on({now: "2026-01-01"}, "k,k,k.ado,ado\n")
        self.assertEqual(rows, {now: "2026-01-01"})

    def test_names_that_cannot_be_a_word_are_dropped(self):
        self.assertEqual(self.run_on({}, "a-b,p,a-b.ado,ado\n"), {})


class ReadSnapshots(unittest.TestCase):
    ROOT = "fmwww.bc.edu/repec/bocode/"

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = folder.name
        os.mkdir(os.path.join(self.folder, "blobs"))
        self.manifest = []

    def add(self, tag, pkgs, files):
        """Add a snapshot. pkgs is {path: text}, or None if the tag has no zip."""
        zip_blob = ""
        if pkgs is not None:
            zip_blob = f"zip{tag}"
            with zipfile.ZipFile(os.path.join(self.folder, "blobs", zip_blob), "w") as archive:
                for path, text in pkgs.items():
                    archive.writestr("mirror/" + self.ROOT + path, text)
        list_blob = f"list{tag}"
        with open(os.path.join(self.folder, "blobs", list_blob), "w") as handle:
            handle.write("".join(self.ROOT + path + "\n" for path in files))
        self.manifest.append(f"{tag}\t{zip_blob}\t{list_blob}\n")

    def read(self):
        with open(os.path.join(self.folder, "manifest.tsv"), "w") as handle:
            handle.writelines(self.manifest)
        return read_snapshots(self.folder)

    def test_resolves_paths_relative_to_the_pkg_file(self):
        self.add("2026-01-01", {"r/reghdfe.pkg": "f reghdfe.ado\nf reghdfe.sthlp\nf ../e/estfe.ado\n"},
                 ["r/reghdfe.ado", "r/reghdfe.sthlp", "e/estfe.ado"])
        last_seen, tags, never = self.read()
        self.assertEqual(set(last_seen), {("reghdfe", "reghdfe", "reghdfe.ado", "ado"),
                                          ("estfe", "reghdfe", "estfe.ado", "ado")})
        self.assertEqual((tags, never), (["2026-01-01"], set()))

    def test_a_keyword_that_has_gone_stays(self):
        self.add("2026-01-01", {"a/a.pkg": "f a.ado\n"}, ["a/a.ado"])
        self.add("2025-01-01", {"a/a.pkg": "f a.ado\nf gone.ado\n", "b/b.pkg": "f b.ado\n"},
                 ["a/a.ado", "a/gone.ado", "b/b.ado"])
        last_seen = self.read()[0]
        self.assertEqual(last_seen[("a", "a", "a.ado", "ado")], "2026-01-01")
        self.assertEqual(last_seen[("gone", "a", "gone.ado", "ado")], "2025-01-01")
        self.assertEqual(last_seen[("b", "b", "b.ado", "ado")], "2025-01-01")

    def test_a_file_that_was_never_there_gives_no_keyword(self):
        self.add("2026-01-01", {"g/g.pkg": "f _grmax.ado\nf g.ado\n"}, ["g/g.ado"])
        last_seen, _, never = self.read()
        self.assertEqual(set(last_seen), {("g", "g", "g.ado", "ado")})
        self.assertEqual(never, {("g", "_grmax.ado")})

    def test_a_file_there_only_once_is_not_reported_as_never_there(self):
        self.add("2026-01-01", {"a/a.pkg": "f a.ado\n"}, [])
        self.add("2025-01-01", {"a/a.pkg": "f a.ado\n"}, ["a/a.ado"])
        last_seen, _, never = self.read()
        self.assertEqual(last_seen, {("a", "a", "a.ado", "ado"): "2025-01-01"})
        self.assertEqual(never, set())

    def test_a_file_in_another_folder_does_not_count(self):
        self.add("2026-01-01", {"s/s.pkg": "f ../a/basicstats.ado\n"}, ["b/basicstats.ado"])
        self.assertEqual(self.read()[0], {})

    def test_an_ado_file_in_no_package_gives_no_keyword(self):
        self.add("2026-01-01", {}, ["o/orphan.ado"])
        self.assertEqual(self.read()[0], {})

    def test_a_tag_without_the_zip_is_skipped(self):
        self.add("2026-01-01", {"a/a.pkg": "f a.ado\n"}, ["a/a.ado"])
        self.add("2025-01-01", None, ["z/z.ado"])
        last_seen, tags, _ = self.read()
        self.assertEqual(set(last_seen), {("a", "a", "a.ado", "ado")})
        self.assertEqual(tags, ["2026-01-01"])


if __name__ == "__main__":
    unittest.main()
