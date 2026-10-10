#!/bin/bash

# Assumes stata-mp is in the path (override with STATA=...)
# Each test do-file installs the package from the local checkout (test/install.do)

STATA=${STATA:-stata-mp}
failed=0

for t in 1 2 3
do
   # Test 2: what happens when there are long words
   # Test 3: what happens when there are duplicate keywords
   $STATA -b do test/test$t.do
   test/verify_test$t.sh || failed=1
done

if [[ $failed -ne 0 ]]
then
   echo "One or more tests failed"
   exit 1
fi
echo "All tests passed"
