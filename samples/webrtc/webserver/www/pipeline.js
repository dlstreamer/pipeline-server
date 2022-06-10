/*
* Copyright (C) 2022 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
*/

var g_pipeline_server_host=window.location.hostname
var g_pipeline_server_port=8080
var PIPELINE_SERVER = "http://" + g_pipeline_server_host + ':' + g_pipeline_server_port;
var VIDEO_INPUT = ["https://github.com/intel-iot-devkit/sample-videos/raw/master/person-bicycle-car-detection.mp4",
                   "https://github.com/intel-iot-devkit/sample-videos/raw/master/face-demographics-walking-and-pause.mp4",
                   "https://github.com/intel-iot-devkit/sample-videos/raw/master/car-detection.mp4",
                   "https://github.com/intel-iot-devkit/sample-videos/raw/master/people-detection.mp4",
                   "https://github.com/intel-iot-devkit/sample-videos/raw/master/classroom.mp4",
                   "https://github.com/intel-iot-devkit/sample-videos/raw/master/head-pose-face-detection-male.mp4",
                   "https://github.com/intel-iot-devkit/sample-videos/raw/master/bottle-detection.mp4",
                   "https://lvamedia.blob.core.windows.net/public/homes_00425.mkv"]
var g_trim_media_prefix = true;
var g_assigned_by_query_param = false;
var g_pipeline_server_instance_id = null;
var g_default_server_peer_id = null;
var g_init_pipeline_idx = null;
var g_init_media_idx = null;
var g_sync_playback = true;
var g_poll_status = true;
var g_initialized_expando = false;
var g_grafana_dashboard_manual_launch = false;

function initExpando(classname) {
    if (!g_initialized_expando) {
        var coll = document.getElementsByClassName(classname);
        var i;
        for (i = 0; i < coll.length; i++) {
            if (coll[i].getAttribute('listener') !== 'true') {
                coll[i].addEventListener("click", function(elm) {
                    const elmClicked = elm.target;
                    elmClicked.setAttribute('listener', 'true');
                    console.log("Attached click listener to expando section.")
                    this.classList.toggle("active");
                    var content = this.nextElementSibling;
                    if (content.style.maxHeight){
                        content.style.maxHeight = null;
                    } else {
                        content.style.maxHeight = content.scrollHeight + "px";
                    } 
                });
            }
        }
        g_initialized_expando = true;
    }
}

function restReq(verb, route, body, callback) {
    var request = new XMLHttpRequest();
    request.open(verb, route); 
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.setRequestHeader("Vary", "Origin");
    request.onreadystatechange = function() {
        if (request.readyState === 4) {
            callback(request.response, request.status);
        }
    }
    console.log("Invoking " + verb + " on route " + route);
    request.send(body);
}

function receivePipelines(responseValue, http_status) {
    pipelines = [];
    responsePipelines = JSON.parse(responseValue);
    responsePipelines.forEach(function(obj) {
        pipeline = obj.name + "/" + obj.version;
        console.log(pipeline);
        pipelines.push(pipeline);
    });
    setPipelinesAvailable(pipelines);
}

function onGetPipelinesClicked() {
    var pipeline_server = getPipelineServer();
    var requestPath = "/pipelines"
    requestPipelines(pipeline_server, requestPath, receivePipelines);
}

function requestPipelines(pipeline_server, requestPath, callback) {
    restReq("GET", pipeline_server + requestPath, '', callback);
}

function setPipelinesAvailable(options) {
    var selPipelines = document.getElementById('pipelines');
    selPipelines.options.length = 0;
    var def = document.createElement("option");
    def.textContent = "[Choose a pipeline]";
    def.value = "";
    selPipelines.appendChild(def);
    for(var i = 0; i < options.length; i++) {
        var opt = options[i];
        var el = document.createElement("option");
        el.textContent = opt;
        el.value = opt;
        selPipelines.appendChild(el);
        if (g_init_pipeline_idx == i) {
            def.value = opt;
            setPipeline(opt);
        }
    }
    selPipelines.options.selectedIndex = g_init_pipeline_idx;
    selPipelines.onchange();
}

