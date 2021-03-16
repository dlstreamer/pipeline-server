import os
import tempfile
import pytest
import copy
import json
import time


def get_client_execution_time(helpers, client_timing_test_case, loop_count):
    client_test_case = copy.deepcopy(client_timing_test_case)
    client_test_case["params"]["loop_count"] = loop_count
    start_time = time.time()
    helpers.run_client(client_test_case["params"])
    return time.time() - start_time

def get_serial_test_time_1_client(helpers, test_case_client):
    num_of_concurrent_clients = test_case_client.get("num_of_concurrent_clients", 1)
    #If num_of_concurrent_clients is 1, the serial test time is not used
    if num_of_concurrent_clients == 1:
        return 1

    client_timing_test_case = copy.deepcopy(test_case_client)
    #Prime the server to remove possible init delay in response
    get_client_execution_time(helpers, client_timing_test_case, 1)
    #Get time each frame will take on average ignoring init delay
    #Serial time is init time + frame time * num_frames * num_of_concurrent_clients
    num_frames = test_case_client["params"]["loop_count"]
    one_frame_time = get_client_execution_time(helpers, client_timing_test_case, 1)
    multi_frame_time = get_client_execution_time(helpers, client_timing_test_case, num_frames)
    client_frame_time = (multi_frame_time - one_frame_time) / (num_frames - 1)
    client_init_time = one_frame_time - client_frame_time
    print("Client execution times: 1 frame = {}, {} frames = {}".format(one_frame_time, num_frames, multi_frame_time))
    print("Client execution times: init = {}, frame = {}".format(client_init_time, client_frame_time))
    serial_test_time = client_init_time + num_of_concurrent_clients * num_frames * client_frame_time
    return serial_test_time

def test_pipeline_execution_positive(helpers, test_case, test_filename, generate):
    #Create copy of test case to create the generated file
    _test_case = copy.deepcopy(test_case)

    helpers.run_server(test_case["server_params"])

    #Create temporary directory for saving output
    workdir_path = tempfile.TemporaryDirectory()
    output_locations = []
    proc_list = []
    counter = 0

    # num_of_concurrent_clients is used for checking pipelines run concurrently
    # because of behavior of test checking serial runtime, this is difficult to
    num_of_concurrent_clients = 0
    for client in test_case["client"]:
        num_of_concurrent_clients += client.get("num_of_concurrent_clients", 1)

    overall_test_time = 0
    # If multiple pipelines defined in test case, calculate serial test time individually
    if len(test_case["client"]) > 1:
        for client in test_case["client"]:
            loop_count = 1
            if (".jpg" in client["params"]["source"]) or (".png" in client["params"]["source"]):
                loop_count = 10
            overall_test_time += get_client_execution_time(helpers, client, loop_count)
    else:
        overall_test_time = get_serial_test_time_1_client(helpers, test_case["client"][0])

    # Start clients
    for client in test_case["client"]:
        for _ in range(client.get("num_of_concurrent_clients", 1)):
            output_file = "output" + str(counter) + ".jsonl"
            counter += 1
            output_location = os.path.join(workdir_path.name, output_file)
            output_locations.append(output_location)
            client["params"]["output_location"] = output_location
            p = helpers.run_client(client["params"], num_of_concurrent_clients > 1)
            proc_dict = { "process": p, "expected_return_code": client["params"].get("expected_return_code", 0)}
            proc_list.append(proc_dict)

    # Monitor number of running clients, wait for them all finish
    # TODO: Add timeout
    start_time = time.time()
    # Ensure the while loop doesn't hang if processes hang
    end_time = start_time + (overall_test_time * 2)
    sleep_duration = 0.25
    num_clients_running = num_of_concurrent_clients
    all_clients_running_count = 0
    while num_clients_running > 0 and time.time() < end_time:
        num_clients_running = 0
        for proc_dict in proc_list:
            proc_dict["process"]
            if proc_dict["process"].poll() is None:
                num_clients_running+=1
            else:
                assert proc_dict["process"].returncode == proc_dict["expected_return_code"]
        if num_clients_running == num_of_concurrent_clients:
            all_clients_running_count+=1
        time.sleep(sleep_duration)
    concurrent_client_running_time =  time.time() - start_time

    for proc_dict in proc_list:
        if proc_dict["process"].poll() is None:
            proc_dict["process"].kill()

    # Test concurrency - do all clients run concurrently or serially?
    # If max_running_pipelines == 1 we expect serial operation
    if num_of_concurrent_clients > 1:
        print("Client execution test time {}s. All clients running for {}s".format(overall_test_time, concurrent_client_running_time))
        run_to_run_variance = 1.0
        if test_case["server_params"]["max_running_pipelines"] > 1:
            assert concurrent_client_running_time < overall_test_time, "Clients not running concurrently"
        else:
            assert (overall_test_time - concurrent_client_running_time) < run_to_run_variance, "Clients not running serially"

    for output_file in output_locations:
        helpers.validate_output_against_schema(output_file)

    if test_case["golden_results"]:
        results = []
        for output_file in output_locations:
            helpers.get_results_from_file(output_file, results)
        if generate:
            _test_case["results"] = results
            with open(test_filename+'.generated', "w") as test_output:
                json.dump(_test_case, test_output, indent=4)
        else:
            assert helpers.cmp_results(results, test_case["results"],
                                       test_case["numerical_tolerance"]), "Inference result mismatch"
