#!/bin/bash

# Keep only the rows of the table of candidate packages and their package names,
# sorted (the rank column, and so the row order, follows SSC popularity)
normalize() {
   grep -E '^ +[0-9]+\. \|' | awk '{print $3}' | sort
}

if [[ -f test4.log ]]
then
   # Verify: delimiters separate words, and macro-built names stay in one piece
   sed -n '/^Candidate packages listed below/,/^====Test 4: END/p' test4.log > actual_output4.txt
   diff <(normalize < actual_output4.txt) <(sort test/expected_output4.txt) || { echo "Not the expected output: Test 4"; exit 2; }
   echo "Success: Test 4"
   exit 0
else
   echo "Something went wrong with running Stata"
   exit 2
fi
