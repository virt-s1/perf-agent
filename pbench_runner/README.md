# Usage

This is about using pbench-fio and pbench-uperf on the test machine.  
Since perf-insight supports users to store their test logs on perf-insight or pbench-server (recommended), this instruction will cover both usages. Choose the correct description based on your situation.

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

## 2. Setup and configuration

### 2.1 General preparation

Command:

```bash
# Setup picli tool
curl https://raw.githubusercontent.com/virt-s1/perf-insight/main/cli_tool/picli -o /bin/picli
curl https://raw.githubusercontent.com/virt-s1/perf-insight/main/cli_tool/.picli.toml -o ~/.picli.toml

chmod a+x /bin/picli
sed -i 's/localhost:5000/perf-insight.lab.eng.pek2.redhat.com:5000/' ~/.picli.toml

pip3 install click tabulate --user
```

### 2.2 Store logs on perf-insight

Command:

```bash
mkdir /nfs-mount
mount -t nfs perf-insight.lab.eng.pek2.redhat.com:/nfs/perf-insight/.staging /nfs-mount
log_path="/nfs-mount/${testrun_id}"
mkdir -p ${log_path}
```

> Notes: The logs will be delieverd to the perf-insight server via NFS.

### 2.3 Store logs on pbench-server

TBD

`log_path=/var/lib/pbench-agent`

## 3. Generate metadata.json file

Command:

```bash
./write_metadata.py --file ${log_path}/metadata.json \
    --keypair testrun-id=${testrun_id} \
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

# Run pre-defined pbench-fio tests in a quick/standard/extended mode
./pbench-fio-runner.py --testrun-id ${testrun_id} --targets /dev/sdx --mode <quick|standard|extended>

# Or, run a bunch of custom tests
./pbench-fio-runner.py --testrun-id ${testrun_id} --targets /dev/sdx --mode customized \
     --test-types rw --block-sizes 1024 --iodepth 1,64 --numjobs 1,16 --samples 3 --runtime 10
./pbench-fio-runner.py --testrun-id ${testrun_id} --targets /dev/sdx --mode customized \
     --test-types randrw --block-sizes 4 --iodepth 1,64 --numjobs 1,16 --samples 3 --runtime 10

# Or, reproduce the failure cases from a benchmark report
report_id=<Report ID>   # Ex. "benchmark_xxxxxxxx_over_xxxxxxxx"
./pick_up_cases.py --report-id ${report_id}
./pbench-fio-runner.py --testrun-id ${testrun_id} --targets /dev/sdx --mode backlog
```

Notes:
- The script `pbench-fio-runner.py` **can be run multiple times** to complete your testing, all the results will be collected as the whole TestRun.
- The `--mode` parameter in `pbench-fio-runner.py` can be any predefined test dimension (see below) defined in the `profiles.toml` file. In addition, there is a special mode called "backlog", which runs tests based on a specified backlog file.
- The different test dimension meet difference test requirements, the details can be found in the table below.
  - "all_types" stands for "read,write,rw,randread,randwrite,randrw".
  - `ramptime` is set to 5 seconds for the tests, so `runtime=10` can be valid.
  - It is strongly recommended to put the dimension keywords in TestRunID.
  - To use any customized dimension other than the listed, put the "customized" keyword in TestRunID.
- The script `pick_up_cases.py` is used to create a backlog from the benchmark report. By default, it only filters "Dramatic Regression" cases, but this behavior can be overridden by specifying the `--case-filter` parameter. For example, `--case-filter 'Dramatic Regression' --case-filter 'High Variance'` will collect both "Dramatic Regression" and "High Variance" cases into the backlog file.

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

# More
./pbench-uperf-runner.py --help

