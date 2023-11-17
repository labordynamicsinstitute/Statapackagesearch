// convert_signalcommands 

version 14

// convert_signalcommands from Sergio Correia

global infile "keyword-package-crosswalk.dta"
global outfile "p_signalcommands.txt"

use "$infile", clear
keep if extension == "ado"
keep keyword package 
rename keyword Signals
rename package Package

// save as txt file, no delimiters
outsheet using "$outfile", replace noquote