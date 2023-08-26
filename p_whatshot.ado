program p_whatshot
*! version 1.0.16  26aug2023
    version 14
    syntax , vars(string) [  debug ]

        local p_vars_hot `vars'
    	// Collect top hits at SSC for the past month 
		// We directly use the file that is used by the "ssc whatshot" command, Suggestion by Sergio Correia
    	local whatshotsrc "http://repec.org/docs/sschotPPPcur.dta"

    	use package author hits_cur using "`whatshotsrc'"
		// legacy consistency
    	rename package packagename
		rename author authors
		rename hits_cur hits
		gen rank = _n

		keep packagename `p_vars_hot'
end
