[![Test CI Stata](https://github.com/labordynamicsinstitute/Statapackagesearch/actions/workflows/test.yml/badge.svg)](https://github.com/labordynamicsinstitute/Statapackagesearch/actions/workflows/test.yml)
[![Latest release](https://img.shields.io/github/v/release/labordynamicsinstitute/Statapackagesearch)](https://github.com/labordynamicsinstitute/Statapackagesearch/releases/latest)

# `Packagesearch`: module to scan Stata .do files and identify SSC packages used by the code

## Installation
To install, type the following command into Stata. 

```
net install packagesearch, from("https://labordynamicsinstitute.github.io/Statapackagesearch/")
```

To install a specific release instead, put its tag (listed under [Releases](https://github.com/labordynamicsinstitute/Statapackagesearch/releases)) into the URL. For example, for `v1.1.3`:

```
net install packagesearch, replace from("https://raw.githubusercontent.com/labordynamicsinstitute/Statapackagesearch/v1.1.3/")
```

Releases from `v1.1.2` on are tagged `vX.Y.Z`. Older releases have no `v` in their tags: `1.1.0`, `1.0.20` and `1.0.16`. `replace` overwrites whatever version is currently installed.

`which packagesearch` shows the installed version.

## Syntax: (also available in the help file)

```{stata}

      help packagesearch                                              (SJX-X: dmXXXX)
      -------------------------------------------------------------------------------
      
      Title
      
          packagesearch -- Module to search Stata code for the SSC packages used by
              the code
      
      Description
      
          packagesearch provides a tool that scans, parses, and matches all Stata
          .do files in a directory (and its subdirectories) against a list of all
          packages currently hosted at SSC. It outputs a list of candidate SSC
          packages that were (likely) used when code is run.
      
      Syntax
      
              packagesearch , codedir(directorytoscan)[ details domain(domain) filesave
                      excelsave nodropfalsepos installfounds]
      
      
      Options
      
          codedir(directorytoscan) is required. It specifies the directory that
              contains the .do files to be scanned for SSC packages.
          details will preserve the list of keywords that triggered the package match. 
              By default, only the count of such keywords is output.

          domain(domain) optionally specifies a domain from which to take
              statistics to help identify likely packages (by default, ssc hot is
              used). Only available domain right now is econ.
      
          filesave outputs a list of all files that were parsed during the scanning
              process.
      
          excelsave saves the results of the scan into an Excel spreadsheet titled
              candidatepackages.xlsx. This file is saved in the specified
              directorytoscan and will include a list of parsed programs if
              filesave is also indicated as an option.
      
          nodropfalsepos By default, command removes packages that were frequently
              found to be false positives during beta testing. This flag disables
              that feature. Presently this includes the following packages:  white,
              missing, index, dash, title, cluster, pre, bys
      
          installfounds installs all SSC packages found during the scanning process
              into the current working directory.
      
```




## Description:

The code begins by either collecting a list of all packages hosted at SSC using the `whatshot` command, or pulling a list of common SSC packages used in economics research (if option `domain(econ)` is specified).   
Next, it identifies all .do files in the specified `codedir` directory and subdirectories, then parses each .do file into individual words using the `txttool` command. 
Finally, it matches the individual words against the list of common Stata packages and outputs a list of candidate packages that were (likely) used when the Stata code was run.  

## Testing

The Github repository has a few files to test the package. To run, you can do the following:

```{bash}
GITURL=https://github.com/labordynamicsinstitute/Statapackagesearch/
git clone $GITURL
cd Statapackagesearch
```

and then, if you have Stata installed,

```{bash}
./test/run.sh
```

and if you don't, but have access to a Stata license (e.g. on [Github Codespaces with the proper setup](https://github.com/labordynamicsinstitute/codespaces-stata-skeleton))
    
```{bash}
echo "$STATA_LIC_BASE64" | base64 -d > stata.lic
docker run -it --rm \
   -v $(pwd)/stata.lic:/usr/local/stata/stata.lic \
   -v $(pwd):/project \
   -w /project \
   --entrypoint /bin/bash dataeditors/stata19_5-mp:2026-08-12 \
   ./test/run.sh
```

## Contributing and releases

The version number lives in `VERSION` and is stamped into the `.ado`, `.sthlp`, `.pkg`, `stata.toc` and `CITATION.cff` files by the release workflow. **Do not edit version numbers by hand**; state in your pull request whether the change warrants a major, minor or patch release. The rules are in [AGENTS.md](AGENTS.md), and the release process is in [docs/RELEASING.md](docs/RELEASING.md).

### Questions?

Contact:   
Lydia Reiner (lr397@cornell.edu)  
Lars Vilhuber (lars.vilhuber@cornell.edu)


