#!/bin/bash

# Description:

function switch_back_to_noneus() {
    # Switch a RHEL 7.x/8.x VM back to non-EUS.
    # Ref. https://docs.microsoft.com/en-us/azure/virtual-machines/workloads/redhat/redhat-rhui#switch-a-rhel-8x-vm-back-to-non-eus-remove-a-version-lock

    # verify EUS repo
    local pkgs=$(rpm -qa)
    local rhel_ver=""
    echo $pkgs | grep -q rhui-azure-rhel7-eus && rhel_ver=7
    echo $pkgs | grep -q rhui-azure-rhel8-eus && rhel_ver=8

    [ -z $rhel_ver ] && echo "EUS repo was not installed or not supported." && exit 1

    # remove EUS repos
    yum --disablerepo='*' remove 'rhui-azure-rhel*-eus' -y

    # remove the version lock
    mv -f /etc/yum/vars/releasever /etc/yum/vars/releasever.bak

    # get the regular repos config file and add non-EUS repos
    yum --config="https://rhelimage.blob.core.windows.net/repositories/rhui-microsoft-azure-rhel${rhel_ver}.config" \
        install "rhui-azure-rhel${rhel_ver}"
}

function enable_codeready_repo() {
    # Enable the CodeReady repos
    yum-config-manager --enable "rhui-codeready-builder-for-rhel-*-x86_64-rhui-rpms"
}

function install_yum_utils() {
    # install yum_config_manger
    yum install -y yum-utils
}

function enable_private_repos() {
    [ ! -e /etc/yum.repos.d/rhel.repo ] && echo "No private repos was found." && exit 1
    yum-config-manager --enable rhel-appstream rhel-base || exit 1
}

# main

# for instance with private repos
if [ -e /etc/yum.repos.d/rhel.repo ]; then
    echo "Enable private repos."
    install_yum_utils
    enable_private_repos
    exit 0
fi

# for instance with EUS repos
rpm -qa | grep -q "rhui-azure-rhel*-eus"
if [ "$?" = "0" ]; then
    echo "Switch back to non-EUS and enable CodeReday repos."
    switch_back_to_noneus
    install_yum_utils
    enable_codeready_repo
    exit 0
fi

# for instance with non-EUS repos
rpm -qa | grep -v "rhui-azure-rhel*-eus" | grep -q "rhui-azure-rhel"
if [ "$?" = "0" ]; then
    echo "Enable CodeReday repos."
    install_yum_utils
    enable_codeready_repo
    exit 0
fi

exit 0
