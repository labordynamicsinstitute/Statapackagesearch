/* Installability check: -net install packagesearch- from each source listed
   in install_check_sources.txt (a directory or a URL per line), each into
   its own empty PLUS directory. Writes one line per source to install_check_result.txt:
   "ok <source>" or "FAIL rc=<rc> <source>". Called by install_check.sh. */

adopath - PERSONAL
adopath - OLDPLACE
adopath - "."
adopath - SITE

local root "`c(pwd)'"
tempname in out
file open `in'  using "`root'/install_check_sources.txt", read text
file open `out' using "`root'/install_check_result.txt", write text replace

mkdir "`root'/install_check_plus", public
local i 0
file read `in' src
while r(eof) == 0 {
    local ++i
    local plus "`root'/install_check_plus/`i'"
    mkdir "`plus'", public
    sysdir set PLUS "`plus'"

    di as txt _n "=== `i': `src'"
    capture noisily {
        net install packagesearch, from("`src'") replace
        which packagesearch
        which p_whatshot
        findfile packagesearch.sthlp
        findfile p_stats_econ.dta
        findfile p_keyword_pkg_xwalk.dta
        findfile p_stopwords.txt
    }
    if _rc file write `out' "FAIL rc=`=_rc' `src'" _n
    else     file write `out' "ok `src'" _n
    file read `in' src
}
file close `in'
file close `out'
