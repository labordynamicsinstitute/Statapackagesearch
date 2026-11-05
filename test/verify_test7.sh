#!/bin/bash

# Each scan finds nothing to report: it must say so, and finish without an error.
check() {
   local n=$1 message=$2 output
   output=$(sed -n "/^====Test 7-$n: BEGIN/,/^====Test 7-$n: END/p" test7.log)
   grep -q "^====Test 7-$n: rc=0\$" <<<"$output" || { echo "Stopped with an error: Test 7-$n"; exit 2; }
   grep -q "^$message" <<<"$output" || { echo "Not the expected output: Test 7-$n"; exit 2; }
   echo "Success: Test 7-$n"
}

if [[ -f test7.log ]]
then
   check 1 "No matched packages found"
   check 2 "No matched packages found"
   check 3 "No Stata .do files found"
   check 4 "All matched packages found were false positives"
   exit 0
else
   echo "Something went wrong with running Stata"
   exit 2
fi
