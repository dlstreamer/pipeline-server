'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: MIT License
'''

import subprocess
import time
import os

class TestLvaMultipleClients:
    def teardown_method(self, test_method):
        if self.server_process is not None:
            self.server_process.kill()

    def test_multiple_clients(self, sleep_period=0.25, port=5001, max_running_pipelines=10):
        server_args = ["python3", "/home/video-analytics-serving/samples/lva_ai_extension/server", "-p", str(port)]
        print(' '.join(server_args))
        self.server_process = subprocess.Popen(server_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        bufsize=1, universal_newlines=True)
        time.sleep(sleep_period)

        client_args = ["python3", "/home/video-analytics-serving/samples/lva_ai_extension/client",
                    "-s", "127.0.0.1:" + str(port),
                    "-f", "/home/video-analytics-serving/samples/lva_ai_extension/sampleframes/sample01.png"]
        print(' '.join(client_args))
        client_process_list = []
        for _ in range(max_running_pipelines):
            client_process = subprocess.Popen(client_args, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE, bufsize=1,
                                            universal_newlines=True)
            client_process_list.append(client_process)
        print(client_process_list)
        client_process_list[-1].poll()
        elapsed_time = 0
        while client_process_list[-1].returncode is None and elapsed_time < 60:
            time.sleep(sleep_period)
            elapsed_time += sleep_period
            client_process_list[-1].poll()
        assert client_process_list[-1].returncode is not None
        assert client_process_list[-1].returncode == 0
        print("Elapsed time = {}s".format(elapsed_time))
