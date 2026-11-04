/* This will test the packagesearch package */
/* It should find keywords and packages whose raw names have underscores or capitals */
/* Note this will run the *local* version, not the to-be-installed version */
/* expected output:

Test 5-1: the scan cleans words to lower case without underscores, and the crosswalk
          is compared in the same form. Each candidate package appears once, with
          its count of distinct keywords. See data/test5/underscores.do for the cases.

Test 5-2: the details option lists each candidate package with its cleaned keywords,
          including the longest ones (30 and 29 characters).

*/

* the table with the longest keyword must not be wrapped
set linesize 120

include "test/install.do"
which packagesearch
di "====Test 5-1: BEGIN"
packagesearch, codedir(data/test5)
di "====Test 5-1: END"
di "====Test 5-2: BEGIN"
packagesearch, codedir(data/test5) details
di "====Test 5-2: END"

exit, clear STATA
