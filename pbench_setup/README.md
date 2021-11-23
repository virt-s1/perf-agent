# The pbench setup scripts

These scripts are designed to run on your laptop or master node (if you use Jenkins CI) to remotely set up a test machine using Ansible.

# Usage

## 1. Update ansible_vars.yaml

The `./ansible_vars.yaml` cantains the options for setting up pbench. It could be like this:

```yml
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

Notes:
1. The `system_type` can be one of the following values:
   1. local - run for local BMs or VMs inside Red Hat network;
   2. aws - run for AWS instances;
   3. azure - run for the Azure instances;
   4. alibaba - run for the Alibaba instances;
2. At this time, `os_vendor` can only be `rhel`.
3. If you want to install additional packages, set `package_install` to `1` and provision `package_list` according to your needs, otherwise set it to `0`.
4. Set `pbench_install` to `1` for pbench installation, otherwise set to `0`.
5. Set `dev_env_install` to `1` to install `@Development tools` for uperf, otherwise set to `0`.

## 2. Configure ansible.cfg

The `./ansible.cfg` provides Ansible the basic configurations. It could be like this:

```ini
[defaults]
remote_user=root
log_path=./ansible.log
#private_key_file=~/.pem/cheshi.pem

[ssh_connection]
ssh_args="-C -o ControlMaster=auto -o ControlPersist=20m"
```

Notes:
- Provision `remote_user` and `private_key_file` to let Ansible know how to connect to your test machine.

## 3. Provision inventory

The `./inventory` file tells Ansible which test machine to connect and set up. It could be like this:

```ini
54.201.27.5
54.201.27.6
#54.202.189.22 ansible_ssh_extra_args="-R 8080:localhost:3128"
#54.202.189.23 ansible_ssh_extra_args="-R 8080:localhost:3128"
```

Notes:
- If you need to setup pbench on multiple test machines. You can list all of them in the inventory file. Just like the example above.
- When using a private image on clouds, you might consider enabling the "ssh reverse proxy" by adding the `ansible_ssh_extra_args` option to the specific host. In this case, you need to set up an http proxy on the Ansible host (`localhost`), or change `localhost` to any existing proxy server that the Ansible host can access.

## 4. Execute setup.sh

Execute `./setup.sh` to start the setup process.

Notes:
- This script will download the latest sshkey and config files from Red Hat intranet if you didn't provide them.
- Thus if you want to use your own sshkey and config files, you should put them into `./config` before running `setup.sh`.

Notes:
- The latest sshkey and config files are required to use `pbench-copy-results`.
- Script `setup.sh` will download the latest sshkey and config files from the Red Hat intranet for you.
- In addition, if you want to use your own sshkey and config files, you should put them in `./config` before running `setup.sh`. (Check the code for more details)
