#!/bin/bash

# Description:
#   A workaround of the Azure RHUI EUS compatibility issue.
#   This script does the following actions:
#   1. Check whether the instance is confiured with RHUI EUS repos.
#   2. Try to frozen the $releasever for the RHUI EUS repos.
#   3. Update the $releasever configuration.

# check whether the instance is confiured with RHUI EUS repos
found=$(ls /etc/yum.repos.d/rh-cloud*eus*.repo 2>/dev/null | wc -l)
[ "$found" == "0" ] && echo "No RHUI EUS repos is configured." && exit 0

# get config file of RHUI EUS repos
[ "$found" != "1" ] && echo "Multiple repo files were found." && exit 1
rpfile=$(ls /etc/yum.repos.d/rh-cloud*eus*.repo) || exit 1

# check whether the $releasever is already frozen
grep -q '$releasever' $rpfile || exit 0

# backup the file if haven't yet
[ ! -e ${rpfile}.orginal ] && cp $rpfile ${rpfile}.orginal

# get current $releasever
releasever=$(cat /etc/yum/vars/releasever 2>/dev/null)
[ -z "$releasever" ] && echo "Failed to get \$releasever." && exit 1

# frozen the $releasever for the RHUI EUS repos
echo "Forzen release version for RHUI repos to \"$releasever\"."
sed -i "s/\$releasever/$releasever/g" $rpfile

# set the new $releasever
releasever=${releasever%%.*}

# update the $releasever configuration
rlsfile=/etc/yum/vars/releasever
echo "Set the release version in $rlsfile to \"$releasever\"."
[ ! -e ${rlsfile}.orginal ] && cp $rlsfile ${rlsfile}.orginal
echo $releasever >$rlsfile

exit 0
