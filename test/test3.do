/* This will test the packagesearch package */
/* It should identify the fact that multiple keywords from the same package should yield only one mention */
/* Note this will run the version from raw github, not the to-be-installed version */
/* expected output: 

Test 3-1:


*/


include "test/install.do"
which packagesearch
di "====Test 3-1: BEGIN"
packagesearch, codedir(data/test3) 
di "====Test 3-1: END"
di "====Test 3-2: BEGIN"
packagesearch, codedir(data/test3) details
di "====Test 3-2: END"

exit, clear STATA
