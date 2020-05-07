# VA Serving Test Listeners

When VA Serving pipelines are initiated their associated output is directly monitored by methods in PyTest tests. If this output is sent to a message bus, the appropriate client is instantiated and subscribes to the designated topic(s). The messages received by the pipeline execution are then compared against assertion files to confirm expectations were met.

The scripts found in this folder are used by Team City build agents to configure and launch message brokers and for troubleshooting on the **host**. These are located here in case developers want to configure local brokers that match CI setup.

Subscribing to the broker in this way, either on the host or from a remote system may facilitate future system level testing. It allows us to monitor messages received by the broker from multiple VA Serving containers, etc.

