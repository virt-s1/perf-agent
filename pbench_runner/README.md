# Usage

## 1. Generate a TestRunID

Command:

```bash
testrun_id=$(./make_testrunid.py \
    --type fio \
    --platform ESXi \
    --compose RHEL-8.4.0-20201209.n.0 \
    --customized-labels x86_bios_scsi_standard)
```

Notes:
- This script helps to generate a unified TestRunID.
- `--customized-labels` parameter can contain many labels separated by `_`.
- If not specified with `--timestamp`, the script will generate an ID with the current timestamp.
- Get more details by `make_testrunid.py --help`.

Example of a unified TestRunID:
```
fio_ESXi_RHEL-8.4.0-20201209.n.0_x86_bios_scsi_standard_D201220T212213
--- ---- ----------------------- ---------------------- --------------
|   |    |                       |                      |__________ Timestammp
|   |    |                       |_________________________________ Customized labels
|   |    |_________________________________________________________ Compose ID
|   |______________________________________________________________ Platform: "ESXi", "AWS", etc
|__________________________________________________________________ TestType: "fio", "uperf", etc
```

## 2. Create log path

Command:

```bash
mkdir /nfs-mount
mount -t nfs perf-insight.lab.eng.pek2.redhat.com:/nfs /nfs-mount
log_path="/nfs-mount/perf-insight/testruns/$testrun_id"
mkdir -p $log_path
```

Notes:
- Currently, we deliver logs to the perf-insight server via NFS.

## 3. Generate metadata.json file

Command:

```bash
./write_metadata.py --file $log_path/metadata.json \
    --keypair testrun-id=$testrun_id \
    --keypair testrun-type=fio \
    --keypair testrun-platform=ESXi \
    --keypair ......
```

Notes:
- This script can be run more than once, it performs add/update logic to the json file.
- When preparing metadata, follow the example below to obtain the key pair name and format.
- The key pair name and format can be changed in the future, so keep an eye on this.
- If you need to add key pairs, please contact the project owners to ensure consistency.

```js
{
   // The TestRun information
   "testrun-id": "fio_ESXi_RHEL-8.4.0-20201209.n.0_x86_bios_scsi_standard_D201220T212213",
   "testrun-type": "fio",               // "uperf" for pbench-uperf tests
   "testrun-platform": "ESXi",          // "Hyper-V", "AWS", "Azure", etc
   "testrun-date": "2020-12-20",        // When was this test performed?
   "testrun-comments": "",              // Leave any comments here
   // The Guest OS information
   "os-branch": "RHEL-8.4",
   "os-compose": "RHEL-8.4.0-20201209.n.0",
   "os-kernel": "4.18.0-259.el8.x86_64",
   "tool-fio_version": "fio-3.19-3.el8.x86_64",         // pbench-fio only
   "tool-uperf_version": "uperf-1.0.7-1.el8.x86_64",    // pbench-uperf only
   // The guest(VM) information
   "guest-flavor": "esx.g2.4xlarge",    // Consult project owners
   "guest-cpu": "16",
   "guest-memory": "64GB",
   // The host(hypervisor) information
   "hypervisor-cpu": "128",
   "hypervisor-cpu_model": "AMD EPYC 7251",
   "hypervisor-version": "VMware ESX 7.0.1 build-16850804",
   // The hardware information (storage tests only)
   "hardware-disk-capacity": "80G",
   "hardware-disk-backend": "NVMe",
   "hardware-disk-driver": "SCSI",
   "hardware-disk-format": "raw",
   // The hardware information (network tests only)
   "hardware-net-capacity": "40GiB",
   "hardware-net-driver": "VMXNET3",
   "hardware-net-speed": "10000Mb/s",
   "hardware-net-duplex": "Full", 
   // The cloud information (cloud only)
   "cloud-az": "us-west-1a",
   "cloud-region": "us-west-1",
}
```

## 4. Run pbench tests

### 4.1 pbench-fio

Command:

```bash
# Check target volume
[ -b /dev/sdx ] || exit 1

# Run pbench-fio tests (standard)
./pbench-fio.wrapper --config=${testrun_id#*_} \
    --job-file=./fio-default.job --samples=5 \
    --targets=/dev/sdx --job-mode=concurrent \
    --pre-iteration-script=./drop-cache.sh \
    --test-types=read,write,rw,randread,randwrite,randrw \
    --block-sizes=4,64,1024 --runtime=30 \
    --iodepth=1,8,64 --numjobs=1,16
```

Notes:
- `pbench-fio.wrapper` is a workaround to support iteration on `iodepth` and `numjobs` to meet QE requirments. It keeps the same usage of `pbench-fio`.
- `${testrun_id#*_}` is the remaining part without TestType, so that pbench generates test logs into `/var/lib/pbench-agent/TestRunID_*` folders.
- This script can be run multiple times to complete your testing.
- The different test dimension meet difference test requirements, the details can be found in the table below.
  - "all_types" stands for "read,write,rw,randread,randwrite,randrw".
  - `ramptime` is set to 5 seconds for the tests, so `runtime=10` can be valid.
  - It is strongly recommended to put the dimension keywords in TestRunID.
  - To use any customized dimension other than the listed, put the "customized" keyword in TestRunID.

