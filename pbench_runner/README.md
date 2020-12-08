# Usage

## Run FIO tests

Deliver `*.sh` and `*.job` files to the pbench controller.
Run `run_fio_tests.sh -h` to check the usage of this script.
Run `deliever_fio_logs.sh` to deliver the logs to the pbench server.

## New procedure

```bash
# Get TestRunID
testrun_id=$(make_testrunid.py --type fio --platform ESXi \
--compose RHEL-8.3.0-2020111009.2 --customized-labels lite_scsi) || exit 1

# Create log directory
log_path="./$testrun_id"
mkdir -p $log_path

# Change to log directory
cd $log_path

# Write down metadata to a json file
write_metadata.py --file $log_path/testrun_metadata.json \
    --keypair testrun.platform=ESXi \
    --keypair testrun.type=fio \
    --keypair os.compose=RHEL-8.3.0-2020111009.2 \
    --keypair disk.backend=NVMe \
    --keypair disk.driver=scsi \
    --keypair disk.format=raw \
    --keypair host.cpu=32 \
    --keypair host.memory=16G

```
