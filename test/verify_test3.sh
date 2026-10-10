#!/bin/bash

# Keep only table rows, drop the row number and the "rank" column (SSC popularity
# changes monthly), and sort (row order among tied ranks is not stable)
normalize() {
   grep -E '^ +[0-9]+\. \|' | awk '{print $3, $5, $6}' | sort
}

if [[ -f test3.log ]]
then
   # Verify first test: multiple keywords from the same package yield only one match
   grep -B 9 "====Test 3-1: END" test3.log > actual_output3-1.txt
   diff <(normalize < actual_output3-1.txt) <(normalize < test/expected_output3-1.txt) || { echo "Not the expected output: Test 3-1"; exit 2; }
   echo "Success: Test 3-1"
   # Verify second test: details option lists each matched keyword
   tail -17 test3.log | cut -b -55  > actual_output3-2.txt
   diff <(normalize < actual_output3-2.txt) <(normalize < test/expected_output3-2.txt) || { echo "Not the expected output: Test 3-2"; exit 2; }
   echo "Success: Test 3-2"
   exit 0
else
   echo "Something went wrong with running Stata"
   exit 2
fi

