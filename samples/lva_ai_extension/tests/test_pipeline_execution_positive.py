import os
import tempfile
import pytest
import copy
import json
import time


def get_client_execution_time(helpers, client_timing_test_case, num_frames):
    client_timing_test_case["loop_count"] = num_frames
    start_time = time.time()
    helpers.run_client(client_timing_test_case)
    return time.time() - start_time

def get_serial_test_time(helpers, test_case):
    if test_case["num_of_concurrent_clients"] == 1:
        return 1
    client_timing_test_case = copy.deepcopy(test_case["client_params"])
    # In case this is the first test, prime the server to remove possible init delay in response
    get_client_execution_time(helpers, client_timing_test_case, 1)
    num_frames = test_case["client_params"]["loop_count"]
    one_frame_time = get_client_execution_time(helpers, client_timing_test_case, 1)
    multi_frame_time = get_client_execution_time(helpers, client_timing_test_case, num_frames)
    client_frame_time = (multi_frame_time - one_frame_time) / (num_frames - 1)
    client_init_time = one_frame_time - client_frame_time
    print("Client execution times: 1 frame = {}, {} frames = {}".format(one_frame_time, num_frames, multi_frame_time))
    print("Client execution times: init = {}, frame = {}".format(client_init_time, client_frame_time))
    serial_test_time = client_init_time + test_case["num_of_concurrent_clients"] * num_frames * client_frame_time
    return serial_test_time

def test_pipeline_execution_positive(helpers, test_case, test_filename, generate):
    #Create copy of test case to create the generated file
    _test_case = copy.deepcopy(test_case)

    helpers.run_server(test_case["server_params"])

    #Create temporary directory for saving output
    workdir_path = tempfile.TemporaryDirectory()
    output_locations = []
    proc = []
    counter = 0

    num_of_concurrent_clients = test_case["num_of_concurrent_clients"]
    overall_test_time = get_serial_test_time(helpers, test_case)

    # Start clients
    for _ in range(num_of_concurrent_clients):
        output_file = "output" + str(counter) + ".jsonl"
        counter += 1
        output_location = os.path.join(workdir_path.name, output_file)
        output_locations.append(output_location)
        test_case["client_params"]["output_location"] = output_location
        p = helpers.run_client(test_case["client_params"], test_case["num_of_concurrent_clients"] > 1)
        proc.append(p)

    # Monitor number of running clients, wait for them all finish
    # TODO: Add timeout
    start_time = time.time()
    end_time = start_time + overall_test_time
    sleep_duration = 0.25
    num_clients_running = num_of_concurrent_clients
    all_clients_running_count = 0
    while num_clients_running > 0 and time.clock() < end_time:
        num_clients_running = 0
        for p in proc:
            if p.poll() is None:
                num_clients_running+=1
            else:
                assert p.returncode == test_case["client_params"]["expected_return_code"]
        if num_clients_running == num_of_concurrent_clients:
            all_clients_running_count+=1
        time.sleep(sleep_duration)
    concurrent_client_running_time =  time.time() - start_time

    # Test concurrency - do all clients run concurrently or serially?
    # If max_running_pipelines == 1 we expect serial operation
    if num_of_concurrent_clients > 1:
        print("Client execution test time {}s. All clients running for {}s".format(overall_test_time, concurrent_client_running_time))
        for p in proc:
            if p.poll() is None:
                p.kill()
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
