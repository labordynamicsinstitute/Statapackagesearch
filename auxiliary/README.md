# Incorporating more detailed command names from packages

`p_keyword_pkg_xwalk.dta`, in the repository root, maps each keyword (what a do-file would name) to the package that provides it. `keyword-package-crosswalk.dta` in this directory is an identical copy, and `keyword-package-crosswalk.csv` is the same data in a form that shows up in a diff.

**Current version: built from the [`ssc-ng/archive`](https://github.com/ssc-ng/archive) snapshot tagged `2026-11-04`** (`stata-pkg-files.zip`, git blob `1a393624dfc1feff6a6029a3e4f1911a436521fe`): 9,149 keywords from 4,098 packages. It replaces the original list provided by Sergio Correia. `p_signalcommands.txt` and `convert_signalcommands.do` belong to that original list; the package does not use them, and they were not refreshed.

## How keywords are defined

- Each `f` or `F` line of each `.pkg` file names a file. Only `.ado` and `.scheme` files give a keyword.
- `foo.ado` gives `foo`, `_gfoo.ado` gives the `egen` function `foo`, and `scheme-foo.scheme` gives the scheme `foo`.
- Names are stored as they are, with underscores and capitals. Names that are not made up of letters, digits and underscores, or are over 32 characters, are left out (for example `WIN64 fren.ado`).
- `packagesearch` needs one row per keyword. When several packages provide a keyword, the build prefers an `.ado` file over a scheme, then the package named after the keyword, then the first package alphabetically.

Test 2 fails if a keyword is over 30 characters once cleaned the way a do-file is cleaned, because `packagesearch` would drop that word from the scan.

## Updating

From the repository root, with the date of the snapshot to use:

```bash
TAG=2026-11-04
gh api -H "Accept: application/vnd.github.raw" \
  "repos/ssc-ng/archive/contents/stata-pkg-files.zip?ref=$TAG" > /tmp/stata-pkg-files.zip
python3 tools/build_keyword_crosswalk.py /tmp/stata-pkg-files.zip auxiliary/keyword-package-crosswalk.csv
stata-mp -b do auxiliary/convert_keyword_crosswalk.do
test/run.sh
```

Then update the snapshot and the counts above. A refresh of the crosswalk is a **patch** release.

