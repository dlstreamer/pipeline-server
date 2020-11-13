import subprocess
import time
import os
import json
import tempfile

from jsonschema import validate

def test_lva_validate_schema(port=5001, sleep_period=0.25):
    if not os.getenv('PIPELINE_NAME') and not os.getenv('PIPELINE_VERSION'):
        print("LVA environment not detected, skipping test")
        return

    #Create temporary parameter file
    workdir_path = tempfile.TemporaryDirectory()
    output_file = "output.json"
    output_location = os.path.join(workdir_path.name, output_file)
   
    #Run server client to generate a results file
    server_args = [ "python3", "/home/video-analytics-serving/samples/lva_ai_extension/server", "-p", str(port)]
    client_args = [ "python3", "/home/video-analytics-serving/samples/lva_ai_extension/client", "-s", "127.0.0.1:" + str(port), "-l", str(1), "-f", "/home/video-analytics-serving/samples/lva_ai_extension/sampleframes/sample01.png", "-o", output_location]
    print(' '.join(server_args))
    server_process = subprocess.Popen(server_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True)
    time.sleep(sleep_period)
    print(' '.join(client_args))
    client_process = subprocess.Popen(client_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True)
    client_process.poll()
    elapsed_time = 0
    while client_process.returncode is None and elapsed_time < 5:
        time.sleep(sleep_period)
        elapsed_time += sleep_period
        client_process.poll()
    assert client_process.returncode is not None
    assert client_process.returncode == 0

    #Validate the output file against the schema

    json_data = None
    with open(output_location, "r") as read_file:
        json_data = json.load(read_file)
    
    json_schema = None
    json_schema_file = os.path.join(os.path.dirname(__file__), 'common/Extension_Data_Schema.json')
    with open(json_schema_file, "r") as read_file:
        json_schema = json.load(read_file)
    validate(instance=json_data, schema=json_schema)
    
if __name__=="__main__":
    test_lva_validate_schema()

