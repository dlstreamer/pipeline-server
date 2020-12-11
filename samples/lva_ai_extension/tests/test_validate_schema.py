import subprocess
import time
import os
import json
import tempfile

from jsonschema import validate

class TestLvaValidate:
    def teardown_method(self, test_method):
        if self.server_process is not None:
            self.server_process.kill()

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

    def test_lva_validate_schema(self, sleep_period=0.25, port=5001):
        server_args = ["python3", "/home/video-analytics-serving/samples/lva_ai_extension/server", "-p", str(port)]
        print(' '.join(server_args))
        self.server_process = subprocess.Popen(server_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        bufsize=1, universal_newlines=True)
        time.sleep(sleep_period)

        #Create temporary parameter file
        workdir_path = tempfile.TemporaryDirectory()
        output_file = "output.jsonl"
        output_location = os.path.join(workdir_path.name, output_file)

        self.run_client(source="/home/video-analytics-serving/samples/lva_ai_extension/sampleframes/sample01.png",
                        sleep_period=sleep_period,
                        port=port,
                        output_location=output_location,
                        timeout=5)
        self.validate_output(output_location)
