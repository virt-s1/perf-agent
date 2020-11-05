#/bin/bash

set -e

[ ! -f "./config/id_rsa" ] && ssh-keygen -t rsa -N "" -q -f ./config/id_rsa
[ ! -f "./config/id_rsa.cloud" ] && ssh-keygen -t rsa -N "" -q -f ./config/id_rsa.cloud

ansible-playbook -i ./inventory --extra-vars "working_dir=$PWD ansible_python_interpreter=auto" pbench_setup.yml

exit 0