function receiveStopResult(responseValue, http_status) {
    console.log(responseValue);
}

function onStopClicked() {
    var pipeline_server = getPipelineServer();
    var idInstanceID = document.getElementById("instance-id")
    var instance_id = idInstanceID.value;
    if (pipeline_server != null && instance_id != null && instance_id != "") {
        if (instance_id == "unknown") {
            alert("Pipeline Server instance_id was created offline (it is unknown)");
            return;
        }
        var requestPath = pipeline_server + "/pipelines/" + instance_id;
        doStop(requestPath, receiveStopResult);
    } else {
        alert("No active Pipeline Server pipeline instance!");
        g_poll_status = false;
    }
}

function doStop(requestPath, callback) {
    setVizStatus("Stopping primary pipeline ("+requestPath+")...");
    restReq("DELETE", requestPath, '', callback);
}

function getJsonValue(objJSON, key) {
    var value = null;
    if (key in objJSON) {
        value = objJSON[key];
    }
    return value;
}

function receiveStatusResult(responseValue, status_code) {
      if (g_pipeline_server_instance_id != "unknown" && g_poll_status) {
        var objStatus = JSON.parse(responseValue);
        var span = document.getElementById("fps-status");
        span.style.visibility = "visible";
        if (status_code == 200 && objStatus != "Invalid instance") {
            var avg_fps = parseFloat(getJsonValue(objStatus, "avg_fps")).toFixed(2);
            var elapsed_sec = parseFloat(getJsonValue(objStatus, "elapsed_time")).toFixed(0);
            var state = getJsonValue(objStatus, "state");
            var status_text = "Pipeline State: " + state + "    " + avg_fps + " fps (avg)   Elapsed: " + elapsed_sec + "s";
            document.getElementById("fps-status").innerHTML = status_text;
            span.style.color = "#007dc3";
            if (state == "COMPLETED") {
                console.log("Pipeline state is COMPLETED, so will no longer query for pipeline status each 3s for instance " + getJsonValue(objStatus, "id") + ".");
                g_poll_status=false;
                connect_attempts = 15; // expire visualization retries for this primary pipeline
                console.log("Toggle to expand pipeline_launcher section for new stream")
                document.getElementById("pipeline_launcher").click();
                // Disable Disconnect/Visualize and Stop Pipeline Buttons until we have a running stream
                setVizStatus("Launch a new pipeline...");
            } else if (state == "ABORTED") {
                console.log("Pipeline state is ABORTED, so will no longer query for pipeline status each 3s for instance " + getJsonValue(objStatus, "id") + ".");
                g_poll_status=false;
                connect_attempts = 15; // expire visualization retries for this primary pipeline
                setVizStatus("Launch a new pipeline...");
            }
        } else {
            span.innerHTML = "Pipeline State: " + objStatus + "    http_status: " + status_code;
            span.style.color = "red";
            if (objStatus == "Invalid instance") {
                g_poll_status = false;
                console.log("Pipeline state had status_code " + status_code + " so will no longer query for pipeline status each 3s for instance " + getJsonValue(objStatus, "id") + ".");
            }
        }
    }
}

function doGetStatus(requestPath, callback) {
    restReq("GET", requestPath, '', callback);
}

