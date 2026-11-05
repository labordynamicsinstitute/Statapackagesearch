# Incorporating more detailed command names from packages

`p_keyword_pkg_xwalk.dta`, in the repository root, maps each keyword (what a do-file would name) to the package that provides it. `keyword-package-crosswalk.dta` in this directory is an identical copy, and `keyword-package-crosswalk.csv` is the same data in a form that shows up in a diff.

**A keyword stays once it has been a keyword**, because a do-file may use a command, or a whole package, that has since left SSC.

**Current version: 9,296 keywords from 4,114 packages**, from two sources:

- the last 700 date-stamped tags of [`ssc-ng/archive`](https://github.com/ssc-ng/archive), up to `2026-11-04`. `stata-pkg-files.zip` holds the `.pkg` files as of its tag only, and starts on `2025-03-21`, so 590 of those tags have one. `keyword-package-crosswalk-snapshots.tsv` lists the tags and the git blobs used.
- `keyword-package-crosswalk-original.csv`, the original list provided by Sergio Correia (the data file in the repository `ssc-ng/stata-keyword-crosswalk` is identical). It is the evidence for keywords from before those tags.

This is a static build. A full solution, covering all tags and updated regularly, is [issue 36](https://github.com/labordynamicsinstitute/Statapackagesearch/issues/36). `p_signalcommands.txt` and `convert_signalcommands.do` belong to that original list; the package does not use them, and they were not refreshed.

## How keywords are defined

- Each `f` or `F` line of each `.pkg` file names a file, relative to the `.pkg` file. Only `.ado` and `.scheme` files give a keyword, and only if `sscfiles.txt` of the same tag has the file: a package could not deliver a file the archive did not have. A file that was there in any one tag is enough. The build prints those that were never there.
- `.ado` files that no `.pkg` file lists give no keyword, because `ssc install` could not deliver them.
- `foo.ado` gives `foo`, `_gfoo.ado` gives the `egen` function `foo`, and `scheme-foo.scheme` gives the scheme `foo`.
- Names are stored as they are, with underscores and capitals. Names that are not made up of letters, digits and underscores, or are over 32 characters, are left out (for example `WIN64 fren.ado`).
- `packagesearch` needs one row per keyword. When several packages provide a keyword, the build prefers an `.ado` file over a scheme, then the package named after the keyword, then the package that had it most recently, then the first package alphabetically.
- Common words are not filtered. The results show how likely a match is to be a false positive, based on the popularity of the package. A package that is not on the SSC popularity list (because it has left SSC, say) has no rank and a `probFalsePos` of 1.

Test 2 fails if a keyword is over 30 characters once cleaned the way a do-file is cleaned, because `packagesearch` would drop that word from the scan.

## Updating

From the repository root, with the date of the snapshot to use:

```bash
python3 tools/fetch_archive_snapshots.py 700 /tmp/ssc-snapshots
python3 tools/build_keyword_crosswalk.py /tmp/ssc-snapshots auxiliary/keyword-package-crosswalk.csv \
  --previous auxiliary/keyword-package-crosswalk-original.csv
cp /tmp/ssc-snapshots/manifest.tsv auxiliary/keyword-package-crosswalk-snapshots.tsv
stata-mp -b do auxiliary/convert_keyword_crosswalk.do
test/run.sh
```

The download is about 1.9 GB (for 700 tags) and is not needed afterwards.

Then update the tags and the counts above. A refresh of the crosswalk is a **patch** release.

