# Continuous integration (CI) for packagesearch

The workflow [`.github/workflows/test.yml`](../.github/workflows/test.yml) runs the tests in this directory ([`run.sh`](run.sh)) inside a Stata Docker image (`dataeditors/stata19_5-mp`). It runs:

- on every push to `main` and on every pull request,
- monthly (1st of the month, 06:17 UTC), to catch changes outside this repository (SSC packages, the SSC popularity list, an expired license),
- manually: `gh workflow run test.yml` (add `--ref <branch>` to test a branch).

After the tests, it runs [`install_check.sh`](install_check.sh), which checks that `net install packagesearch` works from
- a release archive built from the commit (`git archive`, which is what a GitHub release ships), and
- every `net install ... from("...")` URL in the main [README](../README.md) and [`docs/RELEASING.md`](../docs/RELEASING.md), so a documented install command that does not work (say, a tag that does not exist) fails the CI.

Each source installs into its own empty `PLUS` directory; the results are in `install_check_result.txt` and `install_check.log`.

## Required secret

The only secret needed is **`STATA_LIC_BASE64`**: the Stata license file `stata.lic`, base64-encoded. The license must be valid for the Stata version in the Docker image (`STATA_IMAGE` in `test.yml`).

For this repository it is an **organization secret** of `labordynamicsinstitute`, visible to all repositories in the organization. Nothing needs to be set at the repository level. A fork in another account or organization needs its own copy (see below).

## Renewing the license (yearly)

Stata licenses expire. **When the license expires, the CI fails**: the "Run Stata tests" step reports a license error, or all tests fail without producing results. The secret then has to be replaced with a renewed license:

1. Install the renewed license locally (run `stinit` on Linux; on macOS/Windows, Stata prompts for the new license). This updates your local `stata.lic`.
2. Find `stata.lic` in your Stata installation directory, for example:
   - Linux: `/usr/local/stata19/stata.lic` (or `/usr/local/statanow19/stata.lic`)
   - macOS: `/Applications/Stata/stata.lic` (or `/Applications/StataNow/stata.lic`)
   - Windows: `C:\Program Files\Stata19\stata.lic` (or `C:\Program Files\StataNow19\stata.lic`)
3. Encode it and update the secret, as shown below.
4. Re-run the workflow (`gh workflow run test.yml`) and check that it passes.

If the renewal also moves to a new Stata version, update `STATA_IMAGE` in `test.yml` (and the `docker run` example in the main [README](../README.md)) to a matching image from <https://hub.docker.com/u/dataeditors>.

### Base64-encoding the license file

Linux:

```bash
base64 -w0 /usr/local/stata19/stata.lic > stata.lic.b64
```

macOS (`base64` does not wrap lines by default):

```bash
base64 -i /Applications/Stata/stata.lic -o stata.lic.b64
```

Windows (PowerShell):

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\Program Files\Stata19\stata.lic")) | Out-File -NoNewline -Encoding ascii stata.lic.b64
```

To check the encoding, `base64 -d stata.lic.b64` should print the original license file.

### Updating the secret

With the [GitHub CLI](https://cli.github.com/), reading the value from the file so the license does not end up in your shell history:

```bash
# Organization secret, keeping it visible to all repositories (requires org admin)
gh secret set STATA_LIC_BASE64 --org labordynamicsinstitute --visibility all < stata.lic.b64

# Or: repository secret, e.g., for a fork
gh secret set STATA_LIC_BASE64 -R OWNER/Statapackagesearch < stata.lic.b64
```

Alternatively, paste the contents of `stata.lic.b64` into *Settings → Secrets and variables → Actions* (organization or repository).

Then delete the encoded copy: `rm stata.lic.b64`. Neither `stata.lic` nor its encoded version should be committed (both are in `.gitignore`).

## Running the tests locally

See the "Testing" section of the main [README](../README.md).
