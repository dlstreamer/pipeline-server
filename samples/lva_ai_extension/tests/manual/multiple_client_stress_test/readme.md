This manual test is used to check if the server can handle concurrent streams.

To validate, monitor the server logs, most pipelines will be set to 'Running' before any finish.

In the docker folder
./run_server.sh --max-running-pipelines 10

In the tests/manual/multiple_client_stress_test
./run_client_multiple_times.sh
