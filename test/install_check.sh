#!/bin/bash

# Installability check: packagesearch must -net install- from
#   1. a release archive built from HEAD (git archive, which honours
#      .gitattributes, so this is what a GitHub release ships), and
#   2. every net install URL that README.md and docs/RELEASING.md give.
# Each source installs into its own empty PLUS directory (test/install_check.do).
# Run from the repository root. Needs git, network access and Stata
# (stata-mp is assumed; override with STATA=...).

STATA=${STATA:-stata-mp}

rm -rf install_check_archive install_check_plus install_check_sources.txt install_check_result.txt
mkdir install_check_archive
# safe.directory: in the CI container the checkout belongs to another user
git -c safe.directory='*' archive HEAD | tar -x -C install_check_archive || exit 1

{
   echo "$(pwd)/install_check_archive"
   grep -ho 'net install packagesearch[^`]*from("[^"]*")' README.md docs/RELEASING.md \
      | sed 's/.*from("\([^"]*\)").*/\1/' | sort -u
} > install_check_sources.txt
nsources=$(wc -l < install_check_sources.txt)

# Sources go through a file: given as arguments, Stata would name the
# batch log after the last one rather than after the do-file.
$STATA -b do test/install_check.do

if [[ ! -f install_check_result.txt ]]
then
   echo "Installability check did not run; see install_check.log"
   exit 1
fi
cat install_check_result.txt
if [[ $(grep -c '^ok ' install_check_result.txt) -ne $nsources ]]
then
   echo "Installability check failed; see install_check.log"
   exit 1
fi
echo "Installs from all $nsources sources"