function updateFPS() {
    g_poll_status = true;
    var statusEvery3Sec = window.setInterval(function() {
        console.log("Updating FPS from Pipeline Server status endpoint for instance " + g_pipeline_server_instance_id + ".");
        var pipeline_server = getPipelineServer();
        if (pipeline_server != null && g_pipeline_server_instance_id != null 
            && g_pipeline_server_instance_id != "unknown" && g_pipeline_server_instance_id != "") {
            var requestPath = pipeline_server + "/pipelines/status/" + g_pipeline_server_instance_id;
            doGetStatus(requestPath, receiveStatusResult);
        } else {
            if (g_pipeline_server_instance_id == "unknown") {
                console.log("WARNING: Pipeline Server pipeline instance is completely unknown!");
            } else {
                console.log("WARNING: No active Pipeline Server pipeline instance! Stopping fps polling.");
                g_poll_status = false;
            }
        }
        if (!g_poll_status) {
            if (peer_connection == null) {
                clearInterval(statusEvery3Sec); // fps, etc should no longer update.
                console.log("Cleared status update interval for pipeline instance " + g_pipeline_server_instance_id + ".");
            } else {
                console.log("Waiting for WebRTC peer connection to close for pipeline instance " + g_pipeline_server_instance_id + ".");
            }
        }
    }, 3000);
}

function setPipelineServer(value) {
    document.getElementById('pipeline-server').value = value;
}
function getPipelineServer() {
    return document.getElementById('pipeline-server').value;
}

function setMediaSource(value) {
    elm = document.getElementById('mediasource');
    elm.value = value;
    if (elm.onchange)
        elm.onchange();
}
function getMediaSource() {
    return document.getElementById('mediasource').value;
}

function setPipeline(value) {
    elm = document.getElementById('pipeline');
    elm.value = value;
    if (elm.onchange)
        elm.onchange();
}
function getPipeline() {
    return document.getElementById('pipeline').value;
}

function getRandomInt(max) {
    return Math.floor(Math.random() * max);
}

function setDestinationPeerID(value) {
    elm = document.getElementById('destination-peer-id');
    elm.value = value.replace('$RANDOM', getRandomInt(100000).toString());
    if (elm.onchange)
        elm.onchange();
}
function getDestinationPeerID() {
    return document.getElementById('destination-peer-id').value;
}

function setMediaSources(options) {
    var selSources = document.getElementById("sel_mediasources");
    selSources.options.length = 0;
    if (selSources != null) {
        var def = document.createElement("option");
        def.textContent = "[Choose a media source]";
        def.value = "";
        selSources.appendChild(def);
        for(var i = 0; i < options.length; i++) {
            var opt = options[i];
            var el = document.createElement("option");
            if (g_trim_media_prefix) {
                media_name = opt.replace("https://github.com/intel-iot-devkit/sample-videos/raw/master/", "");
                media_name = media_name.replace("https://lvamedia.blob.core.windows.net/public/", "");
            } else {
                media_name = opt;
            }
            el.textContent = media_name;
            el.value = opt;
            selSources.appendChild(el);
            if (g_init_media_idx == i) {
                def.value = opt;
                setMediaSource(opt);
            }
        }
        selSources.options.selectedIndex = g_init_media_idx;
        selSources.onchange();
    } else {
        alert("sel_mediasources select element is not yet on page")
    }
}

function initPipelineValues() {
    setPipelineServer(PIPELINE_SERVER);
    var sources = [];
    for (var i = 0; i < VIDEO_INPUT.length; i++) {
        sources.push(VIDEO_INPUT[i]);
    }
    const params = new Proxy(new URLSearchParams(window.location.search), {
        get: (searchParams, prop) => searchParams.get(prop),
    });
    if (params.autolaunch) {
        g_grafana_dashboard_auto_launch = (params.autolaunch == "true");
    }
    if (params.pipeline_idx) {
        g_init_pipeline_idx = params.pipeline_idx;
        onGetPipelinesClicked();
        if (params.media_idx) {
            g_init_media_idx = params.media_idx;
        }
    }
    setMediaSources(sources);
}

function receivePipelineInstance(responseValue) {
    if (responseValue == null || responseValue == "") {
        console.log("ERROR launching Pipeline Server pipeline instance!");
    } else {
        setStreamInstanceValue(responseValue);
    }
}

