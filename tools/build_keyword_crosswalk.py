#!/usr/bin/env python3
"""Build the keyword-to-package crosswalk from the .pkg files of an SSC snapshot.

The input is stata-pkg-files.zip from a date-stamped tag of
https://github.com/ssc-ng/archive; see auxiliary/README.md. The output is a CSV
with the columns of p_keyword_pkg_xwalk.dta (keyword, package, filename,
extension), which auxiliary/convert_keyword_crosswalk.do turns into that file.

Standard library only.
"""

import argparse
import collections
import csv
import posixpath
import re
import sys
import zipfile

# Only these files define something a do-file can name.
EXTENSIONS = ("ado", "scheme")
# A word the scan could ever see. Rules out, for example, "WIN64 fren.ado".
VALID_KEYWORD = re.compile(r"^[A-Za-z0-9_]{1,32}$")
FIELDS = ("keyword", "package", "filename", "extension")


def keyword_for(filename):
    """Return (keyword, extension) for a file name, or None if it has no keyword.

    _gfoo.ado provides the egen function foo, and scheme-foo.scheme the scheme foo.
    """
    stem, _, extension = filename.rpartition(".")
    extension = extension.lower()
    if not stem or extension not in EXTENSIONS:
        return None
    if extension == "ado" and stem.startswith("_g") and len(stem) > 2:
        stem = stem[2:]
    if extension == "scheme" and stem.startswith("scheme-"):
        stem = stem[len("scheme-"):]
    if not VALID_KEYWORD.match(stem):
        return None
    return stem, extension


def files_in_pkg(text):
    """Return the base names on the f and F lines of a .pkg file."""
    names = []
    for line in text.splitlines():
        line = line.strip()
        if len(line) > 2 and line[0] in "fF" and line[1].isspace():
            names.append(posixpath.basename(line[2:].strip().replace("\\", "/")))
    return names


def read_candidates(zip_path):
    """Return every (keyword, package, filename, extension) in the archive."""
    candidates = set()
    with zipfile.ZipFile(zip_path) as archive:
        for name in archive.namelist():
            if not name.endswith(".pkg"):
                continue
            package = posixpath.basename(name)[: -len(".pkg")]
            # .pkg files have no declared encoding; the f lines are ASCII in practice
            text = archive.read(name).decode("latin-1")
            for filename in files_in_pkg(text):
                found = keyword_for(filename)
                if found:
                    keyword, extension = found
                    candidates.add((keyword, package, filename, extension))
    return candidates


def select(candidates):
    """Keep one row per keyword, because packagesearch merges 1:1 on keyword.

    A keyword can come from several packages. In order, prefer an .ado file over a
    scheme, the package named after the keyword, and then the first package
    alphabetically, so that the result does not depend on the order of the input.
    """
    by_keyword = collections.defaultdict(list)
    for row in candidates:
        by_keyword[row[0]].append(row)

    def preference(row):
        keyword, package, filename, extension = row
        return (extension != "ado", package.lower() != keyword.lower(), package, filename)

    return [min(by_keyword[keyword], key=preference) for keyword in sorted(by_keyword)]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pkg_zip", help="stata-pkg-files.zip from a snapshot of ssc-ng/archive")
    parser.add_argument("output", help="CSV file to write")
    args = parser.parse_args(argv)

    candidates = read_candidates(args.pkg_zip)
    rows = select(candidates)
    with open(args.output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(FIELDS)
        writer.writerows(rows)

    shared = len(candidates) - len(rows)
    print(
        f"{len(rows)} keywords from {len({row[1] for row in rows})} packages; "
        f"{shared} candidate rows set aside because another package has the keyword",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
