
Use --entrypoint-args to specify pytest arguments. e.g.

./run.sh --entrypoint-args "-k test_lva_parameter_string_argument"

To run a specific test from the test case

./run.sh --entrypoint-args "-k test_pipeline_execution_positive[object_tracking_person_vehicle_bike_tracking_cpu]"

By default only CPU tests will run. --gpu adds GPU tests. --myriad adds NCS2 tests. --no-cpu excludes cpu tests.

