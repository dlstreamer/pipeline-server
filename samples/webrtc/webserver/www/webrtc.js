/* vim: set sts=4 sw=4 et :
 *
 * Demo Javascript app for negotiating and streaming a sendrecv webrtc stream
 * with a GStreamer app. Runs only in passive mode, i.e., responds to offers
 * with answers, exchanges ICE candidates, and streams.
 *
 * Author: Nirbheek Chauhan <nirbheek@centricular.com>
 */

/*
* Copyright (C) 2022 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
*/

// Set this to override the automatic detection in websocketServerConnect()
var ws_server;
var ws_port;
// Set this to use a specific peer id instead of a random one; e.g., 256
var default_peer_id = null;

// Override with your own STUN servers if you want
var rtc_configuration = {};
//var rtc_configuration = {iceServers: [{urls: "stun:stun.services.mozilla.com"},
//                                      {urls: "stun:stun.l.google.com:19302"}]};

// Launchable WebRTC pipelines
var auto_retry = true;
var DELAY_AUTOSTART_MSEC=2000

// The default constraints that will be attempted. Can be overriden by the user.
var default_constraints = {video: true, audio: false};

var connect_attempts = 0;
var loop = false;
var peer_connection;
var send_channel;
var ws_conn = null;
// Promise for local stream after constraints are approved by the user
var local_stream_promise;
var statsTimer;
var statsTimerPipelineStatus;

function setConnectButtonState(value) {
    document.getElementById("peer-connect-button").value = value;
    if (value == "Visualize") {
        document.getElementById("divStreamPlayback").style.display = "none";
        if (g_pipeline_server_instance_id == "unknown") {
            viz_message = "WARNING: No pipeline instance provided so its state is unknown. Click 'Visualize' to attempt direct render."
            setVizStatus(viz_message);
        } else if (g_poll_status) { // handle pipeline stopped condition
            viz_message = "Click 'Visualize' to resume rendering (re-connect to the stream), or Stop Pipeline to terminate the stream."
            setVizStatus(viz_message);
        }
    } else {
        document.getElementById("divStreamPlayback").style.display = "";
        if (g_pipeline_server_instance_id == "unknown") {
            viz_message = "WARNING: No pipeline instance provided so its state is unknown. Click 'Disconnect' to attempt direct un-render."
            setVizStatus(viz_message);
        } else if (g_poll_status) { // handle pipeline stopped condition
            viz_message = "Click the 'Disconnect' button to suspend rendering, or Stop Pipeline to terminate the stream."
            setVizStatus(viz_message);
        }
    }
}

function isSocketOpen(ws_conn) {
    if (ws_conn == null) {
        return false;
    }
    return (ws_conn.readyState === ws_conn.OPEN);
}

function onConnectClicked() {
    if (isSocketOpen(ws_conn) || document.getElementById("peer-connect-button").value === "Disconnect") {
        resetState();
        setConnectButtonState("Visualize");
        return;
    }
    var id = document.getElementById("peer-connect").value;
    if (id == "") {
        alert("Target stream peer id must be provided. Populate peer-connect field with destination_peer_id and click Visualize.");
        return;
    }
    window.setTimeout(websocketServerConnect, 600);
    ws_conn.send("SESSION " + id);
    setConnectButtonState("Disconnect");
}

function getOurId() {
    return Math.floor(Math.random() * (9000 - 10) + 10).toString();
}

function resetState() {
    // This will call onServerClose()
    if (ws_conn) {
        ws_conn.close();
    } else {
        console.log("INFO: resetState called with no active connection.")
    }
}

function handleIncomingError(error) {
    setError("ERROR: " + error);
    resetState();
    if (auto_retry) {
        window.setTimeout(websocketServerConnect, DELAY_AUTOSTART_MSEC);
    }
}

function getVideoElement() {
    return document.getElementById("stream");
}

function setStatus(text) {
    console.log(text);
    var span = document.getElementById("status")
    if (!span.classList.contains('error'))
        span.textContent = text;
}

