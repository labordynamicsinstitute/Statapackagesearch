/* install from the local checkout (run from the repository root) */

adopath - PERSONAL
adopath - OLDPLACE
adopath - "."
net install packagesearch, from("`c(pwd)'") replace
which packagesearch
