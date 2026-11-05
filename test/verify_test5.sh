#!/bin/bash

# Keep only the rows of the table of candidate packages, with the package name and
# the keyword (or count of keywords). The rank and probFalsePos columns, and so the
# row order, follow SSC popularity, which changes monthly.
normalize() {
   grep -E '^ +[0-9]+\. \|' | awk '{print $3, $6}' | sort
}

if [[ -f test5.log ]]
then
   # A file that could not be scanned would fail the tests below for the wrong reason
   if grep -qE '^w_[a-z0-9]+ invalid name|^Error: file ' test5.log
   then
      echo "Not the expected output: Test 5 (file not scanned)"
      exit 2
   fi
   # Verify first test: every candidate package is found once, and its keywords are
   # counted once each
   sed -n '/^====Test 5-1: BEGIN/,/^====Test 5-1: END/p' test5.log | sed -n '/^Candidate packages/,$p' > actual_output5-1.txt
   diff <(normalize < actual_output5-1.txt) <(normalize < test/expected_output5-1.txt) || { echo "Not the expected output: Test 5-1"; exit 2; }
   echo "Success: Test 5-1"
   # Verify second test: details lists each cleaned keyword
   sed -n '/^====Test 5-2: BEGIN/,/^====Test 5-2: END/p' test5.log | sed -n '/^Candidate packages/,$p' > actual_output5-2.txt
   diff <(normalize < actual_output5-2.txt) <(normalize < test/expected_output5-2.txt) || { echo "Not the expected output: Test 5-2"; exit 2; }
   echo "Success: Test 5-2"
   exit 0
else
   echo "Something went wrong with running Stata"
   exit 2
fi
