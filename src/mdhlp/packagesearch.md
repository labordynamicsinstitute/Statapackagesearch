# Title

__packagesearch__ - Module to search Stata code for the SSC packages used by the code

# Syntax

__packagesearch__ , __**codedir**(_directorytoscan_)__ [__details__] [__**domain**(_domain_)__] [__**file**save__] [__**excel**save__] [__**nodrop**falsepos__] [__**install**founds__]

| _options_ | Description |
|-----------|-------------|
| __**codedir**(_directorytoscan_)__ | Required. Directory that contains the `.do` files to be scanned for SSC packages. |
| __details__ | Preserve the list of keywords that triggered the package match. By default, only the count of such keywords is output. |
| __**domain**(_domain_)__ | Optionally specifies a domain from which to take statistics to help identify likely packages (by default, _ssc hot_ is used). Only available domain right now is _econ_. |
| __**file**save__ | Outputs a list of all files that were parsed during the scanning process. |
| __**excel**save__ | Saves the results of the scan into an Excel spreadsheet titled `candidatepackages.xlsx`. This file is saved in the specified _directorytoscan_ and will include a list of parsed programs if __filesave__ is also indicated as an option. |
| __**nodrop**falsepos__ | By default, command removes packages that were frequently found to be false positives during beta testing. This flag disables that feature. Presently this includes the following packages: _white, missing, index, dash, title, cluster, pre, bys_. |
| __**install**founds__ | Installs all SSC packages found during the scanning process into the current working directory. |

# Description

__packagesearch__ provides a tool that scans, parses, and matches all Stata `.do` files in a directory (and its subdirectories) against a list of all packages currently hosted at SSC. It outputs a list of candidate SSC packages that were (likely) used when code is run.

# Options

__**codedir**(_directorytoscan_)__ is required. It specifies the directory that contains the `.do` files to be scanned for SSC packages.

__details__ will preserve the list of keywords that triggered the package match. By default, only the count of such keywords is output.

__**domain**(_domain_)__ optionally specifies a domain from which to take statistics to help identify likely packages (by default, _ssc hot_ is used). Only available domain right now is _econ_.

__**file**save__ outputs a list of all files that were parsed during the scanning process.

__**excel**save__ saves the results of the scan into an Excel spreadsheet titled `candidatepackages.xlsx`. This file is saved in the specified _directorytoscan_ and will include a list of parsed programs if __filesave__ is also indicated as an option.

__**nodrop**falsepos__ by default, command removes packages that were frequently found to be false positives during beta testing. This flag disables that feature. Presently this includes the following packages: _white, missing, index, dash, title, cluster, pre, bys_.

__**install**founds__ installs all SSC packages found during the scanning process into the current working directory.

# Examples

## Example 1

Scan a project directory for SSC packages:

```
packagesearch, codedir("C:/Users/username/myproject")
```

## Example 2

Scan a project directory and save the list of parsed files:

```
packagesearch, codedir("C:/Users/username/myproject") filesave
```

## Example 3

Scan a directory on Linux/Mac, save results to Excel, keep all matches (including common false positives), and install found packages:

```
packagesearch, codedir("/home/username/myproject") excelsave nodropfalsepos installfounds
```

# Authors

Lars Vilhuber, Cornell University
lars.vilhuber@cornell.edu

Lydia Reiner, independent researcher
lr397@cornell.edu
