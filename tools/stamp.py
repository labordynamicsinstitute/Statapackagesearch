"""Write the release version and date into every file that carries them.

VERSION is the single source of truth. Every other copy is a literal
value on an existing line, rewritten by field substitution, so main stays
installable at all times (GitHub Pages serves it directly).

To version a new file, add it to TARGETS. check() fails for any
root-level .ado or .sthlp file that is missing from TARGETS.
"""
from __future__ import annotations

import datetime
import re
from pathlib import Path
from typing import NamedTuple, Optional

from tools.version import parse

VERSION_FILE = "VERSION"

_MONTHS = ["jan", "feb", "mar", "apr", "may", "jun",
           "jul", "aug", "sep", "oct", "nov", "dec"]


def stata_date(when: datetime.date) -> str:
    """Stata %td style, in English regardless of locale: 09oct2026."""
    return f"{when.day:02d}{_MONTHS[when.month - 1]}{when.year}"


def _parse_stata_date(text: str) -> datetime.date:
    m = re.fullmatch(r"(\d{2})([a-z]{3})(\d{4})", text)
    if m is None or m.group(2) not in _MONTHS:
        raise ValueError(text)
    return datetime.date(int(m.group(3)), _MONTHS.index(m.group(2)) + 1,
                         int(m.group(1)))


def _parse_compact(text: str) -> datetime.date:
    return datetime.datetime.strptime(text, "%Y%m%d").date()


_parse_iso = datetime.date.fromisoformat


class Field(NamedTuple):
    """One stamped line.

    `pattern` must match exactly one line. Its named group `v` captures the
    version and `d` the date, when present. `template` is formatted with
    version, stata, iso and compact. `parse_date` reads group `d` back.
    """
    pattern: str
    template: str
    parse_date: Optional[callable] = None


_ADO = Field(r"^\*! version (?P<v>\S+)[ \t]+(?P<d>\S+)[ \t]*$",
             "*! version {version}  {stata}", _parse_stata_date)

TARGETS = {
    VERSION_FILE: [
        Field(r"\A(?P<v>.*)\n?\Z", "{version}\n"),
    ],
    "packagesearch.ado": [_ADO],
    "p_whatshot.ado": [_ADO],
    "packagesearch.sthlp": [
        Field(r"^\{\* \*! version (?P<v>\S+)[ \t]+(?P<d>[^\s}]+)\}\{\.\.\.\}$",
              "{{* *! version {version}  {stata}}}{{...}}", _parse_stata_date),
    ],
    "packagesearch.pkg": [
        Field(r"^d Version: (?P<v>\S+)$", "d Version: {version}"),
        Field(r"^d Distribution-Date: (?P<d>\S+)$",
              "d Distribution-Date: {compact}", _parse_compact),
    ],
    "stata.toc": [
        Field(r"^d Version (?P<v>\S+) \((?P<d>[^)]+)\)$",
              "d Version {version} ({iso})", _parse_iso),
    ],
    "CITATION.cff": [
        Field(r"^version: (?P<v>\S+)$", "version: {version}"),
        Field(r"^date-released: (?P<d>\S+)$",
              "date-released: {iso}", _parse_iso),
    ],
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def stamp(repo: Path, version: str, when: datetime.date) -> None:
    """Write `version` and `when` into every target under `repo`."""
    if parse(version) is None:
        raise ValueError(f"{version!r} is not a valid N.N.N version")
    values = dict(version=version, stata=stata_date(when),
                  iso=when.isoformat(), compact=when.strftime("%Y%m%d"))
    # Compute every new text before writing any, so a target whose header
    # has gone missing leaves the tree untouched.
    updated = {}
    for rel, fields in TARGETS.items():
        text = _read(repo / rel)
        for field in fields:
            line = field.template.format(**values)
            text, n = re.subn(field.pattern, lambda _: line, text,
                              flags=re.MULTILINE)
            if n != 1:
                raise ValueError(
                    f"{rel}: expected exactly one line matching "
                    f"{field.pattern!r}, found {n}")
        updated[rel] = text
    for rel, text in updated.items():
        (repo / rel).write_text(text, encoding="utf-8")


def check(repo: Path) -> list:
    """Every way the stamped files disagree with VERSION, as messages.

    An empty list means the tree is consistent.
    """
    problems = []
    current = _read(repo / VERSION_FILE).strip()
    if parse(current) is None:
        problems.append(f"{VERSION_FILE}: {current!r} is not N.N.N")

    dates = {}
    for rel, fields in TARGETS.items():
        if rel == VERSION_FILE:
            continue
        path = repo / rel
        if not path.exists():
            problems.append(f"{rel}: file is missing")
            continue
        text = _read(path)
        for field in fields:
            found = list(re.finditer(field.pattern, text, flags=re.MULTILINE))
            if len(found) != 1:
                problems.append(
                    f"{rel}: expected exactly one line matching "
                    f"{field.pattern!r}, found {len(found)}")
                continue
            groups = found[0].groupdict()
            if "v" in groups and groups["v"] != current:
                problems.append(
                    f"{rel}: version {groups['v']}, but {VERSION_FILE} "
                    f"says {current}")
            if "d" in groups:
                try:
                    dates[rel] = field.parse_date(groups["d"])
                except ValueError:
                    problems.append(
                        f"{rel}: cannot read the date {groups['d']!r}")

    if len(set(dates.values())) > 1:
        # Name the files that disagree with the most common date.
        common = max(set(dates.values()),
                     key=list(dates.values()).count)
        for rel, d in dates.items():
            if d != common:
                problems.append(
                    f"{rel}: release date {d}, but other files say {common}")

    for path in sorted(repo.glob("*.ado")) + sorted(repo.glob("*.sthlp")):
        if path.name not in TARGETS:
            problems.append(
                f"{path.name}: not versioned; add a version header and "
                f"register it in tools/stamp.py TARGETS")
    return problems
