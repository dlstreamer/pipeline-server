import os
import tempfile
import pytest
import copy
import json

from multiprocessing import Process

def test_pipeline_execution_positive(helpers, test_case, test_filename, generate):
    #Create copy of test case to create the generated file
    _test_case = copy.deepcopy(test_case)

    helpers.run_server(test_case["server_params"])

    #Create temporary directory for saving output
    workdir_path = tempfile.TemporaryDirectory()

    output_locations = []
    proc = []
    counter = 0
    for _ in range(test_case["num_of_concurrent_clients"]):
        output_file = "output" + str(counter) + ".jsonl"
        counter += 1
        output_location = os.path.join(workdir_path.name, output_file)
        output_locations.append(output_location)
        test_case["client_params"]["output_location"] = output_location
        p = Process(target=helpers.run_client(test_case["client_params"]))
        p.start()
        proc.append(p)
    for p in proc:
        p.join()

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
