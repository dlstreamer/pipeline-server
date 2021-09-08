## Using gRPC Server
To build and run the server, open a terminal and issue these commands:
```
../docker/build.sh
../docker/run_server.sh
```

To confirm connectivity to the server, open a second terminal and run the gRPC client:
```
../docker/run_client.sh
[AIXC] [MainThread  ] [INFO]: =======================
[AIXC] [MainThread  ] [INFO]: Options for __main__.py
[AIXC] [MainThread  ] [INFO]: =======================
<snip>
[AIXC] [MainThread  ] [INFO]: Client finished execution
```

Refer to [Documentation here](../README.md#running-the-edge-ai-extension-module) for more details and settings.