function setError(text) {

    console.error(text);
    var span = document.getElementById("status")
    var newContent = text;
    if (!span.classList.contains('error'))
        span.classList.add('error');
    else {
        newContent = span.textContent + text;
    }
    span.style.visibility = "visible";
    span.textContent = newContent;
}

function resetVideo() {
    // Release the webcam and mic
    if (local_stream_promise)
        local_stream_promise.then(stream => {
            if (stream) {
                stream.getTracks().forEach(function (track) { track.stop(); });
            }
        });

    // Reset the video element and stop showing the last received frame
    var videoElement = getVideoElement();
    videoElement.pause();
    videoElement.src = "";
    videoElement.load();
}

// SDP offer received from peer, set remote description and create an answer
function onIncomingSDP(sdp) {
    peer_connection.setRemoteDescription(sdp).then(() => {
        setStatus("Remote SDP set");
        if (sdp.type != "offer")
            return;
        setStatus("Got SDP offer");
        if (local_stream_promise) {
            local_stream_promise.then((stream) => {
                setStatus("Got local stream, creating answer");
                peer_connection.createAnswer()
                .then(onLocalDescription).catch(setError);
            }).catch(setError);
        } else {
            peer_connection.createAnswer().then(onLocalDescription).catch(setError);
        }
    }).catch(setError);
}

// Local description was set, send it to peer
function onLocalDescription(desc) {
    console.log("Got local description: " + JSON.stringify(desc));
    peer_connection.setLocalDescription(desc).then(function() {
        setStatus("Sending SDP answer");
        sdp = {'sdp': peer_connection.localDescription}
        ws_conn.send(JSON.stringify(sdp));
    });
}

// ICE candidate received from peer, add it to the peer connection
function onIncomingICE(ice) {
    var candidate = new RTCIceCandidate(ice);
    peer_connection.addIceCandidate(candidate).catch(setError);
}

function onServerMessage(event) {
    console.log("Received " + event.data);
    switch (event.data) {
        case "HELLO":
            ws_conn.send('SESSION ' + g_default_server_peer_id);
            setStatus("Registered with server, waiting for call");
            return;
        case "SESSION_OK":
            setStatus("Initiating stream session");

            ws_conn.send('START_WEBRTC_STREAM');
            /* Intentionally not implementing offers from client
            if (wantRemoteOfferer()) {
                ws_conn.send("OFFER_REQUEST");
                setStatus("Sent OFFER_REQUEST, waiting for offer");
                return;
            }
            if (!peer_connection)
                createCall(null).then (generateOffer);
            */
            return;
        /* Not implementing
        case "OFFER_REQUEST":
            // The peer wants us to set up and then send an offer
            if (!peer_connection)
                createCall(null).then (generateOffer);
                return;
        */
        default:
            setStatus("Event received while registering with server: " + event.data);
            if (event.data.startsWith("ERROR")) {
                handleIncomingError(event.data);
                return;
            }
            // Handle incoming JSON SDP and ICE messages
            try {
                msg = JSON.parse(event.data);
            } catch (e) {
                if (e instanceof SyntaxError) {
                    handleIncomingError("Error parsing incoming JSON: " + event.data);
                } else {
                    handleIncomingError("Unknown error parsing response: " + event.data);
                }
                return;
            }

            // Incoming JSON signals the beginning of a call
            if (!peer_connection)
                createCall(msg);

            if (msg.sdp != null) {
                onIncomingSDP(msg.sdp);
            } else if (msg.ice != null) {
                onIncomingICE(msg.ice);
            } else {
                handleIncomingError("Unknown incoming JSON: " + msg);
            }
    }
}

function onServerClose(event) {
    setStatus('Stream ended. Disconnected from server');
    resetVideo();

    if (peer_connection) {
        clearTimeout(statsTimer);
        peer_connection.close();
        peer_connection = null;
    }

    // Reset after a second if we want to loop (connect and re-stream)
    if (loop) {
        window.setTimeout(websocketServerConnect, 1000);
    } else {
        setConnectButtonState("Visualize");
    }
}

function onServerError(event) {
    setError("Unable to connect to server. Confirm it is running and accessible on network.")
    // Retry after 2 seconds
    window.setTimeout(websocketServerConnect, DELAY_AUTOSTART_MSEC);
}

