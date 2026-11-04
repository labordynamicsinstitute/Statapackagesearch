/* This will test the packagesearch package */
/* Note this will run the *local* version, not the to-be-installed version */
/* expected output: 

Test 2-1: data/test2/longwords_nounderscores.do is scanned; its 31-character
          word is dropped before txttool runs

Test 2-2: both files are scanned, so reghdfe and ivreg2 are both found

*/


include "test/install.do"
which packagesearch
packagesearch, codedir(data/test2) 
exit, clear STATA
