# Incorporating more detailed command names from packages

`p_keyword_pkg_xwalk.dta`, in the repository root, maps each keyword (what a do-file would name) to the package that provides it. `keyword-package-crosswalk.dta` in this directory is an identical copy, and `keyword-package-crosswalk.csv` is the same data in a form that shows up in a diff.

**Current version: built from a shallow clone of the [`ssc-ng/archive`](https://github.com/ssc-ng/archive) tag `2026-11-04`** (commit `a44de01c3c7182844c0ba8ba2722cc740c5df552`): 9,114 keywords from 4,087 packages. It replaces the original list provided by Sergio Correia, whose data file is the same as the one in the repository `ssc-ng/stata-keyword-crosswalk`. `p_signalcommands.txt` and `convert_signalcommands.do` belong to that original list; the package does not use them, and they were not refreshed.

## How keywords are defined

- Each `f` or `F` line of each `.pkg` file names a file, relative to the `.pkg` file. Only `.ado` and `.scheme` files give a keyword, and only if the file is in the archive: a package cannot deliver a file the archive does not have. The build prints those it leaves out.
- `.ado` files that no `.pkg` file lists give no keyword, because `ssc install` cannot deliver them.
- `foo.ado` gives `foo`, `_gfoo.ado` gives the `egen` function `foo`, and `scheme-foo.scheme` gives the scheme `foo`.
- Names are stored as they are, with underscores and capitals. Names that are not made up of letters, digits and underscores, or are over 32 characters, are left out (for example `WIN64 fren.ado`).
- `packagesearch` needs one row per keyword. When several packages provide a keyword, the build prefers an `.ado` file over a scheme, then the package named after the keyword, then the first package alphabetically.

Test 2 fails if a keyword is over 30 characters once cleaned the way a do-file is cleaned, because `packagesearch` would drop that word from the scan.

## Updating

From the repository root, with the date of the snapshot to use:

```bash
TAG=2026-11-04
git clone --depth 1 --single-branch --branch "$TAG" https://github.com/ssc-ng/archive.git /tmp/ssc-archive
python3 tools/build_keyword_crosswalk.py /tmp/ssc-archive auxiliary/keyword-package-crosswalk.csv
stata-mp -b do auxiliary/convert_keyword_crosswalk.do
test/run.sh
```

The clone takes about 2 minutes and 2.6 GB of disk space, and is not needed afterwards.

Then update the snapshot and the counts above. A refresh of the crosswalk is a **patch** release.

