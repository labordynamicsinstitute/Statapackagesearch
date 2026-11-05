/* This will test the packagesearch package */
/* A scan that finds nothing to report is not an error */
/* Note this will run the *local* version, not the to-be-installed version */

set linesize 120

include "test/install.do"
which packagesearch
local n 0
foreach dir in nomatch comments nodofiles falsepos {
	local ++n
	di "====Test 7-`n': BEGIN"
	cap noi packagesearch, codedir(data/test7/`dir')
	di "====Test 7-`n': rc=" _rc
	di "====Test 7-`n': END"
}
exit, clear STATA
