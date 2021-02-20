## Overview
Tests are written using [pytest](https://docs.pytest.org/en/stable/).

Most test cases are driven by a JSON file. Here is an example for a `pipeline_execution_positive` test case. Client arguments are set by the test case and it issues the resulting request to server. Successful client exit is checked and inference results are optionally compared to ground truth files.

```json
{
    "server_params": {
        "pipeline_name":"object_classification",
        "pipeline_version":"vehicle_attributes_recognition",
        "pipeline_parameters": {
            "detection-device": "CPU",
            "classification-device":"CPU"
            },
        "sleep_period":0.25,
        "port":5001
    },
    "client_params": {
        "source":"/home/video-analytics-serving/samples/lva_ai_extension/sampleframes/sample01.png",
        "output_location":"",
        "shared_memory":true,
        "loop_count":1,
        "sleep_period":0.25,
        "port":5001,
        "timeout":300,
        "expected_return_code":0
    },
    "num_of_concurrent_clients":1,
    "golden_results":false
}
```
## Usage
To list all tests run the following
```
$ ./run.sh --entrypoint-args "--collect-only"
<snip>
collected 11 items
<Module tests/test_nonexistant_source.py>
  <Function test_lva_nonexistant_source>
<Module tests/test_parameters.py>
  <Function test_lva_parameter_string_argument>
  <Function test_lva_parameter_file_argument>
<Module tests/test_pipeline_execution_positive.py>
  <Function test_pipeline_execution_positive[object_detection_person_vehicle_bike_detection_cpu_video_golden_truth]>
  <Function test_pipeline_execution_positive[object_tracking_person_vehicle_bike_tracking_cpu]>
  <Function test_pipeline_execution_positive[object_detection_person_vehicle_bike_detection_cpu_serial_clients]>
  <Function test_pipeline_execution_positive[object_detection_person_vehicle_bike_detection_cpu_multiple_clients]>
  <Function test_pipeline_execution_positive[object_detection_person_vehicle_bike_detection_cpu_video]>
  <Function test_pipeline_execution_positive[object_classification_vehicle_attributes_recognition_cpu_video_golden_truth]>
  <Function test_pipeline_execution_positive[object_tracking_person_vehicle_bike_tracking_cpu_video_golden_truth]>
  <Function test_pipeline_execution_positive[object_classification_vehicle_attributes_recognition_cpu]>
```

To run a subset of tests use `-k` argument
```
$ ./run.sh --entrypoint-args "-k test_pipeline_execution_positive"
```

To run a specific test case
```
$ ./run.sh --entrypoint-args "-k test_pipeline_execution_positive[object_tracking_person_vehicle_bike_tracking_cpu]"
```
## Enable accelerator tests
By default only CPU tests will run. `--gpu` adds GPU tests. `--myriad` adds NCS2 tests. `--no-cpu` excludes cpu tests.

## Concurrent client test
We need to validate that concurrent client requests result in concurrent pipeline execution. This is done by setting `num_of_concurrent_clients` > 1.
The current test is simplistic and only works under the following conditions
1. Only a single client can be specified (test case schema can support a number of clients all with different settings)
2. An image must be used as input media with a loop count of at least 10.
3. A video cannot be specified as input media as it would cause a test failure.

See [object_detection_person_vehicle_bike_detection_cpu_multiple_clients.json](./test_cases/pipeline_execution_positive/cpu/object_detection_person_vehicle_bike_detection_cpu_multiple_clients.json) as a valid example.
