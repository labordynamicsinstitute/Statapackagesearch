"""Semantic-version arithmetic for packagesearch releases.

Adapted from https://github.com/ssc-ng/ssc2 (tools/version.py), without
release candidates.

Everything here except git_tags() is pure, so the release logic can be
unit-tested without a repository.

Convention: version strings never carry a leading "v"; tag strings always
do. The base for the next release is the VERSION file, not the tag list:
the repository's legacy tags (1.0.16, 1.0.20, 1.1.0) predate the vN.N.N
rule and are ignored.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Iterable, NamedTuple, Optional

_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


class Version(NamedTuple):
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


def parse(text: str) -> Optional[Version]:
    """Parse "1.1.1". Returns None -- never raises -- for anything else."""
    m = _RE.match(text.strip())
    if m is None:
        return None
    return Version(*(int(g) for g in m.groups()))


def parse_tag(text: str) -> Optional[Version]:
    """Parse a git tag name; the leading "v" is mandatory."""
    return parse(text[1:]) if text.startswith("v") else None


def tag_of(v: Version) -> str:
    return f"v{v}"


def bump(v: Version, part: str) -> Version:
    if part == "major":
        return Version(v.major + 1, 0, 0)
    if part == "minor":
        return Version(v.major, v.minor + 1, 0)
    if part == "patch":
        return Version(v.major, v.minor, v.patch + 1)
    raise ValueError(f"bump part must be major, minor or patch; got {part!r}")


def next_version(current: str, part: str = "patch",
                 override: Optional[str] = None,
                 tags: Iterable[str] = ()) -> Version:
    """Decide the version for the release being cut.

    `current` is the content of the VERSION file. With an override, that
    version is used after validation; it may equal `current` (releasing
    what is already stamped, as for the first release) but not go below
    it. Otherwise `current` is bumped by `part`. Either way the result is
    refused if its vN.N.N tag already exists.
    """
    cur = parse(current)
    if override:
        target = parse(override)
        if target is None:
            raise ValueError(
                f"{override!r} is not a valid version: expected N.N.N "
                f"without a leading 'v'")
        if cur is not None and target < cur:
            raise ValueError(
                f"version {target} is lower than the current version {cur}")
    else:
        if cur is None:
            raise ValueError(
                f"VERSION holds {current.strip()!r}, which is not N.N.N; "
                f"pass an explicit version override")
        target = bump(cur, part)

    if tag_of(target) in set(tags):
        raise ValueError(f"tag {tag_of(target)} already exists")
    return target


def git_tags(repo: Path) -> list:
    """All tag names in `repo`. The one impure function in this module."""
    out = subprocess.run(
        ["git", "-C", str(repo), "tag", "--list"],
        check=True, capture_output=True, text=True).stdout
    return [line.strip() for line in out.splitlines() if line.strip()]