function getLocalStream() {
    var constraints;
    var textarea = document.getElementById('constraints');
    try {
        constraints = JSON.parse(textarea.value);
    } catch (e) {
        console.error(e);
        setError('ERROR parsing constraints: ' + e.message + ', using default constraints');
        constraints = default_constraints;
    }
    console.log(JSON.stringify(constraints));

    // Add local stream
    if (navigator.mediaDevices.getUserMedia) {
        return navigator.mediaDevices.getUserMedia(constraints);
    } else {
        errorUserMediaHandler();
    }
}

function websocketServerConnect() {
    connect_attempts++;
    if (connect_attempts > 15) {
        setError("Too many connection attempts, aborting. Refresh page to try again");
        return;
    }
    setConnectButtonState("Disconnect");

    // initialize expandable form sections
    initExpando("expando");

    // initialize Pipeline Server API parameters
    initPipelineValues();

    // if empty, populate pipeline server instance id to connect using value from query param
    var attempt_connect = setStreamInstance();
    if (attempt_connect) {
        console.log("Parameters provided - attempting to connect");
    } else {
        return;
    }
    if (!g_default_server_peer_id) {
        console.log("Will not attempt connection until Pipeline Server WebRTC frame destination peerid is requested.");
        return;
    }

    // Clear errors in the status span for fresh run
    console.log("Clearing error state from WebRTC status field.")
    var span = document.getElementById("status");
    span.classList.remove('error');
    console.log("Clearing stats for fresh WebRTC run");
    window.document.getElementById("stats").innerHTML = "Preparing WebRTC Stats...";
    // Populate constraints
    var textarea = document.getElementById('constraints');
    if (textarea.value == '')
        textarea.value = JSON.stringify(default_constraints);
    // Fetch the peer id to use
    peer_id = default_peer_id || getOurId();
    ws_port = ws_port || '8443';
    if (window.location.protocol.startsWith ("file")) {
        ws_server = ws_server || "127.0.0.1";
    } else if (window.location.protocol.startsWith ("http")) {
        let searchParams = new URLSearchParams(window.location.search);
        if (searchParams.has("websocket") === true) {
            ws_server = searchParams.get("websocket");
            ws_port = searchParams.get("wsport");
        } else {
            ws_server = ws_server || window.location.hostname;
        }
    } else {
        throw new Error ("Don't know how to connect to the signaling server with uri" + window.location);
    }

    // Support AutoPlay in Chrome/Safari browsers
    var autoPlayVideo = document.getElementById("stream");
    autoPlayVideo.oncanplaythrough = function() {
        autoPlayVideo.muted = true;
        autoPlayVideo.play();
        autoPlayVideo.pause();
        autoPlayVideo.play();
    }
    autoPlayVideo.scrollIntoView(false);

    var ws_url = 'ws://' + ws_server + ':' + ws_port;
    setStatus("Connecting to server " + ws_url);
    ws_conn = new WebSocket(ws_url);
    /* When connected, immediately register with the server */
    ws_conn.addEventListener('open', (event) => {
        document.getElementById("peer-id").value = peer_id;
        ws_conn.send('HELLO ' + peer_id);
        setStatus("Registering with server as client " + peer_id.toString());
        //setConnectButtonState("Visualize");
    });
    ws_conn.addEventListener('error', onServerError);
    ws_conn.addEventListener('message', onServerMessage);
    ws_conn.addEventListener('close', onServerClose);
}

function onRemoteTrack(event) {
    if (getVideoElement().srcObject !== event.streams[0]) {
        console.log('Incoming stream');
        getVideoElement().srcObject = event.streams[0];
    }
}

function errorUserMediaHandler() {
    setError("Browser doesn't support getUserMedia!");
}

const handleDataChannelOpen = (event) =>{
    console.log("dataChannel.OnOpen", event);
};

