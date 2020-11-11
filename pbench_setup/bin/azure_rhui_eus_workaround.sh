#!/bin/bash

# Description:
#   A workaround of the Azure RHUI EUS compatibility issue.
#   This script does the following actions:
#   1. Check whether the instance is confiured with RHUI EUS repos.
#   2. Try to frozen the $releasever for the RHUI EUS repos.
#   3. Disable the /etc/yum/vars/releasever configuration.

# check whether the instance is confiured with RHUI EUS repos.
found=$(ls /etc/yum.repos.d/rh-cloud*eus*.repo 2>/dev/null | wc -l)
[ "$found" == "0" ] && echo "No RHUI EUS repos is configured." && exit 0

# get config file of RHUI EUS repos
[ "$found" != "1" ] && echo "Multiple repo files were found." && exit 1
rpfile=$(ls /etc/yum.repos.d/rh-cloud*eus*.repo) || exit 1

# backup the file if haven't yet
[ ! -e ${rpfile}.orginal ] && cp $rpfile ${rpfile}.orginal

# get current $releasever
releasever=$(cat /etc/yum/vars/releasever) || exit 1
[ -z "$releasever" ] && echo "Failed to get \$releasever." && exit 1

# Frozen the $releasever for the RHUI EUS repos.
echo "Forzen release version for RHUI repos to \"$releasever\"."
sed -i "s/\$releasever/$releasever/g" $rpfile

# Disable the /etc/yum/vars/releasever configuration
mv /etc/yum/vars/releasever /etc/yum/vars/releasever.bak

exit 0
