#!/bin/bash

# Keep only the rows of the table of candidate packages and their package names,
# sorted (the rank column, and so the row order, follows SSC popularity)
normalize() {
   grep -E '^ +[0-9]+\. \|' | awk '{print $3}' | sort
}

if [[ -f test2.log ]]
then
   # Verify first test: a word too long for a variable name (31 characters, 33 with
   # the w_ prefix) is dropped, so txttool does not fail on the file
   grep -q "Processing file data/test2/longwords_nounderscores.do" test2.log || { echo "Not the expected output: Test 2-1 (file not processed)"; exit 2; }
   if grep -qE "invalid name|unable to be processed" test2.log
   then
      echo "Not the expected output: Test 2-1"
      exit 2
   fi
   echo "Success: Test 2-1"
   # Verify second test: both files are scanned, so both packages are found
   sed -n '/^Candidate packages listed below/,/^Programs parsed:/p' test2.log > actual_output2-2.txt
   diff <(normalize < actual_output2-2.txt) <(normalize < test/expected_output2-2.txt) || { echo "Not the expected output: Test 2-2"; exit 2; }
   echo "Success: Test 2-2"
   exit 0 
else
   echo "Something went wrong with running Stata"
   exit 2
fi
