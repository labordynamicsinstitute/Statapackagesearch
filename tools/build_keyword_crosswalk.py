#!/usr/bin/env python3
"""Build the keyword-to-package crosswalk from a clone of the SSC archive.

The input is a shallow clone of a date-stamped tag of
https://github.com/ssc-ng/archive; see auxiliary/README.md. The output is a CSV
with the columns of p_keyword_pkg_xwalk.dta (keyword, package, filename,
extension), which auxiliary/convert_keyword_crosswalk.do turns into that file.

Standard library only.
"""

import argparse
import collections
import csv
import os
import posixpath
import re
import sys

# Where the packages are, within a clone of the archive.
PACKAGES = "fmwww.bc.edu/repec/bocode"
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
    """Return the paths on the f and F lines of a .pkg file, relative to that file."""
    paths = []
    for line in text.splitlines():
        line = line.strip()
        if len(line) > 2 and line[0] in "fF" and line[1].isspace():
            paths.append(line[2:].strip().replace("\\", "/"))
    return paths


def read_candidates(archive):
    """Return the rows for every keyword in a clone, and the listed files that are missing.

    The rows are (keyword, package, filename, extension). A .pkg file can list a file
    that the archive does not have. That file cannot be installed, so it gives no keyword.
    """
    candidates = set()
    missing = set()
    top = os.path.join(archive, *PACKAGES.split("/"))
    for folder, _, names in os.walk(top):
        for name in names:
            if not name.endswith(".pkg"):
                continue
            # .pkg files have no declared encoding; the f lines are ASCII in practice
            with open(os.path.join(folder, name), encoding="latin-1") as handle:
                text = handle.read()
            package = name[: -len(".pkg")]
            for path in files_in_pkg(text):
                filename = posixpath.basename(path)
                found = keyword_for(filename)
                if not found:
                    continue
                if os.path.isfile(os.path.join(folder, *path.split("/"))):
                    candidates.add((found[0], package, filename, found[1]))
                else:
                    missing.add((package, path))
    return candidates, missing


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
    parser.add_argument("archive", help="shallow clone of a snapshot of ssc-ng/archive")
    parser.add_argument("output", help="CSV file to write")
    args = parser.parse_args(argv)

    candidates, missing = read_candidates(args.archive)
    if not candidates:
        parser.error(f"no packages found under {args.archive}/{PACKAGES}")
    rows = select(candidates)
    with open(args.output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(FIELDS)
        writer.writerows(rows)

    shared = len(candidates) - len(rows)
    print(
        f"{len(rows)} keywords from {len({row[1] for row in rows})} packages; "
        f"{shared} candidate rows set aside because another package has the keyword; "
        f"{len(missing)} listed files are not in the archive:",
        file=sys.stderr,
    )
    for package, path in sorted(missing):
        print(f"  {package}: {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
