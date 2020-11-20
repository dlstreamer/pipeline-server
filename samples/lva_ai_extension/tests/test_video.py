 
'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: MIT License
'''

import subprocess
import time
import os
import json
import tempfile

class TestLvaVideo:
    def setup_method(self, test_method):
        server_args = [ "python3", "/home/video-analytics-serving/samples/lva_ai_extension/server", "-p", str(5001)]
        print(' '.join(server_args))
        self.server_process = subprocess.Popen(server_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.25)

    def teardown_method(self, test_method):
        self.server_process.kill()

    def test_lva_video(self, sleep_period=0.25):
        #Create temporary parameter file
        workdir_path = tempfile.TemporaryDirectory()
        output_file1 = "output1.jsonl"
        output_file2 = "output2.jsonl"
        output_location1 = os.path.join(workdir_path.name, output_file1)
        output_location2 = os.path.join(workdir_path.name, output_file2)

        client1_args = [ "python3", "/home/video-analytics-serving/samples/lva_ai_extension/client", "-s", "127.0.0.1:" + str(5001), "-f", "/home/video-analytics-serving/classroom.mp4", "-m", "-o", output_location1]
        client2_args = [ "python3", "/home/video-analytics-serving/samples/lva_ai_extension/client", "-s", "127.0.0.1:" + str(5001), "-f", "/home/video-analytics-serving/classroom.mp4", "-m", "-o", output_location2]
        print(' '.join(client1_args))

        client_process1 = subprocess.Popen(client1_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        client_process1.poll()
        elapsed_time = 0
        while client_process1.returncode is None and elapsed_time < 300:
            time.sleep(sleep_period)
            elapsed_time += sleep_period
            client_process1.poll()
        assert client_process1.returncode is not None
        assert client_process1.returncode == 0

        client_process2 = subprocess.Popen(client2_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        client_process2.poll()
        elapsed_time = 0
        while client_process2.returncode is None and elapsed_time < 300:
            time.sleep(sleep_period)
            elapsed_time += sleep_period
            client_process2.poll()
        assert client_process2.returncode is not None
        assert client_process2.returncode == 0

        #Read the first inference result from the first client
        json_data1 = None
        json_data2 = None
        with open(output_location1, "r") as file1:
            with open(output_location2, "r") as file2:
                file1_s = file1.readline()
                file2_s = file2.readline()
                while file1_s != '' and file2_s != '':
                    json_data1 = json.loads(file1_s)
                    json_data2 = json.loads(file2_s)

                    assert json_data1 == json_data2

                    file1_s = file1.readline()
                    file2_s = file2.readline()
                if file1_s != '' and file2_s == '':
                    assert False
                if file1_s == '' and file2_s != '':
                    assert False

