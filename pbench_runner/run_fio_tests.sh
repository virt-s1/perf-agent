#!/bin/bash

# please upate the following varibles manually
platform=ESXi
compose=RHEL-8.3.0-20201109.n.0
label=lite_nvme
targets=/dev/sdx
samples=5
rw_list=read,write,rw,randread,randwrite,randrw
bs_list=4,256,1024
iodepth_list=1,8,64
numjobs=16

use_single_job_for_random_test=1
dryrun=1

timestamp=$(date +D%y%m%dT%H%M%S)
testrun=${platform}_${compose}_${label}_${timestamp}
# save metadata
mdfile=$HOME/workspace/metadata.info
cat >$mdfile <<EOF
testrun=fio_${testrun}
trigger=perf-agent
timestame=$timestamp
platform=$platform
compose=$compose
label=$label
targets=$targets
samples=$samples
rw_list=$rw_list
bs_list=$bs_list
iodepth_list=$iodepth_list
numjobs=$numjobs
use_single_job_for_random_test=$use_single_job_for_random_test
dryrun=$dryrun
EOF

for rw in $(echo $rw_list | tr ',' ' '); do
    for iodepth in $(echo $iodepth_list | tr ',' ' '); do
        # set numjobs for random tests
        jobs=$numjobs
        if [[ $rw =~ ^rand ]]; then
            [ "$use_single_job_for_random_test" = "1" ] && jobs=1
        fi

        # show info
        echo "(rw=$rw;bs=$bs_list;iodepth=$iodepth;numjobs=$jobs)"
        [ "$dryrun" = "1" ] && continue

        # call pbench-fio
        pbench-fio --config=$testrun \
            --job-file=$HOME/workspace/fio-default.job \
            --targets=$targets --job-mode=concurrent --samples=$samples \
            --pre-iteration-script=$HOME/workspace/drop-cache.sh \
            --test-types=$rw --block-sizes=$bs_list \
            --iodepth=$iodepth --numjobs=$jobs
    done
done

exit 0
