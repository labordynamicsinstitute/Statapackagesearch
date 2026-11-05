/* This will test the packagesearch package */
/* A keyword stays in the crosswalk after its package has left SSC. Such a package is reported, as unlikely */
/* Note this will run the *local* version, not the to-be-installed version */

set linesize 120

include "test/install.do"
which packagesearch
di "====Test 6-1: BEGIN"
packagesearch, codedir(data/test6)
di "====Test 6-1: END"
di "====Test 6-2: BEGIN"
packagesearch, codedir(data/test6) domain(econ)
di "====Test 6-2: END"
di "====Test 6-3: BEGIN"
packagesearch, codedir(data/test6) installfounds
di "====Test 6-3: END"
exit, clear STATA
