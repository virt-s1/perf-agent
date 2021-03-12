# -*- coding=utf-8 -*-

# File Name: pbench-uperf.wrapper
# Description:
#	A wrapper of pbench-uperf, provides cmdline paramters,
#	or read parameters from YAML to run pbench-uperf test.
# Plans:
#   v0.0.1 - 03/10/2021 - Filter function to confirm paramters None or not.
#   v0.0.2 - 03/12/2021 - Write ret.stdout to a file.
#   v0.0.3 - 03/12/2021 - Use re to check parameter 'config' correct or not.
# Reversions:
#   v0.0.1 - 03/01/2021 - Built the script.
#   v0.1.0 - 03/03/2021 - Supported 'group' different commands of click.
#   v0.2.0 - 03/04/2021 - Supported test suites to run test.
#   v0.3.0 - 03/06/2021 - Fixed int parameters from YAML.
#   v0.4.0 - 03/07/2021 - Removed 'group' of click.
#   v0.5.0 - 03/09/2021 - Handled parameters values None or not.
#   v0.5.1 - 03/12/2021 - Enhanced script comments.
#   v0.6.0 - 03/12/2021 - Fixed full test suites parameters values when YAML file was changed.


import os
import click
import yaml
import subprocess


# YAML file name.
file_name = "pbench-uperf.job"


# Read a pbench-uperf.job YAML which owns full test cases by default.
def get_yaml(file_name):
    # To find a pbench-uperf.job file located the same folder with the script.
    job_path = os.path.abspath(".")
    job_file = os.path.join(job_path, file_name)
    if os.path.isfile(job_file) and os.path.exists(job_file):
        print("INFO: Job file - {} exists.".format(file_name))
    else:
        print("ERROR: Exit as file has been gone.")
        exit 1

    # Open target YAML file.
    with open(job_file, "r", encoding = "utf-8") as jf:
        job_content = yaml.load(jf.read(), Loader=yaml.Loader)
        # print("DEBUG: job_content:\n{}".format(job_content))

    # Below keys are the parameters from the YAML file to configure pbench-uperf test.
    config = job_content["config"]
    print(config)
    
    # Type of protocols is a list.
    protocols = job_content["protocols"]
    protocols = ",".join(protocols)
    print(protocols)

    # Type of test_types is a list.
    test_types = job_content["test-types"]
    test_types = ",".join(test_types)
    print(test_types)

    runtime = job_content["runtime"]
    print(runtime)

    # Convert int elements of list to str, as pbench-uperf is a shell script.
    message_sizes = job_content["message_sizes"]
    message_sizes = [str(x) for x in message_sizes]
    # Type of message_sizes is a list.
    message_sizes = ",".join(message_sizes)
    print(message_sizes)

    # Convert int elements of list to str, as pbench-uperf is a shell script.
    instances = job_content["instances"]
    instances = [str(x) for x in instances]
    # Type of instances is a list.
    instances = ",".join(instances)
    print(instances)

    nr_samples = job_content["nr_samples"]
    print(nr_samples)

    max_failures = job_content["max_failures"]
    print(max_failures)

    maxstddevpct = job_content["maxstddevpct"]
    print(maxstddevpct)

    return protocols, config, test_types, runtime, message_sizes, instances, nr_samples, max_failures, maxstddevpct


# Define three test suites for pbench-uperf-quick-tests.
def test_suites(test_suite_name):
    protocols, config, test_types, runtime, message_sizes, instances, nr_samples, max_failures, maxstddevpct = get_yaml(file_name)

    if test_suite_name == "lite":
        print("INFO: Run pbench-uperf with lite test suite.")
        protocols = "tcp,udp"
        test_types = "stream,rr"
        instances = "1,8"
        runtime = 20
        message_sizes = "1,64"
        nr_samples = 2
        max_failures = 3
        maxstddevpct = 2
    elif test_suite_name == "default":
        print("INFO: Run pbench-uperf with default test suite.")
        protocols = "tcp,udp"
        test_types = "stream,maerts,rr"
        instances = "1,8,64"
        runtime = 30
        message_sizes = "1,64,16384"
        nr_samples = 3
        max_failures = 4
        maxstddevpct = 3
    elif test_suite_name == "full":
        print("INFO: Run pbench-uperf with full test suite.")
        protocols = "tcp,udp"
        test_types = "stream,maerts,bidirec,rr"
        instances = "1,8,64"
        runtime = 60
        message_sizes = "1,64,1024,16384"
        nr_samples = 5
        max_failures = 6
        maxstddevpct = 5
    else:
        print("ERROR: Incorrect test suite name.")
        return False

    return protocols, config, test_types, runtime, message_sizes, instances, nr_samples, max_failures, maxstddevpct


