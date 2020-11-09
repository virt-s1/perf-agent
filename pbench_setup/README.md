# Use pbench setup Ansible scripts

## Update ansible_vars.yaml

The `./ansible_vars.yaml` cantains the options for setting up pbench. It looks like:

```
---
config_info:
  system_type: local
  os_vendor: rhel
  package_install: 1
  package_list:
    - zip
    - unzip
    - bc
    - numactl
    - time
  pbench_install: 1
  dev_env_install: 1
```

The `system_type` can be one of the following values:
- local - run for local VMs inside Red Hat network;
- aws   - run for AWS instances;
- azure - run for the Azure instances;

The `os_vendor` can only be `rhel` at this moment.

Set `package_install` as `1` and provision `package_list` according to your needs if you want to install additional packages, other wise set it as `0`.

Set `pbench_install` as `1` to perform pbench installation, other wise set it as `0`.

Set `dev_env_install` as `1` to install `@Development tools` for uperf, other wise set it as `0`.

## Configure ansible.cfg

The `./ansible.cfg` provides Ansible the basic configurations. It could be like this:

```
[defaults]
remote_user=root
#private_key_file=~/.pem/rhui-dev-cheshi.pem
```

Provision `remote_user` and `private_key_file` to let Ansible know how to connect to the host.

## Provision inventory

The `./inventory` file tells Ansible which host(s) to be connected.

If you need to setup pbench on more than one host. You can list all the IPs in the inventory file. Just like this:

```
54.201.247.22
54.202.189.64 ansible_ssh_extra_args="-R 8080:localhost:3128"
```

When using private image on clouds, you might consider enabling the "ssh reverse proxy". You can do this by adding `ansible_ssh_extra_args` option to the specific host.

## Execute setup.sh

Finally, you can execute `./setup.sh` to start the setup process.
