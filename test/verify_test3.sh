#!/bin/bash


if [[ -f test2.log ]]
then
   # Verify first test: one of the files has a variable that is too long (var is 32char, but prepend makes it too long)
   grep -B 9 "====Test 3-1: END" test3.log > actual_output3-1.txt
   diff actual_output3-1.txt test/expected_output3-1.txt || (echo "Not the expected output: Test 3-1"; exit 2)
   echo "Success: Test 3-1"
   # Verify second test: cleanly processed the file with underscores. Should only find the expected output
   tail -17 test3.log | cut -b -55  > actual_output3-2.txt
   diff actual_output3-2.txt test/expected_output3-2.txt || (echo "Not the expected output: Test 3-2"; exit 2)
   echo "Success: Test 3-2"
   exit 0 
else
   echo "Something went wrong with running Stata"
   exit 2
fi

