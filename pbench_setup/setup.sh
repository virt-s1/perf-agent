#/bin/bash

set -e

# Prepare the sshkey and config before installing pbench-agent
PRODUCTION_SSHKEY=http://git.app.eng.bos.redhat.com/git/perf-dept.git/plain/bench/pbench/agent/production/ssh/id_rsa
PRODUCTION_CONFIG=http://git.app.eng.bos.redhat.com/git/perf-dept.git/plain/bench/pbench/agent/production/config/pbench-agent.cfg
CLOUDS_SSHKEY=http://git.app.eng.bos.redhat.com/git/perf-dept.git/plain/bench/pbench/agent/ec2/ssh/id_rsa
CLOUDS_CONFIG=http://git.app.eng.bos.redhat.com/git/perf-dept.git/plain/bench/pbench/agent/ec2/config/pbench-agent.cfg

[ ! -f "./config/id_rsa" ] && curl -kL ${PRODUCTION_SSHKEY} -o ./config/id_rsa
[ ! -f "./config/pbench-agent-production.cfg" ] && curl -kL ${PRODUCTION_CONFIG} -o ./config/pbench-agent-production.cfg

[ ! -f "./config/id_rsa.cloud" ] && curl -kL ${CLOUDS_SSHKEY} -o ./config/id_rsa.cloud
[ ! -f "./config/pbench-agent-cloud.cfg" ] && curl -kL ${CLOUDS_CONFIG} -o ./config/pbench-agent-cloud.cfg

# Setup pbench-agent
ansible-playbook -i ./inventory --extra-vars "working_dir=$PWD ansible_python_interpreter=auto" pbench_setup.yml

exit 0
