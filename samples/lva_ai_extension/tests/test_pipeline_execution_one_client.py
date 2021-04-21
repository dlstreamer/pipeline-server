import os
import tempfile
import pytest
import copy
import json
import time
import cv2

def test_pipeline_execution_one_client(helpers, test_case, test_filename, generate):
    #Create copy of test case to create the generated file
    _test_case = copy.deepcopy(test_case)
    helpers.run_server(test_case["server_params"])

    #Create temporary directory for saving output
    workdir_path = tempfile.TemporaryDirectory()
    output_file = None

    if not "client" in test_case:
        assert False, "Invalid test"

    # Start client
    client_params = test_case["client"]["params"]
    output_file = os.path.join(workdir_path.name, "output_one_client.jsonl")
    client_params["output_location"] = output_file
    process = helpers.run_client(client_params, True)
    time.sleep(client_params["sleep_period"])
    expected_return_code = client_params.get("expected_return_code", 0)

    rtsp = client_params.get("rtsp", None)
    if rtsp:
        url = rtsp["url"]
        port = rtsp["port"]
        frame_destination = client_params["pipeline"]["frame-destination"]
        if frame_destination.get("type") == "rtsp":
            rtsp_path = frame_destination.get("path")
            rtsp_url = "{}:{}/{}".format(url, port, rtsp_path)
            print("Reading frame from %s", rtsp_url)
            cap = cv2.VideoCapture(rtsp_url, cv2.CAP_GSTREAMER)
            ret, frame = cap.read()
            cap.release()
            assert ret, "Unable to read RTSP frame"
            assert frame.size > 0 , "Unable to read RTSP frame"

    if client_params["wait_to_complete"]:
        process.wait()
    elif process.poll() is None:
        process.kill()

    assert process.returncode == expected_return_code

    if output_file:
        helpers.validate_output_against_schema(output_file)