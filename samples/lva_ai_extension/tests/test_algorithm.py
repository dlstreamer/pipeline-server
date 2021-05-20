import os
import tempfile
import pytest
import copy
import json
import time
import cv2

def count_events(results, event_type, valid_event_names):
    print("Counting events of type {} with a name in {}".format(event_type, valid_event_names))
    num_events = 0
    total_zone_count = 0
    with open(results, "r") as file_:
        for line in file_:
            if line and line != '':
                result = json.loads(line)
                if result.get('inferences'):
                    for inference in result['inferences']:
                        if inference['type'] == 'EVENT' and inference['subtype'] == event_type:
                            if inference['event']['name'] in valid_event_names:
                                num_events+=1
                                if event_type == "zoneCrossing":
                                    key = "zoneCount"
                                    total_zone_count += int(inference['event']['properties'][key])
                                print(inference)
    return num_events, total_zone_count

def get_event_names(client_params):
    event_parameter_key = client_params["event_parameter"]
    pipeline_parameter = client_params["pipeline"]["parameters"][event_parameter_key]
    key = event_parameter_key.split('-')
    event_parameter_child = key[0] + 's'
    event_parameters = pipeline_parameter[event_parameter_child]
    event_names = []
    for parameter in event_parameters:
        event_names.append(parameter["name"])
    return event_names

def test_algorithm(helpers, test_case, test_filename, generate):
    #Create copy of test case to create the generated file
    _test_case = copy.deepcopy(test_case)
    helpers.run_server(test_case["server_params"])

    workdir_path = tempfile.TemporaryDirectory()
    output_file = None
    client_params = test_case["client"]["params"]
    output_file = client_params["output_location"]
    if not output_file:
        output_file = os.path.join(workdir_path.name, "algo.jsonl")
        client_params["output_location"] = output_file
    if client_params["run"]:
        process = helpers.run_client(client_params, True)
        expected_return_code = client_params.get("expected_return_code", 0)
        assert process.wait() == expected_return_code
    helpers.validate_output_against_schema(output_file)
    valid_event_names = get_event_names(client_params)
    event_count, total_count = count_events(output_file, client_params["expected_event_type"], valid_event_names)
    print("event_count = {}, total_count = {}".format(event_count, total_count))
    assert event_count == client_params["expected_event_count"], "Incorrect number of events detected"
    assert total_count == client_params.get("expected_total_count", 0), "Incorrect total count detected"


