# Releasing packagesearch

Releases are cut by the **release** workflow. Version strings are never
edited by hand (see `AGENTS.md`).

## How versions are stored

`VERSION` holds the current version (`N.N.N`). The release workflow
stamps it, with the release date, into the `.ado` and `.sthlp` headers,
`packagesearch.pkg`, `stata.toc` and `CITATION.cff`. These are literal
values on `main`, so `main` is always installable. That matters because
GitHub Pages serves `main`, and Pages is the documented install location.

`tools/set_version.py --check` (the drift check) fails if any stamped
file disagrees with `VERSION`, if the stamped dates disagree with one
another, or if a root-level `.ado`/`.sthlp` file has no registered
version header. The **Version check** workflow runs it on every push and
pull request.

## Tags

| Ref | Meaning |
| --- | --- |
| `vX.Y.Z` | A release: an annotated tag on the `release vX.Y.Z` commit on `main`. |
| `1.0.16`, `1.0.20`, `1.1.0` | Legacy tags from before this process. Left in place and ignored by the tooling. |

Any release can be installed by tag:

```stata
net install packagesearch, replace from("https://raw.githubusercontent.com/labordynamicsinstitute/Statapackagesearch/v1.1.3/")
```

## Cutting a release

1. Merge everything that should go out into `main`. Look at the merged
   pull requests to pick the bump level (each one states it; the meanings
   are in `AGENTS.md`). The highest level wins.
2. Go to **Actions → release → Run workflow** (on `main`).

   | Input | Meaning |
   |---|---|
   | `bump` | `patch` (default), `minor` or `major`. |
   | `version` | Leave **blank** normally. Set it only to override, e.g. `2.0.0`. No leading `v`. |

3. Run it. In order, the workflow:
   1. runs the unit tests and the drift check;
   2. stamps the new version and today's date (UTC);
   3. commits `release vX.Y.Z` to `main` and tags it, in one atomic push;
   4. creates the GitHub release with generated notes;
   5. asks GitHub Pages to rebuild.

Starting from `VERSION` = `1.1.1`:

| Inputs | Result |
| --- | --- |
| defaults | `v1.1.2` |
| `bump: minor` | `v1.2.0` |
| `bump: major` | `v2.0.0` |
| `version: 1.1.1` | `v1.1.1`. Allowed while no `v1.1.1` tag exists; releases what is already stamped, with a fresh date. |
| `version: 1.0.0` | refused: lower than `VERSION` |

### The first release

Run it **once** with `version` set to `1.1.1`: `VERSION` already says
`1.1.1`, but no `v1.1.1` tag exists yet. The generated release notes will
start from the previous GitHub release (`1.0.16`, 2022); edit them by hand
if that is too long.

## What a release archive contains

The "Source code" zip and tar.gz of a GitHub release (and what Zenodo
archives) hold only the files `net install` installs (the `f`/`F` lines of
`packagesearch.pkg`), plus `packagesearch.pkg`, `stata.toc`, `LICENSE`,
`CITATION.cff` and `README.md`. `.gitattributes` does this: it marks every
file `export-ignore` and re-includes those by name.
`tools/tests/test_archive.py` fails if that list and the `.pkg` disagree.
To see what the next release would contain:

```bash
git archive HEAD | tar -t
```

## Trying it locally

```bash
python3 tools/set_version.py --check                       # is everything consistent?
python3 tools/set_version.py --bump minor --date 2026-12-01  # see what a release would stamp
git diff
git restore VERSION *.ado *.sthlp *.pkg stata.toc CITATION.cff  # do not commit it
```

## Repository settings the workflow needs

- **Settings → Actions → General → Workflow permissions = Read and
  write.**
- `main` is not protected. If it ever is, allow `github-actions[bot]` to
  push to it, or the release commit will be refused (nothing is pushed in
  that case: the push is atomic).

## Caveats

- Pushes made with `GITHUB_TOKEN` do not trigger other workflows, so the
  Stata tests (`test.yml`) do not run on the release commit. That commit
  only changes header comments and metadata, and the tests ran on the
  commit before it.
- If the Pages rebuild request fails, the run shows a warning. Rebuild
  from **Settings → Pages** or push any commit to `main`.
- If a run pushed the tag but failed at the GitHub-release step, do not
  rerun it (it will refuse, since the tag exists). Finish it by hand:
  `gh release create vX.Y.Z --generate-notes --latest`.
- To redo a release, delete both the GitHub release and its tag. The
  `release vX.Y.Z` commit stays on `main`; rerun with `version: X.Y.Z`.
