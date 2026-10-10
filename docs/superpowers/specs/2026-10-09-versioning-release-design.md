# Versioning and release process — design

Issue: #25. Template: https://github.com/ssc-ng/ssc2 (adapted, not copied).

## Goal

One version number, visible in the code, the help file and the package
metadata; a written rule telling programmers and AI agents how it changes;
a release workflow that applies the rule; and a check that fails when the
copies drift apart.

## Constraints

- `main` must stay installable. GitHub Pages serves `main` directly
  (legacy build) and is the documented install path:
  `net install packagesearch, from("https://labordynamicsinstitute.github.io/Statapackagesearch/")`.
  The Stata tests (`test/install.do`) install from the local checkout.
  This rules out ssc2's `@TOKEN@` placeholders and orphan `dist` branch.
- `main` is unprotected and Actions has write permission, so a workflow
  can commit and tag there.
- `sj/` is a frozen Stata Journal snapshot and is never touched.
- Python standard library only; no new dependencies.

## Decisions

| Question | Decision |
| --- | --- |
| Where the version lives | Literal values on `main`. `VERSION` (one line, `N.N.N`) is the single source of truth. |
| First version | `1.1.1` |
| Tag format | `vN.N.N`. The legacy bare tags (`1.0.16`, `1.0.20`, `1.1.0`) are left in place and ignored by the tooling. |
| Who changes the number | Only the release workflow (or `tools/set_version.py`). Never by hand. |
| Release candidates, floating `latest` tag, Zenodo | Out of scope. |

## Stamped locations

Each is rewritten by field substitution (regex on an existing line), so
every file stays valid and installable at all times.

| File | Line | Example |
| --- | --- | --- |
| `VERSION` | whole file | `1.1.1` |
| `packagesearch.ado` | `*! version` header | `*! version 1.1.1  09oct2026` |
| `p_whatshot.ado` | `*! version` header | `*! version 1.1.1  09oct2026` |
| `packagesearch.sthlp` | SMCL comment, line 2 | `{* *! version 1.1.1  09oct2026}{...}` |
| `packagesearch.pkg` | `d Version:` and `d Distribution-Date:` | `d Version: 1.1.1` / `d Distribution-Date: 20261009` |
| `stata.toc` | `d Version` | `d Version 1.1.1 (2026-10-09)` |
| `CITATION.cff` | `version:` and `date-released:` | `version: 1.1.1` / `date-released: 2026-10-09` |

Dates in `.ado`/`.sthlp` headers use Stata's `%td` style in English
(`09oct2026`), replacing the German `10mai2024` seen previously.

The README gets a GitHub "latest release" badge instead of a literal
version, so it never needs stamping.

## Components

- `tools/version.py` — pure semver arithmetic: `parse`, `parse_tag`
  (requires `v`), `bump`, `next_version(current, part, override, tags)`.
  The base for bumping is the `VERSION` file, not the tag list, because
  the legacy tags do not follow the new format.
- `tools/stamp.py` — `TARGETS`: a table of (file, regex, template).
  `stamp(repo, version, date)` rewrites them; `check(repo)` returns a
  list of human-readable problems: a target whose version or date
  disagrees, a target whose pattern no longer matches, or a root-level
  `*.ado`/`*.sthlp` file not listed in `TARGETS`.
- `tools/set_version.py` — CLI. `--bump patch|minor|major` or
  `--version N.N.N`, optional `--date YYYY-MM-DD` (default: today UTC),
  `--check`. Refuses a version whose tag already exists. Emits
  `version=` and `tag=` to `$GITHUB_OUTPUT` when set.
- `tools/tests/` — `unittest` suites for the three modules, plus a test
  that runs `check()` against the real repository (the drift check).

## Workflows

- `.github/workflows/version-check.yml` — on push and pull request:
  runs `python3 -m unittest discover -s tools/tests -t .`. No Stata
  license needed.
- `.github/workflows/release.yml` — manual dispatch, `main` only.
  Inputs: `bump` (patch/minor/major, default patch), `version`
  (optional override). Steps:
  1. checkout with full history; run the unit tests;
  2. `tools/set_version.py` (which refuses an existing tag);
  3. commit `release vX.Y.Z` as `github-actions[bot]` if anything
     changed, otherwise tag the current HEAD;
  4. annotated tag `vX.Y.Z`; push commit and tag in one `--atomic` push;
  5. `gh release create vX.Y.Z --generate-notes --latest`;
  6. request a GitHub Pages build so the Pages install path serves the
     new version.

The first run passes `version: 1.1.1`; later runs leave it blank.

## The rule

Documented in `AGENTS.md` (read by AI agents; `CLAUDE.md` points to it),
a "Contributing" section in the README, and `docs/RELEASING.md`:

1. Never hand-edit version strings or release dates in the stamped files.
2. Versions change only through the release workflow.
3. Bump meaning for this command: **major** — incompatible syntax or
   output change; **minor** — new option or capability; **patch** — bug
   fix, data/crosswalk refresh, documentation.
4. Every PR states the bump level it warrants.
5. A new root-level `.ado` or `.sthlp` file must carry a version header
   and be added to `tools/stamp.py`; the drift check enforces this.

## Known gaps

- A push made with `GITHUB_TOKEN` does not trigger `test.yml`, so the
  Stata tests do not run on the release commit. That commit only changes
  header comments and metadata.
- `test.yml` triggers only on pushes to `main`; it is not changed here.
