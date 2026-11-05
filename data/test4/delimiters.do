/* For testing of the package only */
/* Punctuation with no space around it must not glue words together. */

/* This one has spaces, and is found with or without the delimiters */
unique y

/* Should be found: a colon after a prefix command */
qui:ivreg2 y x
by id:reghdfe y x

/* Should be found: a semicolon between commands */
#delimit ;
outreg2;winsor2 y x;
#delimit cr

/* Should be found: a string or a weight right after the command name */
which"psmatch2"
which`"rdrobust"'
coefplot[aw=w]

/* Should NOT be found: names built from macros stay in one piece, as do */
/* possessives. These are center, cmp, tabout and sutex as part of a word. */
gen center`i' = 1
gen `v'cmp = 1
use tabout`i'.dta
di "the sutex's value"
