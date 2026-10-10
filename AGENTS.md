# Instructions for AI agents and contributors

## Version numbers — the rule

The version lives in one place: the `VERSION` file. Copies of it, with
the release date, are stamped into:

| File | Line |
| --- | --- |
| `packagesearch.ado`, `p_whatshot.ado` | `*! version 1.1.1  09oct2026` |
| `packagesearch.sthlp` | `{* *! version 1.1.1  09oct2026}{...}` |
| `packagesearch.pkg` | `d Version: 1.1.1` and `d Distribution-Date: 20261009` |
| `stata.toc` | `d Version 1.1.1 (2026-10-09)` |
| `CITATION.cff` | `version:` and `date-released:` |

1. **Never edit these version strings or dates by hand**, and never edit
   `VERSION` by hand. They change only when a release is cut, through the
   **release** workflow (Actions → release → Run workflow), which runs
   `tools/set_version.py`, commits, tags `vX.Y.Z` and publishes the
   GitHub release. See `docs/RELEASING.md`.
2. **State the bump level in every pull request** that changes what users
   get, so whoever cuts the release knows what to pick:
   - **major** — an incompatible change: an option removed or renamed,
     changed syntax, or a changed layout of the results users rely on.
   - **minor** — a new option or capability, backward compatible.
   - **patch** — a bug fix, a refresh of the bundled data
     (`p_*.dta`, `p_stopwords.txt`, the keyword crosswalk), or a
     documentation fix.
   - **none** — changes to tests, CI, tooling or the `sj/` manuscript only.
3. **A new root-level `.ado` or `.sthlp` file** must start with the same
   version header as its siblings (copy the current one) and be added to
   `TARGETS` in `tools/stamp.py`.
4. Before committing, run the checks; CI runs them on every push:

   ```bash
   python3 -m unittest discover -s tools/tests -t .
   python3 tools/set_version.py --check
   ```

   If the drift check fails, do not "fix" it by editing version strings:
   find out which change broke the stamped line and restore that line.

`sj/` is a frozen copy for the Stata Journal article. Never stamp or
update versions there.

## Testing the Stata code

`test/run.sh` runs the Stata test suite (needs a Stata license); see
`test/README-CI.md`.
