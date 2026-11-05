// Turn the CSV from tools/build_keyword_crosswalk.py into the crosswalk that
// packagesearch installs. Run from the repository root; see auxiliary/README.md.

version 14

import delimited using "auxiliary/keyword-package-crosswalk.csv", ///
	varnames(1) case(preserve) stringcols(_all) encoding("utf-8") clear

isid keyword
sort keyword
compress

// release 118, which Stata 14 (the package's minimum version) can read
saveold "p_keyword_pkg_xwalk.dta", version(14) replace
saveold "auxiliary/keyword-package-crosswalk.dta", version(14) replace
exit, clear STATA