function updateLaunchButtonState() {
    document.getElementById("pipeline-launch-button").disabled = true;
    p = getPipeline();
    s = getMediaSource();
    f = getDestinationPeerID();
    if (p && s && f) {
        document.getElementById("pipeline-launch-button").disabled = false;
    } else {
        console.log("Launch button disabled because user must supply:")
        console.log("pipeline: " + p);
        console.log("source: " + s);
        console.log("destination peer-id: " + f);
    }
}

function onLaunchClicked() {
    var pipeline_server = getPipelineServer();
    var pipeline = getPipeline();
    if (!pipeline) { alert("You must specify a pipeline!"); }
    var source = getMediaSource();
    if (!source) { alert("You must specify a media source!"); }
    var frame_destination_peer_id = getDestinationPeerID();
    var sync_playback = getSyncPlayback();
    var requestPath = pipeline_server + "/pipelines/" + pipeline;
    var frame_destination = { "type": "webrtc",
                              "peer-id": frame_destination_peer_id,
                              "sync-with-source": sync_playback,
                              "sync-with-destination": sync_playback
                            };
    var parameters = {"detection-device": "CPU"}
    var requestBody = JSON.stringify(
                            {
                                "source": {"uri": source, "type": "uri"}, 
                                "destination": {
                                    "metadata": {"type": "file", "path": "/tmp/results.jsonl", "format": "json-lines"},
                                    "frame": frame_destination 
                                },
                                "parameters": parameters 
                            });
    setFrameDestinationLabel();
    doLaunch(requestPath, requestBody, receivePipelineInstance);
}

function doLaunch(requestPath, requestBody, callback) {
    connect_attempts = 0;
    restReq("POST", requestPath, requestBody, callback);
}

function getSyncPlayback() {
    return document.getElementById("sync-checkbox").checked;
}

function setFrameDestinationLabel() {
    var peer_id = getDestinationPeerID();
    var sync_playback = getSyncPlayback()
    var elm = document.getElementById("destination")
    elm.value = JSON.stringify({ "type": "webrtc", "peer-id": peer_id,
        "sync-with-source": sync_playback, "sync-with-destination": sync_playback });
    if (elm.onchange) 
         elm.onchange();
}

