#!/usr/bin/env python3
"""Download what build_keyword_crosswalk.py needs from the latest tags of ssc-ng/archive.

For each tag, without cloning it: stata-pkg-files.zip, which holds the .pkg files as
of that tag only (older tags do not have it), and sscfiles.txt, the files present at
that tag. Writes FOLDER/manifest.tsv (tag, git blob of the zip, git blob of the file
list; empty where a tag lacks the file) and FOLDER/blobs/. Running it again does not
download again what is already there. Needs the gh command.
"""

import argparse
import concurrent.futures
import json
import os
import re
import subprocess
import sys

REPO = "ssc-ng/archive"
DATED_TAG = re.compile(r"refs/tags/(\d{4}-\d{2}-\d{2})$")
ZIP_FILE = "stata-pkg-files.zip"
LIST_FILE = "sscfiles.txt"


def latest_tags(count):
    output = subprocess.run(
        ["git", "ls-remote", "--tags", f"https://github.com/{REPO}.git"],
        check=True, capture_output=True, text=True,
    ).stdout
    tags = {match.group(1) for match in map(DATED_TAG.search, output.splitlines()) if match}
    return sorted(tags, reverse=True)[:count]


def blobs_of(tag):
    output = subprocess.run(
        ["gh", "api", f"repos/{REPO}/git/trees/{tag}"],
        check=True, capture_output=True, text=True,
    ).stdout
    tree = {entry["path"]: entry["sha"] for entry in json.loads(output)["tree"]}
    return tag, tree.get(ZIP_FILE, ""), tree.get(LIST_FILE, "")


def download(blob, folder):
    path = os.path.join(folder, blob)
    if os.path.exists(path):
        return
    with open(path + ".part", "wb") as handle:
        subprocess.run(
            ["gh", "api", "-H", "Accept: application/vnd.github.raw", f"repos/{REPO}/git/blobs/{blob}"],
            check=True, stdout=handle, stderr=subprocess.PIPE,
        )
    os.replace(path + ".part", path)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("count", type=int, help="number of tags, starting from the latest")
    parser.add_argument("folder", help="folder to download into")
    args = parser.parse_args(argv)

    blobs = os.path.join(args.folder, "blobs")
    os.makedirs(blobs, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        rows = sorted(pool.map(blobs_of, latest_tags(args.count)), reverse=True)
        wanted = sorted({blob for row in rows for blob in row[1:] if blob})
        list(pool.map(lambda blob: download(blob, blobs), wanted))

    with open(os.path.join(args.folder, "manifest.tsv"), "w", encoding="utf-8") as handle:
        for row in rows:
            handle.write("\t".join(row) + "\n")
    print(f"{len(rows)} tags, {len(wanted)} files in {blobs}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
