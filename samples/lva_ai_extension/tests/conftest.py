import sys
import subprocess
import select
import time
import os
import json
import pytest

from jsonschema import validate
from collections.abc import Mapping

class Helpers:
    def __init__(self):
        self.server_process = None
        self.client_process = None
        self.poll = None
        self.start_time = time.time()

    def run_server(self, params, capture_log = False):
        server_args = ["python3", "/home/video-analytics-serving/samples/lva_ai_extension/server", "-p", str(params["port"])]
        if params.get("pipeline"):
            pipeline = params["pipeline"]
            if pipeline.get("name"):
                server_args.extend(["--pipeline-name", pipeline["name"]])
            if pipeline.get("version"):
                server_args.extend(["--pipeline-version", pipeline["version"]])
        server_args.extend(["--max-running-pipelines", str(params.get("max_running_pipelines", 10))])
        print(' '.join(server_args))
        self.server_process = subprocess.Popen(server_args,
                                               bufsize=0,
                                               stdout=params.get("stdout",None),
                                               stderr=params.get("stderr", subprocess.PIPE if capture_log else None))
        time.sleep(params.get("sleep_period",0.25))
        if capture_log:
            self.poll = select.poll()
            self.poll.register(self.server_process.stderr, select.POLLIN)
        return self.server_process

    def get_server_log_message(self):
        if self.poll and self.poll.poll(0):
            try:
                line = self.server_process.stderr.readline()
                log_message = json.loads(line)
                if "levelname" in log_message and "message" in log_message:
                    return log_message["message"]
            except ValueError:
                pass
        return None

    def get_server_log_messages(self):
        lines = []
        line = self.get_server_log_message()
        while line is not None:
            lines.append(line)
            line = self.get_server_log_message()
        return lines

    def run_client(self, params, asynchronous=False):
        client_args = ["python3", "/home/video-analytics-serving/samples/lva_ai_extension/client",
                    "-s", "127.0.0.1:" + str(params["port"]),
                    "-l", str(params.get("loop_count", 1)),
                    "-f", params["source"]]
        if params.get("pipeline"):
            pipeline = params["pipeline"]
            if pipeline.get("name"):
                client_args.extend(["--pipeline-name", pipeline["name"]])
            if pipeline.get("version"):
                client_args.extend(["--pipeline-version", pipeline["version"]])
            if pipeline.get("parameters"):
                if isinstance(pipeline["parameters"], Mapping):
                    pipeline["parameters"] = json.dumps(pipeline["parameters"])
                client_args.extend(["--pipeline-parameters", pipeline["parameters"]])
        if params.get("shared_memory", False):
            client_args.append("-m")
        if params.get("output_location"):
            client_args.extend(["-o", params["output_location"]])
        print(' '.join(client_args))
        self.client_process = subprocess.Popen(client_args,
                                               stdout=params.get("stdout",None),
                                               stderr=params.get("stderr",None))
        if not asynchronous:
            self.client_process.wait()
            assert self.client_process.returncode == params.get("expected_return_code", 0)
        return self.client_process

    def remove_empty_lists(self, dictionary):
        if not isinstance(dictionary, (dict, list)):
            return dictionary
        if isinstance(dictionary, list):
            return [v for v in (self.remove_empty_lists(v) for v in dictionary) if v or v == 0]
        return {k: v for k, v in ((k, self.remove_empty_lists(v)) for k, v in dictionary.items()) if v or v == 0}

    def validate_output_against_schema(self, output_location):
        json_schema = None
        json_schema_file = os.path.join(os.path.dirname(__file__), 'common/Extension_Data_Schema.json')
        with open(json_schema_file, "r") as read_file:
            json_schema = json.load(read_file)

        #Read each inference result and compare against the schema
        with open(output_location, "r") as file_:
            for line in file_:
                if line and line != '':
                    dictionary = json.loads(line)
                    dictionary = self.remove_empty_lists(dictionary)
                    if dictionary.get("inferences"):
                        for inference in dictionary["inferences"]:
                            inference["type"] = inference["type"].lower()
                    validate(instance=dictionary,schema=json_schema)

    def get_results_from_file(self, output_location):
        results = []
        with open(output_location) as results_file:
            for x in results_file:
                if len(x.strip()) != 0:
                    results.append(json.loads(x))
        return results

    def cmp_results(self, measured, expected, tolerance):
        if measured == expected:
            return True

        assert type(measured) == type(expected), "Type Comparison Mismatch"

        if isinstance(measured, int) or isinstance(measured, float):
            if expected != 0:
                msg = "Measured Value {} not within tolerance ({}) of Expected Value {}"
                assert  (abs(measured-expected) / abs(expected)) < tolerance, \
                msg.format(measured, tolerance, expected)
            else:
                msg = "Measured Value {} not within tolerance ({}) of Expected Value {}"
                assert tolerance > 1, \
                msg.format(measured, tolerance, expected)

            return True

        if isinstance(measured, list):
            assert len(measured) == len(expected), "List length not equal"

            for measured1, expected1 in zip(measured, expected):
                assert self.cmp_results(measured1, expected1, tolerance), "List items not equal"
            return True

        if isinstance(measured, dict):
            assert len(measured) == len(expected), "Dictionary length not equal"
            for key in measured:
                assert key in expected, "Dictionary keys not equal"
                if key.endswith("id"):
                    assert measured[key] == expected[key], "{} doesn't match".format(key)
                    return True
                assert self.cmp_results(measured[key], expected[key], tolerance), "Dictionaries not equal"
            return True

        assert measured == expected, "Values not equal"
        return True

    def cleanup_processes(self):
        if self.server_process is not None:
            self.server_process.kill()