function setStreamInstanceValue(value) {
    if (value == null) {
        console.log("ERROR: Cannot set stream instance to empty value");
        console.log("WARNING: Assigning primary stream instance_id to value 'unknown' to allow WebRTC rendering.");
        //return;
    }
    // remove any quotes surrounding instance_id response
    instance_id=value.replace(/['"\n]+/g, '')
    g_pipeline_server_instance_id = instance_id;
    var idInstanceID = document.getElementById("instance-id")
    idInstanceID.value = g_pipeline_server_instance_id;
    var frame_destination_peer_id = getDestinationPeerID();
    console.log("Pipeline Server instance: " + instance_id + " was launched with destination_peerid: " + frame_destination_peer_id + ".");
    g_default_server_peer_id = frame_destination_peer_id;
    var idServerPeer = document.getElementById("peer-connect")
    idServerPeer.value = frame_destination_peer_id;
    console.log("Toggle to collapse pipeline_launcher section on SetStreamInstanceValue")
    document.getElementById("pipeline_launcher").click();
    console.log("Pipeline Server - starting Pipeline Status (FPS) timer for instance " + instance_id + " with destination_peerid: " + frame_destination_peer_id + ".");
    statsTimerPipelineStatus = setTimeout(updateFPS, 100);

    var auto_visualize_params = "?instance_id=" +  instance_id + "&destination_peer_id=" + frame_destination_peer_id + "";
    var viz_message = ""
    if (g_assigned_by_query_param) {
        if (window.location.hostname === "localhost") {
            viz_message = "Click the 'Visualize' button to view the pipeline stream. Stream may be alternately viewed by navigating to this site remotely using query parameters: ";
        } else {
            viz_message = "Remove the following query parameters to launch/view new streams: ";
        }
    } else {
        if (window.location.hostname === "localhost") {
            viz_message = "Stream may be viewed by clicking 'Visualize' button or navigating in remote browser to this site, adding query parameters: "
        } else {
            viz_message = "Click the 'Visualize' button to view the pipeline stream."
            auto_visualize_params = "";
        }
    }
    setVizStatus(viz_message + auto_visualize_params);
}

function updateLaunchFormVisibility(value) {
    document.getElementById("launch-form").style.display = value;    
}

function setVizStatus(text) {
    console.log(text);
    document.getElementById("viz_status").textContent = text;
    if (text == "Launch a new pipeline...") {
        // disable visualize actions; will re-enable once pipeline is launched
        console.log("Visualize/Stop buttons disabled until pipeline is launched.")
        document.getElementById("peer-connect-button").disabled = true;
        document.getElementById("pipeline-stop-button").disabled = true;
    } else {
        document.getElementById("peer-connect-button").disabled = false;
        if (g_pipeline_server_instance_id != "unknown") {
            document.getElementById("pipeline-stop-button").disabled = false;
        }
    }
}

function setStreamInstance() {
    const params = new Proxy(new URLSearchParams(window.location.search), {
        get: (searchParams, prop) => searchParams.get(prop),
    });
    if (g_pipeline_server_instance_id == null || g_pipeline_server_instance_id == "" || g_pipeline_server_instance_id == "unknown" ) {
        g_pipeline_server_instance_id = params.instance_id;
    }
    var idServerPeer = document.getElementById("peer-connect");
    if (idServerPeer.value == null || idServerPeer.value == "") {
        g_default_server_peer_id = params.destination_peer_id;
        idServerPeer.value = g_default_server_peer_id;
        if (g_default_server_peer_id) {
            setDestinationPeerID(g_default_server_peer_id);
        }
    }
    if (g_pipeline_server_instance_id) {
        console.log("Will attempt to automatically connect to instance_id: " + g_pipeline_server_instance_id);
        console.log("Collapsing New Pipeline Launcher section")
        document.getElementById("pipeline_launcher").click();
    } else {
        console.log("Toggle to show pipeline_launcher section on setStreamInstance")
        document.getElementById("pipeline_launcher").click();
        setConnectButtonState("Visualize");
        console.log("Assigning Pipeline Server instance_id to 'unknown' in case peer-id is legitimate to visualize directly.")
        document.getElementById("pipeline-stop-button").disabled = true;
        g_pipeline_server_instance_id = "unknown";
        document.getElementById("instance-id").value = g_pipeline_server_instance_id;
    }
    g_grafana_dashboard_manual_launch = (g_init_pipeline_idx && g_init_media_idx);
    var automate_grafana = false;
    if (g_grafana_dashboard_manual_launch && automate_grafana) {
        console.log("AUTO-LAUNCH grafana panels");
        onLaunchClicked();
        onConnectClicked();
    }
    var autoConnect = false;
    if (g_grafana_dashboard_manual_launch) {
        autoConnect = (idServerPeer.value && g_pipeline_server_instance_id && g_pipeline_server_instance_id != "unknown");
    } else {
        if (g_default_server_peer_id) {
            g_assigned_by_query_param = true;
            setStreamInstanceValue(g_pipeline_server_instance_id);
            updateLaunchButtonState();
            setConnectButtonState("Disconnect"); // since we're autoplaying
            console.log("Will attempt to automatically connect using frame destination peer_id: " + g_default_server_peer_id);
            setStatus("WebRTC auto-connecting to instance: '" + g_pipeline_server_instance_id + "' peer_id: '" + g_default_server_peer_id + "'");
        }
        autoConnect = (idServerPeer.value && g_pipeline_server_instance_id);
    }
    return autoConnect;
}
