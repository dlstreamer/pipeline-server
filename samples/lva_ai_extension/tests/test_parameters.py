'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: MIT License
'''

import subprocess
import time
import os
import tempfile

def parameter_run_client_server(port, loops, sleep_period, parameters):
    if not os.getenv('PIPELINE_NAME') and not os.getenv('PIPELINE_VERSION'):
        print("LVA environment not detected, skipping test")
        return
    server_args = ["python3", "/home/video-analytics-serving/samples/lva_ai_extension/server",
                   "-p", str(port), "--parameters", parameters]
    client_args = ["python3", "/home/video-analytics-serving/samples/lva_ai_extension/client",
                   "-s", "127.0.0.1:" + str(port), "-l", str(loops),
                   "-f", "/home/video-analytics-serving/samples/lva_ai_extension/sampleframes/sample01.png"]
    print(' '.join(server_args))
    server_process = subprocess.Popen(server_args, stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                      bufsize=1, universal_newlines=True)
    time.sleep(sleep_period)
    print(' '.join(client_args))
    client_process = subprocess.Popen(client_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      bufsize=1, universal_newlines=True)
    client_process.poll()
    elapsed_time = 0
    while client_process.returncode is None and elapsed_time < 5:
        #print(client_process.stdout.readline())
        time.sleep(sleep_period)
        elapsed_time += sleep_period
        client_process.poll()
    assert client_process.returncode is not None
    assert client_process.returncode == 0
    print("Elapsed time = {}s".format(elapsed_time))
    server_process.kill()

def test_lva_parameter_string_argument(port=5001, loops=10, sleep_period=0.25,
                                       parameter_string="{\"device\":\"CPU\"}"):
    parameter_run_client_server(port, loops, sleep_period, parameter_string)

def test_lva_parameter_file_argument(port=5001, loops=10, sleep_period=0.25):
    #Create temporary parameter file
    workdir_path = tempfile.TemporaryDirectory()
    parameter_path = os.path.join(workdir_path.name, "parameters.json")
    with open(parameter_path, "w") as parameter_file:
        parameter_file.write("{\"device\":\"CPU\"}")

    parameter_run_client_server(port, loops, sleep_period, parameter_path)

if __name__ == "__main__":
    test_lva_parameter_string_argument()
    test_lva_parameter_file_argument()