const handleDataChannelMessageReceived = (event) =>{
    console.log("dataChannel.OnMessage:", event, event.data.type);

    setStatus("Received data channel message");
    if (typeof event.data === 'string' || event.data instanceof String) {
        console.log('Incoming string message: ' + event.data);
        textarea = document.getElementById("text")
        textarea.value = textarea.value + '\n' + event.data
    } else {
        console.log('Incoming data message');
    }
    send_channel.send("Hi! (from browser)");
};

const handleDataChannelError = (error) =>{
    console.log("dataChannel.OnError:", error);
};

const handleDataChannelClose = (event) =>{
    console.log("dataChannel.OnClose", event);
};

function onDataChannel(event) {
    setStatus("Data channel created");
    let receiveChannel = event.channel;
    receiveChannel.onopen = handleDataChannelOpen;
    receiveChannel.onmessage = handleDataChannelMessageReceived;
    receiveChannel.onerror = handleDataChannelError;
    receiveChannel.onclose = handleDataChannelClose;
}


function printStats() {
    var statsEvery6Sec = window.setInterval(function() {
        if (peer_connection == null) {
            setStatus("Stream completed. Check console output for detailed information.");
            clearInterval(statsEvery6Sec);
            setConnectButtonState("Visualize");
        } else {
            peer_connection.getStats(null).then(stats => {
            let statsOutput = "";
            if (g_pipeline_server_instance_id != "unknown") {
                statsOutput += `<h2>Pipeline Summary:</h2>\n<strong><a target="_blank" href=${PIPELINE_SERVER}/pipelines/${g_pipeline_server_instance_id}>${PIPELINE_SERVER}/pipelines/${g_pipeline_server_instance_id}</a></strong>`
                statsOutput += `<h2>Pipeline Status:</h2>\n<strong><a target="_blank" href=${PIPELINE_SERVER}/pipelines/status/${g_pipeline_server_instance_id}>${PIPELINE_SERVER}/pipelines/status/${g_pipeline_server_instance_id}</a></strong>`
            } else {
                statsOutput += `<h2>Pipeline Server Instance ID UNKNOWN</h2>`
            }
            stats.forEach(report => {
                statsOutput += `<h2>Report: ${report.type}</h2>\n<strong>ID:</strong> ${report.id}<br>\n` +
                            `<strong>Timestamp:</strong> ${report.timestamp}<br>\n`;
                // Now the statistics for this report; we intentionally drop the ones we
                // sorted to the top above
                Object.keys(report).forEach(statName => {
                if (statName !== "id" && statName !== "timestamp" && statName !== "type") {
                    statsOutput += `<strong>${statName}:</strong> ${report[statName]}<br>\n`;
                }
                });
            });
            window.document.getElementById("stats").innerHTML = statsOutput;
            });
        }
    }, 6000);
}

function createCall(msg) {
    // Reset connection attempts because we connected successfully
    connect_attempts = 0;

    console.log('Creating RTCPeerConnection');
    setStatus("Creating RTCPeerConnection");

    peer_connection = new RTCPeerConnection(rtc_configuration);
    send_channel = peer_connection.createDataChannel('label', null);
    send_channel.onopen = handleDataChannelOpen;
    send_channel.onmessage = handleDataChannelMessageReceived;
    send_channel.onerror = handleDataChannelError;
    send_channel.onclose = handleDataChannelClose;
    peer_connection.ondatachannel = onDataChannel;
    peer_connection.ontrack = onRemoteTrack;
    statsTimer = setTimeout(printStats, 4000);
    
    /* Send our video/audio to the other peer */
    /* local_stream_promise = getLocalStream().then((stream) => {
        console.log('Adding local stream');
        peer_connection.addStream(stream);
        return stream;
    }).catch(setError); */

    if (!msg.sdp) {
        console.log("WARNING: First message wasn't an SDP message!?");
    }

    peer_connection.onicecandidate = (event) => {
        // We have a candidate, send it to the remote party with the same uuid
        if (event.candidate == null) {
            console.log("ICE Candidate was null, done");
           return;
        }
        ws_conn.send(JSON.stringify({'ice': event.candidate}));
    };

    setConnectButtonState("Disconnect");

    setStatus("Created peer connection for call, waiting for SDP");
}