# Reproduce the failure cases from a benchmark report
./pick_up_cases.py --report-id <Benchmark Report ID>
./pbench-uperf-runner.py --server_ip SERVER_IP --client_ip CLIENT_IP --config ${testrun_id#*_} --test_suite_name backlog
```

Notes:
- `pbench-uperf-runner` allows users to use above 0 or mulit options.
- `${testrun_id#*_}` is the remaining part without TestType, so that pbench generates test logs into `/var/lib/pbench-agent/TestRunID_*` folders.
- This script can be run multiple times to complete your testing.
- The different test dimension meet difference test requirements, the details can be found in the table below.
  - "all_types" stands for "stream,maerts,bidirec,rr".
  - It is strongly recommended to put the dimension keywords in TestRunID.
  - To use any customized dimension other than the listed, put the "customized" keyword in TestRunID.
- The scrip `pbench-uperf-runner.py` supports run in the backlog mode by specifying `--test_suite_name quick` as `backlog`. See the "pbench-fio" section for more information.

| Dimension | Duration | test_types | message_sizes   | protocols | instances | samples | runtime |
| :-------- | :------- | :--------- | :-------------- | :-------- | :-------- | :------ | :------ |
| quick     | ~ 1h     | all_types  | 1               | tcp,udp   | 1         | 3       | 20s     |
| standard  | ~ 6h     | all_types  | 1,64            | tcp,udp   | 1,8       | 5       | 30s     |
| extended  | ~ 40h    | all_types  | 1,64,1024,16384 | tcp,udp   | 1,8,64    | 5       | 60s     |


## 5. Deliver TestRun results

You can choose deliver the results to either perf-insight or pbench-server (preferred).

### 5.1 Store logs on perf-insight

Command:

```bash
mv /var/lib/pbench-agent/${testrun_id}* ${log_path}
chcon -R -u system_u -t svirt_sandbox_file_t ${log_path}
```

> Notes: The logs will be delieverd to the perf-insight server via NFS.

### 5.2 Store logs on pbench-server

Command:

The default pbench-server is `pbench.perf.lab.eng.bos.redhat.com`.

```bash
# Specify the path to the metadata file
metadata_file=./metadata.json

# Specify the username on the pbench-server
pbench_username=virt-perftest-test

# Get args for pbench-copy-results
test_machine=$(cat ${metadata_file} | jq -r '."guest-flavor"')
testrun_id=$(cat ${metadata_file} | jq -r '."testrun-id"')

# Copy metadata.json into each subfolder
for d in $(ls -d ${testrun_id}*); do rm -f $d/${metadata_file}; cp ${metadata_file} $d; done

# Upload the logs to pbench-server
pbench-copy-results --user=${pbench_username} --controller=${test_machine} --prefix=${testrun_id}
```

Notes:
- `pbench_username` should be one of the following values:
  - `virt-perftest-test` for debugging or demostration;
  - `virt-perftest-aws` for AWS production;
  - `virt-perftest-aliyun` for Aliyun production;
  - `virt-perftest-azure` for Azure production;
  - `virt-perftest-esxi` for ESXi production;
  - `virt-perftest-hyperv` for Hyper-V production;
- Using `pbench-copy-results` rather than `pbench-move-results`
- `pbench-copy-results` will create `*.copied` file to avoid duplicate copies.

## 6. Load TestRun into perf-insight system

Based on where you have delivered the results to, you can either load the results from the perf-insight or import results from the pbench-server (preferred).

### 6.1 Logs stored on perf-insight

Command:

```bash
# Load the results from perf-insight
picli testrun-load --testrun-id ${testrun_id}
```

### 6.2 Logs stored on pbench-server

The default pbench-server is `pbench.perf.lab.eng.bos.redhat.com`.

Command:

```bash
# Import a bunch of TestRun results from pbench-server
picli testrun-imports --pbench-user ${pbench_username} --pbench-controller ${test_machine} --pbench-prefix ${testrun_id}
```

Notes:
- `picli testrun-imports` will help you import all the related testruns.
- Or you can use `picli testrun-import` to import testruns manally, that's an old method, in this way:
  - The External URLs will be `http://pbench.perf.lab.eng.bos.redhat.com/users/${pbench_username}/${test_machine}/${testrun_id}/${testrun_id}_*/` if your test machine is inside of the Red Hat network (ex. local VMs).
  - Or, you need to add `EC2::` before `${test_machine}` in the URL for external test machines (ex. public clouds)

## 7. Postprocess to the data

Command:

```bash
# Generate benchmark report
base_id=<Base TestRunID>
picli benchmark-create --test-id ${testrun_id} --base-id ${base_id}
report_id=benchmark_${testrun_id}_over_${base_id}

# Get more useful information about the report
if ! (jq --version); then sudo dnf install -y jq; fi

# Report URL (http://...)
picli --output-format json benchmark-inspect --report-id ${report_id} | jq -r '.url'

# Benchmark Conclusion (PASS/FAIL)
picli --output-format json benchmark-inspect --get-statistics true --report-id ${report_id} | jq -r '.statistics.benchmark_result'

# The number of DR cases (0 or 1,2,3,...)
picli --output-format json benchmark-inspect --get-statistics true --report-id ${report_id} | jq -r '.statistics.case_num_dramatic_regression'
```

Notes:
- Don't forget to install the `jq` package first (it has already been installed on perf-insight.lab.eng.pek2.redhat.com).
- You can get the Report URL to send with your email.

