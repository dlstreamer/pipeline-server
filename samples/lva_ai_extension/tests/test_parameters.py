'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: MIT License
'''

import subprocess
import time
import os
import tempfile

class TestLvaParameters:
    def teardown_method(self, test_method):
        if self.server_process is not None:
            self.server_process.kill()

    def parameter_run_client_server(self, sleep_period, port, parameters):
        server_args = ["python3", "/home/video-analytics-serving/samples/lva_ai_extension/server", "-p", str(port),
                "--pipeline-parameters", parameters]
        print(' '.join(server_args))
        self.server_process = subprocess.Popen(server_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(sleep_period)

        client_args = ["python3", "/home/video-analytics-serving/samples/lva_ai_extension/client",
                    "-s", "127.0.0.1:" + str(port),
                    "-f", "/home/video-analytics-serving/samples/lva_ai_extension/sampleframes/sample01.png"]
        print(' '.join(client_args))
        client_process = subprocess.Popen(client_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        bufsize=1, universal_newlines=True)
        client_process.poll()
        elapsed_time = 0
        while client_process.returncode is None and elapsed_time < 5:
            time.sleep(sleep_period)
            elapsed_time += sleep_period
            client_process.poll()
        assert client_process.returncode is not None
        assert client_process.returncode == 0

    def test_lva_parameter_string_argument(self, sleep_period=0.25, port=5001,
                                        parameter_string="{\"device\":\"CPU\"}"):
        self.parameter_run_client_server(sleep_period, port, parameter_string)

    def test_lva_parameter_file_argument(self, sleep_period=0.25, port=5001):
        #Create temporary parameter file
        workdir_path = tempfile.TemporaryDirectory()
        parameter_path = os.path.join(workdir_path.name, "parameters.json")
        with open(parameter_path, "w") as parameter_file:
            parameter_file.write("{\"device\":\"CPU\"}")

        self.parameter_run_client_server(sleep_period, port, parameter_path)
