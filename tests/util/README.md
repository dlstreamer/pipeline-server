# Intel(R) DL Streamer Pipeline Server Test Listeners

When Intel(R) Deep Learning Streamer (Intel(R) DL Streamer) Pipeline Server pipelines are initiated their associated output is directly monitored by methods in PyTest tests. If this output is sent to a message bus, the appropriate client is instantiated and subscribes to the designated topic(s). The messages received by the pipeline execution are then compared against assertion files to confirm expectations were met.

The scripts found in this folder are used by Team City build agents to configure and launch message brokers and for troubleshooting on the **host**. These are located here in case developers want to configure local brokers that match CI setup.
