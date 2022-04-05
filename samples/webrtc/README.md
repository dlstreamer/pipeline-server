# WebRTC Frame Destination

Intel(R) Deep Learning Streamer (Intel(R) DL Streamer) Pipeline Server supports sending media frames to WebRTC peers running on your network. This demonstrates playback within HTML5 video components supported by compatible browsers running anywhere on your network. The use of additional resources and configuration also allows usage beyond your private network - across cloud and public networks.

## Getting Started

The WebRTC sample is comprised of three sample containers that we will run using docker-compose alongside Pipeline Server. The general separation of responsibilities for these microservices are shown below.

![webrtc microservice composition](/docs/images/webrtc_composition.png)

## WebRTC Protocol

[WebRTC](https://opensource.com/article/19/1/gstreamer) brings seamless streaming support from/to web browsers. WebRTC makes use of a set of [communication protocols](https://www.w3.org/TR/webrtc/) _similar_ to [RTSP](/README.md#real-time-streaming-protocol-rtsp).

### WebRTC Signaling Microservice
This sample provides a basic [WebRTC signaling server](https://www.tutorialspoint.com/webrtc/webrtc_signaling.htm) using the starting point provided in [gst-examples](https://gitlab.freedesktop.org/gstreamer/gst-examples/-/blob/master/webrtc/signaling/README.md).
> NOTE: You will need to secure endpoints such as by generating certificates and using secure websocket connections.

### WebRTC Web Server Microservice
This sample provides a basic [WebRTC web server](https://gitlab.freedesktop.org/gstreamer/gst-examples/-/tree/master/webrtc/sendrecv/js) for out-of-the-box runtime compatibility.

### WebRTC Grafana Microservice
This sample provides a container built on top of Grafana. This is used to consolidate multiple requests to the WebRTC Web Server on a single dashboard. In the steps below we will show how to build the Sample Pipeline Server Dashboard from our template and include configuration to automatically load this into the image at runtime using their built-in [Infinity](https://grafana.com/grafana/plugins/yesoreyeram-infinity-datasource/) data source.

## Configuring Client Browser
WebRTC functionality has been validated in Firefox and Chrome browsers on Ubuntu 20.04 hosts with the default Gnome desktop GUI installed. Other browsers are supported through similar updates to configuration. Compatibility checks are available:
* Confirm HTML5 video output compatibility using http://html5test.com/.
* Confirm Browser settings compatibility using https://myownconference.com/blog/en/webrtc/

### Mozilla Firefox
In particular be sure to assign settings by navigating to `about:config`:
1. Confirm `media.peerconnection.enabled` is set to `true`. This is assigned by default.
2. Confirm `media.peerconnection.ice.obfuscate_host_addresses` is set to `false`. This allows successful operation with `http://localhost`.
3. The first time navigating to the site, be sure to click the shield at the left of the address bar in your browser and `Enhanced Tracking Protection` is turned `OFF`.

### Chrome
In particular be sure to assign settings by navigating to `chrome://flags/`:
1. Confirm that `Enable WebRTC actions in Media Session` is set to `Enabled`.
2. Confirm that `Anonymize local IPs exposed by WebRTC` is set to `Disabled`.

## Build All Dependencies

Build the images and launch them as containers in docker-compose.

To do this, open a terminal to the folder where you have cloned Pipeline Server and enter these commands:

```
cd ./samples/webrtc
./build.sh
```

```
Successfully tagged webrtc_signaling_server:latest
<snip>
Successfully tagged webrtc_webserver:latest
<snip>
Successfully tagged webrtc_grafana:latest
<snip>
Successfully tagged dlstreamer-pipeline-server-gstreamer:latest
```

> Note: On subsequent runs you may pass the optional `--remove-volumes` parameter to build.sh. This removes local volumes used to store Grafana runtime information on dashboard panels.

## Run All Microservices

Next we will launch three microservices needed to provide our solution:

```bash
./run.sh
```

```text
Creating network "webrtc_app_network" with driver "bridge"
Creating volume "webrtc_grafana-storage" with local driver
Creating webrtc_webserver ... done
Creating webrtc_signaling_server ... done
Creating webrtc_grafana ... done
Creating pipeline_server  ... done
```

## Launch and Visualize Pipelines

This section provides examples for starting and viewing WebRTC frame output from the localhost using your host's browser.

### Start Pipeline

Starting a  [Pipeline Client](/client/README.md) tool to instruct the `pipeline_server` container running in docker-compose to launch our WebRTC enabled pipeline with web-based input media of a parking lot scene.

```
../../client/pipeline_client.sh start \
   "object_detection/person_vehicle_bike" \
   "https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true" \
   --webrtc-peer-id "pipeline_webrtc1_29442"
```

This produces output:

```
<snip>
Starting pipeline object_detection/person_vehicle_bike, instance = f84ff6b29bfc11ecb4780242ac150004
```

We then construct a URL that includes this same `peer-id` value as supplied in the request. This query parameter allows the `webrtc_webserver` web app to connect to Pipeline Server and render media frames in your browser.

```
http://${HOSTNAME}:8082?destination_peer_id=pipeline_webrtc1_29442
```

> NOTE: The sample web app accepts an _optional_ `instance_id` in case you will be launching a Pipeline Server instance by other means and wish to have the web app independently monitor Pipeline Server instance status otherwise maintain an association with the primary pipeline instance.
   ```
   http://${HOSTNAME}:8082?destination_peer_id=pipeline_webrtc1_29442&instance_id=f84ff6b29bfc11ecb4780242ac150004
   ```

### Example 1: Visualize in web app

The `webrtc_webserver` microservice provides an example that uses WebRTC JavaScript client to connect to Pipeline Server through the `webrtc_signaling` microservice. To get familiar with this web app example, perform these steps:

1. Launch your browser and navigate to the page hosted by the `webrtc_webserver` microservice at http://localhost:8082.

![webrtc web_server](/docs/images/webrtc-launch-pipeline.png)

> NOTE: This web page inherits the hostname specified in the address field with the default port `:8080` as the target address for the `pipeline_server` microservice. You may replace `localhost` with the value from `echo $HOSTNAME` (in a terminal) and navigate to http://$HOSTNAME:8082 in your browser (where $HOSTNAME is the name of your current host).

2. Click `Get Pipelines` to have the web page invoke Pipeline Server's Get Pipelines REST API and populate the dropdown.

3. Choose a value from the dropdown for `Choose Pipeline` and `Choose Media Source` fields. 

4. Provide a unique value for the `Destination Peer ID` and click the `Launch Pipeline` button.

![webrtc launch pipeline](/docs/images/webrtc-pipeline-params3.png)

5. At this point a client is able to begin visualizing the rendered frame output for the launched pipeline via WebRTC. This can be performed now by clicking the Visualize button. Alternately, you may open this page from a browser running on a remote client (at http://$HOSTNAME:8082).

![webrtc visualize local](/docs/images/webrtc-visualize3.png)

> NOTE: If you do not see errors but also are not seeing any stream rendering, confirm `Enhanced Tracking Protection` is turned `OFF` for the site. In Firefox you can do this by navigating to `about:preferences`, search for `Enhanced Tracking Protection` and click the `Manage Exceptions...` button. Confirm the host being used for the `webrtc_webserver` (on port 8082 by default) is on the list of exceptions.

> NOTE: You may optionally expand the "Chosen Pipeline Parameters" and "WebRTC Visualization Parameters" sections to view the relevant parameters that are sent to Pipeline Server's Start Pipeline REST API.

### Initiating More Pipeline Instances

You can disconnect the pipeline and start additional pipelines to visualize directly in same tab. You may also create multiple tabs to produce 3-4 simultaneous streams.

> IMPORTANT: Be certain to assign a unique value to the `Destination Peer ID` _for each request_ or the browser will be unable to connect to the WebRTC stream.

> NOTE: Keep in mind that we need to either wait for the playing stream to exit and disconnect upon completion, or we must manually click the `Disconnect` button beneath it's video player. This will terminate the GStreamer WebRTC Render pipeline. Clicking the `Stop Pipeline` button will ABORT the reference GStreamer pipeline and cause the WebRTC pipeline to cease rendering.

### Example 2: Quick Launch + Visualization in Web App

The `./scripts/start_pipeline.sh` script is provided as a quick way to launch a supported pipeline and render results manually. This prepares a unique `peer-id` and then automatically launches the pipeline and visualization stream (on localhost) when the web page loads.

These scripts launch your host's default browser, which works if compatible with settings applied as explained [above](#configuring_client_browser).

> NOTE: You may optionally pass a `--remote` flag to instruct the script to provide the URL so you can paste in a browser running on a remote system (such as Firefox running on your Windows laptop). However, you must replace `localhost` in the URL with the IP address or fully qualified DNS name (FQDN) for your host.

   ```bash
   ./scripts/start_pipeline.sh --remote
   ```

   ```text
   Paste into browser address field:
   http://pipeline-server.intra.acme.com:8082?destination_peer_id=pipeline_webrtc1_29442&instance_id=36060dc6938c11ec9bfe0242ac140004
   ```

> HINT: You may modify the `scripts/launch_browser.sh` bash script used by start_pipeline.sh so that it provides a suitable FQDN for your host.

> NOTE: When the `instance_id` and `destination_peer_id` query parameters are provided in the URL in addition to the browser address, this web app sample recognizes the pipeline has already launched and WebRTC visualization should immediately begin. The Pipeline Server instance identifier is used for obtaining status and performance information, while the Destination Peer ID is used to request rendered frames from `webrtcbin`.

### Example 3: Grafana Dashboard with multiple instances

Perhaps the easiest way to interact with this sample. Viewing metrics related to Pipeline Server and WebRTC may be consumed by integration into Grafana or similar visualization components. This sample shows how this may be done using a default Grafana Docker image and populating with a dashboard that uses their built-in Infinity datasource to collect FPS metrics and show `active` vs `completed` pipelines as you run these sample streams.

> NOTE: The example Grafana dashboard is optimized for desktops running at resolutions > 1920x1080 or better or mobile > 1116x1609 or 1609x1116.

Navigate in your browser to `http://localhost:3222` or the IP address/FQDN of your host running this sample on port `3222`.

The first time in you will be prompted for credentials so input `admin` as the user and `admin` as the password. Then skip or change the credentials on the next page.

Next click the `Search` menu and choose the dashboard titled `Pipeline Server Sample Dashboard` to view this page.

```
![loaded grafana dashboard](/docs/images/grafana_dashboard_initial.jpg)
```

As shown, this dashboard is populated with four AJAX iframe panels, each representing the same interface we used in Example 1. Notice that each time a panel loads it automatically chooses a pipeline, media source, and appends random digits to the `peer-id` field.

Click the `Launch Pipeline` and `Visualize` button in each panel to see the result.

![webrtc grafana dashboard](/docs/images/grafana_dashboard_active.jpg)

Notice that as primary pipelines run a secondary WebRTC render pipeline also runs. Upon completion we show the results of only the primary pipeline in the panel along the right side of the dashboard. This is populated using content from Pipeline Server's Get Pipeline Status endpoint (http://localhost:8080/pipelines/status).

## Troubleshooting

1. If you encounter issues, be sure to check your host is running the latest version of browser, Docker and Docker Compose.

1. The `./samples/webrtc/run.sh` command instructs Docker Compose to intelligently start only containers that have changed in composition or configuration since your last build. If you run `./samples/webrtc/teardown.sh` beforehand, it will cause all microservices to have clear logs and start from scratch.
   ```
   ./teardown.sh
   ./build.sh --remove-volumes
   ./run.sh
   ```
   Navigate in browser to `http://localhost:3222`.

1. To troubleshoot issues with `pipeline_server` container's use of GStreamer and the webrtcbin element, consider increasing logging by adding the following to the `environment:` section of `./samples/webrtc/docker-compose.yml`
   ```
   - GST_DEBUG=3,*webrtc*:7
   ```

1. The `webrtc_grafana` container runs as the 'grafana' user and 'root' group as documented [here](https://grafana.com/docs/grafana/latest/installation/docker/#migrate-to-v51-or-later). Updates to users/content are stored in the volume mount.

   To wipe out the volume and clear all data, run:
   ```
   ./samples/webrtc/build.sh --remove-volumes
   ```

1. To interact with Pipeline Server from a remote browser such as on your Windows laptop or Android mobile device, update the URL in the browser to point to the system hosting Pipeline Server microservices. This may require that you change from localhost to its IP address or a fully qualified name (FQDN) for the host running Pipeline Server and dependent microservices.

   Confirm that the host running Pipeline Server microservices reside on the same network and are configured to allow access. For example, if your remote system is behind a proxy server, check in the Network Settings of your system and/or browser.
   
   > NOTE: Be aware that some corporate networks may restrict access to ports or have other configuration that limits routes so you may need to check your firewall rules or other network configuration. On restricted or public networks you may extend the implementation by adding secure endpoints and configuring services to utilize STUN/TURN servers -- this will permit connection traversal using best available throughput for alternate/available ports and public IP negotiation.
