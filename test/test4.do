/* This will test the packagesearch package */
/* Punctuation next to a command must separate words, not glue them together */
/* Note this will run the *local* version, not the to-be-installed version */
/* expected output:

Test 4: unique, ivreg2, reghdfe, outreg2, winsor2, psmatch2, rdrobust and coefplot
        are found. center, cmp, tabout and sutex, which only appear as part of a
        word built from a macro or as a possessive, are not.

*/


include "test/install.do"
which packagesearch
packagesearch, codedir(data/test4)
di "====Test 4: END"
exit, clear STATA