# Function to execute pbench-uperf command
def run(server_ip, client_ip, protocols, config, test_types, runtime, message_sizes, instances, nr_samples, max_failures, maxstddevpct):

    command = "pbench-uperf "
    command += "-S {} ".format(server_ip)
    command += "-C {} ".format(client_ip)
    command += "-c {} ".format(config)
    command += "-t {} ".format(test_types)
    command += "-r {} ".format(runtime)
    command += "-m {} ".format(message_sizes)
    command += "-p {} ".format(protocols)
    command += "-i {} ".format(instances)
    command += "--samples={} ".format(nr_samples)
    command += "--max-failures={} ".format(max_failures)
    command += "--max-stddev={} ".format(maxstddevpct)
    print("DEBUG: command:", command)

    ret = subprocess.run(commands, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
    # Store ret.stdout to a file.


# Make the function of cli to a command line mode with the click module.
@click.command()
@click.argument("server_ip")
@click.argument("client_ip")
@click.argument("config")
@click.option("--test_suite", help = "Includes full, default, lite")
@click.option("--protocols", help = "Includes tcp / udp(default is $protocols).")
@click.option("--test_types", help = "Includes stream, maerts, bidirec, rr(default $test_types).")
@click.option("--runtime", type=int, help = "Test period in seconds(default is $runtime).")
@click.option("--message_sizes", help = "Message sizes in bytes(default is $message_sizes).")
@click.option("--instances", help = "Numbers of uperf instances(default is $instances).")
@click.option("--nr_samples", help = "Numbers of times each different tests.")
@click.option("--max_failures", help = "Maximum numbers of failures to get below stddev.")
@click.option("--maxstddevpct", help = "Maximum percent stddev allowed to pass.")
def cli(client_ip, server_ip, test_suite, config, protocols, test_types, runtime, message_sizes, instances, nr_samples, max_failures, maxstddevpct):
    # Arguments.
    server_ip = server_ip
    client_ip = client_ip
    config = config
    # Options.
    test_suite = test_suite
    protocols = protocols
    test_types = test_types
    runtime = runtime
    message_sizes = message_sizes
    instances = instances
    nr_samples = nr_samples
    max_failures = max_failures
    maxstddevpct = maxstddevpct

    # List opt to store options(-S -C...) if parameters isn't None.
    opt = []
    # List para to store parameters if it isn't None.
    para = []

    # Here, filter function is better.
    if test_suite == None:
        print("INFO: Run pbench-uperf with user's parameters defined.")

        if protocols != None:
            opt.append("-p")
            para.append(protocols)
        if test_types != None:
            opt.append("-t")
            para.append(test_types)
        if runtime != None:
            opt.append("-r")
            para.append(runtime)
        if message_sizes != None:
            opt.append("-m")
            para.append(message_sizes)
        if instances != None:
            opt.append("-i")
            para.append(instances)
        if nr_samples != None:
            opt.append("--samples")
            para.append(nr_samples)
        if max_failures != None:
            opt.append("--max_failures")
            para.append(max_failures)
        if maxstddevpct != None:
            opt.append("--maxstddevpct")
            para.append(maxstddevpct)
        print("DEBUG: opt", opt)
        print("DEBUG: para", para)
        
        # Generate commands when user defines parameters.
        command = "pbench-uperf -S " + server_ip
        command += " -C " + client_ip
        command += " --config " + config
        for i in range(len(opt)):
            command += " " + opt[i] + " " + para[i]
        print("DEBUG: command", command)

        # Run command.
        ret = subprocess.run(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8")
    else:
        print("INFO: Use a test suite to start pbench-uperf, will ignore others parameters in cmdline.")

        # Function test_suites updated parts of parameters when user use --test_types.
        protocols, config, test_types, runtime, message_sizes, instances, nr_samples, max_failures, maxstddevpct = test_suites(test_suite)
        
        # Run command.
        run(server_ip, client_ip, protocols, config, test_types, runtime, message_sizes, instances, nr_samples, max_failures, maxstddevpct)


if __name__ == "__main__":
    cli()