@pytest.fixture
def helpers():
    helper = Helpers()
    yield helper
    helper.cleanup_processes()

def pytest_addoption(parser):
    parser.addoption("--generate", action="store_true", help="generate expected results",
                     default=False)
    parser.addoption("--cpu", action="store_true", help="Run CPU tests",
                     default=True)
    parser.addoption("--no-cpu", action="store_false", dest='cpu', help="Disable CPU tests")
    parser.addoption("--gpu", action="store_true", help="Run GPU tests",
                     default=False)
    parser.addoption("--myriad", action="store_true", help="Run MYRIAD tests",
                     default=False)


#Parse the test_cases folder to load config files for parameterizing tests and checking results
def load_test_cases(metafunc, directory):
    dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_cases", directory)
    list_of_dir_paths = [dir_path]

    filenames = []
    if metafunc.config.getoption("cpu"):
        cpu_path = os.path.join(dir_path, "cpu")
        if os.path.isdir(cpu_path):
            list_of_dir_paths.append(cpu_path)
    if metafunc.config.getoption("gpu"):
        gpu_path = os.path.join(dir_path, "gpu")
        if os.path.isdir(gpu_path):
            list_of_dir_paths.append(gpu_path)

    if metafunc.config.getoption("myriad"):
        gpu_path = os.path.join(dir_path, "myriad")
        if os.path.isdir(gpu_path):
            list_of_dir_paths.append(gpu_path)

    for path in list_of_dir_paths:
        dir_filenames = [(os.path.abspath(os.path.join(path, fn)),
                           os.path.splitext(fn)[0]) for fn in os.listdir(path)
                           if os.path.isfile(os.path.join(path, fn)) and
                           os.path.splitext(fn)[1] == '.json']
        filenames.extend(dir_filenames)
    test_cases = []
    test_names = []
    generate = metafunc.config.getoption("generate")
    for filepath, testname in filenames:
        try:
            with open(filepath) as json_file:
                test_cases.append((json.load(json_file), filepath, generate))
                test_names.append(testname)
        except Exception as error:
            print(error)
            assert False, "Error Reading Test Case"
    return (test_cases, test_names)

def pytest_generate_tests(metafunc):
    if "pipeline_execution_positive" in metafunc.function.__name__:
        test_cases, test_names = load_test_cases(metafunc, "pipeline_execution_positive")
        metafunc.parametrize("test_case,test_filename,generate", test_cases, ids=test_names)

