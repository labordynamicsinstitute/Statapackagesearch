#!/usr/bin/env python3
"""Set the packagesearch version, or check that it is consistent.

The release workflow (.github/workflows/release.yml) runs this; you
normally should not. Do not commit its output by hand -- see AGENTS.md.

Usage:
    python3 tools/set_version.py --check              # drift check
    python3 tools/set_version.py                      # bump patch, today
    python3 tools/set_version.py --bump minor
    python3 tools/set_version.py --version 1.1.1 --date 2026-10-09

When $GITHUB_OUTPUT is set, writes `version=` and `tag=` lines to it so
the calling GitHub Actions job can consume them.
"""
from __future__ import annotations

import argparse
import datetime
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.stamp import VERSION_FILE, check, stamp  # noqa: E402
from tools.version import git_tags, next_version, tag_of  # noqa: E402


def _emit_outputs(version: str, tag: str) -> None:
    target = os.environ.get("GITHUB_OUTPUT")
    if not target:
        return
    with open(target, "a", encoding="utf-8") as fh:
        fh.write(f"version={version}\n")
        fh.write(f"tag={tag}\n")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repo", default=".", type=Path,
                   help="repository root (default: current directory)")
    p.add_argument("--check", action="store_true",
                   help="only verify that every stamped file agrees with VERSION")
    p.add_argument("--bump", default="patch",
                   choices=["patch", "minor", "major"],
                   help="which part to increment when --version is absent")
    p.add_argument("--version", default=None,
                   help="explicit version without a leading v, e.g. 1.1.1")
    p.add_argument("--date", default=None,
                   help="release date as YYYY-MM-DD (default: today, UTC)")
    args = p.parse_args(argv)

    if args.check:
        problems = check(args.repo)
        for problem in problems:
            print(f"error: {problem}", file=sys.stderr)
        if problems:
            print("Version strings are out of sync. Do not fix them by hand; "
                  "see AGENTS.md.", file=sys.stderr)
            return 1
        current = (args.repo / VERSION_FILE).read_text(encoding="utf-8").strip()
        print(f"ok: every stamped file says {current}")
        return 0

    when = (datetime.date.fromisoformat(args.date) if args.date
            else datetime.datetime.now(datetime.timezone.utc).date())
    current = (args.repo / VERSION_FILE).read_text(encoding="utf-8")
    try:
        version = next_version(current, part=args.bump,
                               override=args.version,
                               tags=git_tags(args.repo))
        stamp(args.repo, str(version), when)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as exc:
        print(f"error: could not list git tags in {args.repo}: "
              f"{exc.stderr.strip()}", file=sys.stderr)
        return 1

    tag = tag_of(version)
    print(f"set version {version} ({tag}), dated {when.isoformat()}")
    _emit_outputs(str(version), tag)
    return 0


if __name__ == "__main__":
    sys.exit(main())