| Dimension | Duration | test-types | block-sizes      | iodepth     | numjobs   | samples | runtime |
| :-------- | :------- | :--------- | :--------------- | :---------- | :-------- | :------ | :------ |
| quick     | ~ 1.6h   | all_types  | 4,1024           | 1,64        | 1,16      | 3       | 10s     |
| standard  | ~ 9h     | all_types  | 4,64,1024        | 1,8,64      | 1,16      | 5       | 30s     |
| extended  | ~ 50h    | all_types  | 4,16,64,256,1024 | 1,4,8,32,64 | 1,8,16,32 | 5       | 30s     |

### 4.2 pbench-uperf

Command:

```bash
# Run pbench-uperf-runner tests (quick)
./pbench-uperf-runner.py --server_ip SERVER_IP --client_ip CLIENT_IP --config ${testrun_id#*_} --test_suite_name quick

More:
./pbench-uperf-runner.py --help
usage: pbench-uperf-runner.py [-h] --server_ip SERVER_IP --client_ip CLIENT_IP --config CONFIG [--test_suite_name TEST_SUITE_NAME] [--protocols PROTOCOLS] [--test_types TEST_TYPES] [--runtime RUNTIME] [--message_sizes MESSAGE_SIZES] [--instances INSTANCES] [--nr_samples NR_SAMPLES] [--max_failures MAX_FAILURES]
                              [--maxstddevpct MAXSTDDEVPCT]

Arguments of Pbench-uperf.

optional arguments:
  -h, --help            show this help message and exit
  --server_ip SERVER_IP
  --client_ip CLIENT_IP
  --config CONFIG
  --test_suite_name TEST_SUITE_NAME
                        Test suite name.
  --protocols PROTOCOLS, -p PROTOCOLS
                        Network performance protocols supports.
  --test_types TEST_TYPES, -t TEST_TYPES
                        Network performance test types supports.
  --runtime RUNTIME, -r RUNTIME
                        Run time one case run.
  --message_sizes MESSAGE_SIZES, -m MESSAGE_SIZES
                        Message size used in test.
  --instances INSTANCES, -i INSTANCES
                        Counts of threads.
  --nr_samples NR_SAMPLES, -ns NR_SAMPLES
                        Counts of runs.
  --max_failures MAX_FAILURES, -mf MAX_FAILURES
                        Max failures times of one case.
  --maxstddevpct MAXSTDDEVPCT, -ms MAXSTDDEVPCT
                        Max stddevpct to check.
```

Notes:
- `pbench-uperf-runner` allows users to use above 0 or mulit options.
- `${testrun_id#*_}` is the remaining part without TestType, so that pbench generates test logs into `/var/lib/pbench-agent/TestRunID_*` folders.
- This script can be run multiple times to complete your testing.
- The different test dimension meet difference test requirements, the details can be found in the table below.
  - "all_types" stands for "stream,maerts,bidirec,rr".
  - It is strongly recommended to put the dimension keywords in TestRunID.
  - To use any customized dimension other than the listed, put the "customized" keyword in TestRunID.

| Dimension | Duration | test-types | message_szie     | protocols   | instanc   | samples | runtime |
| :-------- | :------- | :--------- | :--------------- | :---------- | :-------- | :------ | :------ |
| quick     | ~ 1h     | all_types  | 1                | tcp,udp     | 1         | 3       | 20s     |
| standard  | ~ 6h     | all_types  | 1,64             | tcp,udp     | 1,8       | 5       | 30s     |
| extended  | ~ 40h    | all_types  | 1,64,1024,16384  | tcp,udp     | 1,8,64    | 5       | 60s     |


## 5. Deliver TestRun results

Command:

```bash
mv /var/lib/pbench-agent/${testrun_id}* $log_path
```

Notes:
- Currently, we deliver logs to the perf-insight server via NFS.


## 6. Load the results into database and generate benchmark report

Command:

```bash
# Load the results into database
ssh virtqe@perf-insight.lab.eng.pek2.redhat.com sudo /opt/perf-insight/utils/process_testrun.sh -t ${testrun_id} -s -d -P

# Generate benchmark report
ssh virtqe@perf-insight.lab.eng.pek2.redhat.com sudo /opt/perf-insight/utils/compare_testruns.sh -t ${testrun_id} -b <base_testrun_id>
```

Notes:
- This is a temporary solution to perform these actions using `ssh`. Therefore, you will need to handle the authentication of ssh keypairs by yourself.
- `compare_testruns.sh` will prompt the "URL of the report" in the last line. So that you can get the URL to send with your email.
