/* This will test the packagesearch package */
/* Note this will run the *local* version, not the to-be-installed version */
/* expected output: 

Test 2-1: no "invalid name" error for data/test2/longwords_nounderscores.do,
          whose 31-character word is dropped before txttool runs

Test 2-2: both files are scanned, so both packages are found (in rank order)

  1. | reghdfe   
  2. |  ivreg2   

*/


include "test/install.do"
which packagesearch
packagesearch, codedir(data/test2) 
exit, clear STATA
