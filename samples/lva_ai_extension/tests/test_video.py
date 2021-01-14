 
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
import pytest

from jsonschema import validate

class TestLvaVideo:
    def teardown_method(self, test_method):
        server_process = getattr(self, "server_process", None)
        if server_process is not None:
            server_process.kill()

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
        assert client_process.returncode is not None
        assert client_process.returncode == 0

    def validate_output(self, output_location):
        json_schema = None
        json_schema_file = os.path.join(os.path.dirname(__file__), 'common/Extension_Data_Schema.json')
        with open(json_schema_file, "r") as read_file:
            json_schema = json.load(read_file)

        #Read each inference result and compare against the schema
        with open(output_location, "r") as file:
            for line in file:
                if line and line != '':
                    validate(instance=json.loads(line),schema=json_schema)


    def _download_video(self, uri, target, no_proxy=""):
        if not os.path.isfile(target):
            arguments = ["wget",no_proxy,"-O",target,uri]
            subprocess.run(arguments)
        return os.path.isfile(target)

    @pytest.mark.parametrize("filename", ["classroom.mp4","person-bicycle-car-detection.mp4","person-bicycle-car-detection_1920_1080_2min.mp4"])
    @pytest.mark.parametrize("backend",["CAP_GSTREAMER"])
    def test_opencv(self, filename, backend):
        os.environ["OPENCV_VIDEOIO_DEBUG"] = "1"
        os.environ["OPENCV_VIDEOCAPTURE_DEBUG"] = "1"
        import cv2
        
        print("OpenCV Version: {}".format(cv2.__version__), flush=True)

        if ("2min" in filename):
            assert(self._download_video("https://gitlab.devtools.intel.com/media-analytics-pipeline-zoo/media/-/raw/main/video/person-bicycle-car-detection/{}?inline=false".format(filename),
                                        "/home/video-analytics-serving/{}".format(filename),
                                        "--no-proxy"))
        else:
            assert(self._download_video("https://github.com/intel-iot-devkit/sample-videos/blob/master/{}?raw=true".format(filename),
                                        "/home/video-analytics-serving/{}".format(filename)))

        print("Opening: {}\n".format(filename),flush=True)
        capture = cv2.VideoCapture("/home/video-analytics-serving/{}".format(filename), getattr(cv2,backend))
        assert(capture)
        ret, frame = capture.read()
        assert(ret and frame is not None)


    def test_lva_video_consistent_results(self, sleep_period=0.25, port=5001):
        server_args = ["python3", "/home/video-analytics-serving/samples/lva_ai_extension/server", "-p", str(port)]
        print(' '.join(server_args))
        self.server_process = subprocess.Popen(server_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(sleep_period)

        #Create temporary parameter file
        workdir_path = tempfile.TemporaryDirectory()
        output_file = "output.jsonl"
        output_location1 = os.path.join(workdir_path.name, output_file)
        output_file2 = "output2.jsonl"
        output_location2 = os.path.join(workdir_path.name, output_file2)

        self.run_client(source="/home/video-analytics-serving/person-bicycle-car-detection.mp4",
                        sleep_period=sleep_period,
                        port=port,
                        output_location=output_location1)
        self.run_client(source="/home/video-analytics-serving/person-bicycle-car-detection.mp4",
                        sleep_period=sleep_period,
                        port=port,
                        output_location=output_location2)
        self.validate_output(output_location1)
        self.validate_output(output_location2)

        #Compare the two outputs to see if they match
        json_data1 = None
        json_data2 = None
        count = 0
        with open(output_location1, "r") as file1:
            with open(output_location2, "r") as file2:
                file1_s = file1.readline()
                file2_s = file2.readline()
                while file1_s != '' and file2_s != '':
                    count += 1
                    json_data1 = json.loads(file1_s)
                    json_data2 = json.loads(file2_s)
          
                    assert json_data1 == json_data2

                    file1_s = file1.readline()
                    file2_s = file2.readline()
                if file1_s != '' and file2_s == '':
                    assert False
                if file1_s == '' and file2_s != '':
                    assert False
        print("Got {} results".format(count), flush=True)
        assert (count == 647)
