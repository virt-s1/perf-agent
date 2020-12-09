# pbench-fio usage

## 1. Get the TestRunID

Example:

```bash
testrun_id=$(./make_testrunid.py --type fio --platform ESXi \
--compose RHEL-8.3.0-2020111009.2 --customized-labels lite_scsi) || exit 1
```

## 2. Create log path

Example:

```bash
log_path="/some-path-to-yours/$testrun_id"
mkdir -p $log_path || exit 1
```

## 3. Write down metadata entries to a json file

Example:

```bash
./write_metadata.py --file $log_path/testrun_metadata.json \
    --keypair testrun.platform=ESXi \
    --keypair testrun.type=fio \
    --keypair os.compose=RHEL-8.3.0-2020111009.2 \
    --keypair disk.backend=NVMe \
    --keypair disk.driver=scsi \
    --keypair disk.format=raw \
    --keypair vm.cpu=64 \
    --keypair vm.memory=16G \
    --keypair hardware.flavor=esx.g2.4xlarge
```

## 4. Run the pbench-fio test

Example:

```bash
# Run pbench-fio for sequential access
./pbench-fio.wrapper --config=$testrun_id \
    --job-file=./fio-default.job --samples=5 \
    --targets=/dev/sdx --job-mode=concurrent \
    --pre-iteration-script=./drop-cache.sh \
    --test-types=write \
    --block-sizes=4,1024 \
    --iodepth=1,64 --numjobs=16

# Run pbench-fio for random access
./pbench-fio.wrapper --config=$testrun_id \
    --job-file=./fio-default.job  --samples=5 \
    --targets=/dev/sdx --job-mode=concurrent \
    --pre-iteration-script=./drop-cache.sh \
    --test-types=randrw \
    --block-sizes=4,1024 \
    --iodepth=1,64 --numjobs=1
```

## 5. Collect test results to the log path

Example:

```bash
# Collect test results to the log path
mv /var/lib/pbench-agent/$testrun_id* $log_path
```
