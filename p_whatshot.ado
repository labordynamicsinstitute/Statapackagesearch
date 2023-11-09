program p_whatshot
*! version 1.0.20  09nov2023
    version 14
    syntax , vars(string) [  debug ]

        local p_vars_hot `vars'
    	// Collect top hits at SSC for the past month 
		// We directly use the file that is used by the "ssc whatshot" command, Suggestion by Sergio Correia
    	local whatshotsrc "http://repec.org/docs/sschotPPPcur.dta"

    	use package author hits_cur using "`whatshotsrc'"
		keep if _n <= 10000
		// legacy consistency
    	gen packagename = lower(package)
		rename author authors
		rename hits_cur hits
		// sort out duplicates. We keep the higher count
		gsort packagename -hits
		n di "Dropping duplicates pulled from SSC"
		duplicates drop packagename hits, force
		// rank by hits
		gsort  -hits
		gen rank = _n

		keep packagename `p_vars_hot'
end
