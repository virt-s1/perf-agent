#!/bin/bash

# Description: Configure the Alibaba environment for pbench setup.

PRIVATE_REPOS_FILE=/etc/yum.repos.d/rhel.repo

function is_private_image() {
    # check if the instance starts from private image
    [ -f /etc/image-id ] && return 1 || return 0
}

function has_private_repos() {
    # check if the image has private yum repos
    [ -f ${PRIVATE_REPOS_FILE} ] && return 0 || return 1
}

function enable_private_repos() {
    # enable private yum repos
    sed -i 's/^.*enable=.*$/enable=1/' ${PRIVATE_REPOS_FILE}
}

function disable_private_repos() {
    # disable private yum repos
    sed -i 's/^.*enable=.*$/enable=0/' ${PRIVATE_REPOS_FILE}
}

function enable_yum_repo_proxy() {
    # enable yum repo proxy
    sed -i 's/^#proxy=/proxy=/' ${PRIVATE_REPOS_FILE}
}

function disable_yum_repo_proxy() {
    # disable yum repo proxy
    sed -i 's/^proxy=/#proxy=/' ${PRIVATE_REPOS_FILE}
}

# main

# for instance with private repos
if (is_private_image); then
    echo "The instance starts from private image."
else
    echo "The instance starts from alibaba image."
    echo "Nothing to be configured."
    exit 0
fi

if (has_private_repos); then
    echo "Found private repos."
else
    echo "No private repos was configured."
    exit 1
fi

# Enable private repos
enable_private_repos
enable_yum_repo_proxy

# Show status of the private repos
grep -e "^name=" -e "^proxy" ${PRIVATE_REPOS_FILE}

exit 0
