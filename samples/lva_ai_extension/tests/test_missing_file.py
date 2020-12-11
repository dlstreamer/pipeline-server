'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: MIT License
'''

import subprocess
import time
import os

class TestLvaValidate:

    def run_client(self, source, sleep_period = 0.25, port = 5001, output_location = None, shared_memory = True, timeout = 300):
        client_args = ["python3", "/home/video-analytics-serving/samples/lva_ai_extension/client",
                        "-s", "127.0.0.1:" + str(port),
                        "-f", source]
        if shared_memory:
            client_args.append("-m")
        if output_location is not None:
            client_args.append("-o")
            client_args.append(output_location)
        print(' '.join(client_args))
        client_process = subprocess.Popen(client_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        client_process.poll()
        elapsed_time = 0
        while client_process.returncode is None and elapsed_time < timeout:
            time.sleep(sleep_period)
            elapsed_time += sleep_period
            client_process.poll()
        return client_process.returncode

    def test_lva_missing_file(self, sleep_period=0.25, port=5001):
        returnCode = self.run_client(source="/home/video-analytics-serving/samples/lva_ai_extension/sampleframes/nonexistantimage.png",
                        sleep_period=sleep_period,
                        port=port,
                        shared_memory=False)

        assert returnCode is not None
        assert returnCode == 1
