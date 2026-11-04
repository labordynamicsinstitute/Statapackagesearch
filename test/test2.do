/* This will test the packagesearch package */
/* Note this will run the *local* version, not the to-be-installed version */
/* expected output: 

Test 2-1: data/test2/longwords_nounderscores.do is scanned; its 31-character
          word is dropped before txttool runs

          data/test2/comments_only.do has no code, which is not an error

Test 2-2: all files are scanned, so reghdfe and ivreg2 are both found

Test 2-3: every keyword fits in a w_<word> variable once cleaned the way the
          scan cleans a do-file, so dropping longer words loses no keyword

*/


include "test/install.do"
which packagesearch
packagesearch, codedir(data/test2) 
use p_keyword_pkg_xwalk.dta, clear
gen cleaned = ustrregexra(lower(keyword), "[^a-z0-9]", "")
qui count if ustrlen(cleaned) > 30
di "Test 2-3: keywords over 30 characters: " r(N)
exit, clear STATA
