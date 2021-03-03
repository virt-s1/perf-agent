# pbench-fio usage

## 1. Create a TestRunID

Example:

```bash
testrun_id=$(./make_testrunid.py \
    --type fio \
    --platform ESXi \
    --compose RHEL-8.3.0-2020111009.2 \
    --customized-labels x86_bios_scsi_lite)

[ -z $testrun_id ] && exit 1
```

## 2. Create log path

Example:

```bash
log_path="/nfs-mount-point-or-your-own-path/$testrun_id"
mkdir -p $log_path || exit 1
```

## 3. Write down metadata entries to a json file

Example:

```bash
./write_metadata.py --file $log_path/metadata.json \
    --keypair testrun-id=$testrun_id \
    --keypair testrun-type=fio \
    --keypair testrun-platform=ESXi \
    --keypair ......
```

Note: Please follow below keypairs to prepare your metadata.

```json
{
   "testrun-id": "fio_ESXi_RHEL-8.4.0-20201209.n.0_x86_64-BIOS-A_lite_scsi_D201220T212213",
   "testrun-type": "fio",
   "testrun-platform": "ESXi",
   "testrun-date": "2020-12-20",
   "testrun-comments": "", 
   "hardware-disk-capacity": "80G",
   "hardware-disk-backend": "NVMe",
   "hardware-disk-driver": "SCSI",
   "hardware-disk-format": "raw",
   "hardware-net-capacity": "40GiB",
   "hardware-net-driver": "", 
   "hardware-net-speed": "", 
   "hardware-net-duplex": "", 
   "os-branch": "RHEL-8.4",
   "os-compose": "RHEL-8.4.0-20201209.n.0",
   "os-kernel": "4.18.0-259.el8.x86_64",
   "tool-fio_version": "fio-3.19-3.el8.x86_64",
   "tool-uperf_version": "uperf",
   "guest-cpu": "16",
   "guest-flavor": "esx.g2.4xlarge",
   "guest-memory": "64GB",
   "cloud-region": "us-west-1",
   "hypervisor-cpu": "128",
   "hypervisor-cpu_model": "AMD EPYC 7251",
   "hypervisor-version": "VMware ESX 7.0.1 build-16850804"
}
```

## 4. Run the pbench-fio test

Example:

```bash
# Check target volume
[ -b /dev/sdx ] || exit 1

# Run pbench-fio for sequential access
./pbench-fio.wrapper --config=${testrun_id#*_} \
    --job-file=./fio-default.job --samples=5 \
    --targets=/dev/sdx --job-mode=concurrent \
    --pre-iteration-script=./drop-cache.sh \
    --test-types=read,write,rw \
    --block-sizes=4,64,1024 \
    --iodepth=1,8,64 --numjobs=1,16

# Run pbench-fio for random access
./pbench-fio.wrapper --config=${testrun_id#*_} \
    --job-file=./fio-default.job  --samples=5 \
    --targets=/dev/sdx --job-mode=concurrent \
    --pre-iteration-script=./drop-cache.sh \
    --test-types=randread,randwrite,randrw \
    --block-sizes=4,64,1024 \
    --iodepth=1,8,64 --numjobs=1,16
```

## 5. Collect test results to the log path

Example:

```bash
# Collect test results to the log path
mv /var/lib/pbench-agent/${testrun_id}* $log_path
```
