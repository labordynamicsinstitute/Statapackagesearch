#!/bin/bash

# Keep only the rows of the table of candidate packages, with the package name and
# the likelihood of a false positive. The rank column, and so the row order, follows
# SSC popularity, which changes monthly.
rows() {
   sed -n "/^====Test 6-$1: BEGIN/,/^====Test 6-$1: END/p" test6.log \
      | sed -n '/^Candidate packages/,$p' \
      | grep -E '^ +[0-9]+\. \|' | awk '{print $3, $5}' | sort
}

if [[ -f test6.log ]]
then
   # Verify first test: packages that have left SSC are reported, as unlikely
   diff <(rows 1) <(printf 'cmaxuse 1\npip 1\nreghdfe 0\n') || { echo "Not the expected output: Test 6-1"; exit 2; }
   echo "Success: Test 6-1"
   # Verify second test: a domain() list restricts what is reported
   diff <(rows 2) <(printf 'reghdfe 0\n') || { echo "Not the expected output: Test 6-2"; exit 2; }
   echo "Success: Test 6-2"
   # Verify third test: installing carries on past packages that have left SSC
   sed -n '/^====Test 6-3: BEGIN/,/^====Test 6-3: END/p' test6.log > actual_output6-3.txt
   grep -q '^Could not install pip from SSC' actual_output6-3.txt \
      && grep -q '^Finished installing' actual_output6-3.txt \
      || { echo "Not the expected output: Test 6-3"; exit 2; }
   echo "Success: Test 6-3"
   exit 0
else
   echo "Something went wrong with running Stata"
   exit 2
fi
