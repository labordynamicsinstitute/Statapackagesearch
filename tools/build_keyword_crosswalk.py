#!/usr/bin/env python3
"""Build the keyword-to-package crosswalk from snapshots of the SSC archive.

A keyword stays in the crosswalk once it has been a keyword: a do-file may use a
command, or a whole package, that has since left SSC. So the input is many tags of
https://github.com/ssc-ng/archive, as downloaded by fetch_archive_snapshots.py; see
auxiliary/README.md. The output is a CSV with the columns of p_keyword_pkg_xwalk.dta
(keyword, package, filename, extension), which
auxiliary/convert_keyword_crosswalk.do turns into that file.

Standard library only.
"""

import argparse
import collections
import csv
import os
import posixpath
import re
import sys
import zipfile

# Where the archive itself starts, in the paths of the zip and of the file list.
ROOT = "fmwww.bc.edu/"
# Only these files define something a do-file can name.
EXTENSIONS = ("ado", "scheme")
# A word the scan could ever see. Rules out, for example, "WIN64 fren.ado".
VALID_KEYWORD = re.compile(r"^[A-Za-z0-9_]{1,32}$")
FIELDS = ("keyword", "package", "filename", "extension")
BEFORE_SNAPSHOTS = "0000-00-00"


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


def read_snapshot(zip_path, list_path):
    """Return the rows for every keyword in one snapshot, and the files it lacks.

    The rows are (keyword, package, filename, extension). A .pkg file can list a file
    that the snapshot does not have. That file could not be installed at the time, so
    it gives no keyword from this snapshot.
    """
    with open(list_path, encoding="latin-1") as handle:
        present = {line.strip() for line in handle}
    candidates = set()
    missing = set()
    with zipfile.ZipFile(zip_path) as archive:
        for name in archive.namelist():
            if not name.endswith(".pkg") or ROOT not in name:
                continue
            pkg_path = ROOT + name.split(ROOT, 1)[1]
            package = posixpath.basename(pkg_path)[: -len(".pkg")]
            # .pkg files have no declared encoding; the f lines are ASCII in practice
            for path in files_in_pkg(archive.read(name).decode("latin-1")):
                filename = posixpath.basename(path)
                found = keyword_for(filename)
                if not found:
                    continue
                if posixpath.normpath(posixpath.join(posixpath.dirname(pkg_path), path)) in present:
                    candidates.add((found[0], package, filename, found[1]))
                else:
                    missing.add((package, path))
    return candidates, missing


def read_snapshots(folder):
    """Combine the snapshots in a folder from fetch_archive_snapshots.py.

    Returns {row: tag of the latest snapshot with that row}, and the tags that were
    read, and the files that no snapshot had when a .pkg file listed them.
    """
    last_seen = {}
    missing = set()
    tags = []
    with open(os.path.join(folder, "manifest.tsv"), encoding="utf-8") as handle:
        manifest = [line.rstrip("\n").split("\t") for line in handle]
    # the latest tag first, so that the first tag to give a row is the latest with it
    for tag, zip_blob, list_blob in sorted(manifest, reverse=True):
        if not zip_blob or not list_blob:
            continue
        tags.append(tag)
        blobs = os.path.join(folder, "blobs")
        candidates, lacking = read_snapshot(os.path.join(blobs, zip_blob), os.path.join(blobs, list_blob))
        for row in candidates:
            last_seen.setdefault(row, tag)
        missing |= lacking
    found = {(row[1], row[2]) for row in last_seen}
    never = {item for item in missing if (item[0], posixpath.basename(item[1])) not in found}
    return last_seen, tags, never


def add_previous(last_seen, path):
    """Add the rows of an earlier crosswalk that the snapshots do not have.

    They are evidence of keywords from before the first snapshot, and count as older
    than any snapshot.
    """
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if VALID_KEYWORD.match(row["keyword"]):
                last_seen.setdefault(tuple(row[field] for field in FIELDS), BEFORE_SNAPSHOTS)


def select(last_seen):
    """Keep one row per keyword, because packagesearch merges 1:1 on keyword.

    A keyword can come from several packages. In order, prefer an .ado file over a
    scheme, the package named after the keyword, the package that had it most
    recently, and then the first package alphabetically, so that the result does not
    depend on the order of the input.
    """
    by_keyword = collections.defaultdict(list)
    for row in last_seen:
        by_keyword[row[0]].append(row)

    def preference(row):
        keyword, package, filename, extension = row
        recency = -int(last_seen[row].replace("-", ""))
        return (extension != "ado", package.lower() != keyword.lower(), recency, package, filename)

    return [min(by_keyword[keyword], key=preference) for keyword in sorted(by_keyword)]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("snapshots", help="folder written by fetch_archive_snapshots.py")
    parser.add_argument("output", help="CSV file to write")
    parser.add_argument("--previous", help="earlier crosswalk (CSV) whose keywords should stay")
    args = parser.parse_args(argv)

    last_seen, tags, never = read_snapshots(args.snapshots)
    if args.previous:
        add_previous(last_seen, args.previous)
    if not last_seen:
        parser.error(f"no packages found in {args.snapshots}")
    rows = select(last_seen)
    with open(args.output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(FIELDS)
        writer.writerows(rows)

    print(
        f"{len(tags)} snapshots, {tags[-1]} to {tags[0]}: "
        f"{len(rows)} keywords from {len({row[1] for row in rows})} packages; "
        f"{len(last_seen) - len(rows)} rows set aside because another package has the keyword; "
        f"{len(never)} listed files that no snapshot had:",
        file=sys.stderr,
    )
    for package, path in sorted(never):
        print(f"  {package}: {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
