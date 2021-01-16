'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: MIT License
'''

import os
import tempfile

def parameter_run_client_server(helpers, sleep_period, port, parameters):
    server_params = {
        "pipeline_parameters": parameters,
        "sleep_period": sleep_period,
        "port": port
    }

    client_params = {
        "source": "/home/video-analytics-serving/samples/lva_ai_extension/sampleframes/sample01.png",
        "sleep_period": sleep_period,
        "port": port
    }


    helpers.run_server(server_params)
    helpers.run_client(client_params)

def test_lva_parameter_string_argument(helpers, sleep_period=0.25, port=5001,
                                        parameter_string="{\"detection-device\":\"CPU\"}"):
    parameter_run_client_server(helpers, sleep_period, port, parameter_string)

def test_lva_parameter_file_argument(helpers, sleep_period=0.25, port=5001):
    #Create temporary parameter file
    workdir_path = tempfile.TemporaryDirectory()
    parameter_path = os.path.join(workdir_path.name, "parameters.json")
    with open(parameter_path, "w") as parameter_file:
        parameter_file.write("{\"detection-device\":\"CPU\"}")

    parameter_run_client_server(helpers, sleep_period, port, parameter_path)
