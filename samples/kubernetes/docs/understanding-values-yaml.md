# Understanding values.yaml

## Increase number of replicas

values.yaml
```
replicaCount: <number_of_nodes>
```
Upgrade the deployment
```
helm upgrade <release-name> .
```

## Enable control plane for dynamic routing (For multiple pods)

values.yaml
```
controlplane:
  enabled: true
```

## Customizing GPU values

Refer to this doc: [https://github.com/openvinotoolkit/docker_ci/blob/master/configure_gpu_ubuntu20.md](https://github.com/openvinotoolkit/docker_ci/blob/master/configure_gpu_ubuntu20.md) to understand more about GPU configuration.  

Render group does not have a strict group ID, unlike the video group, please check the group ID for your GPU render and then replace at `renderGroup`

values.yaml
```
gpu:
  # renderGroup depends on your GPU's hardware (e.g. TGL - 109)
  renderGroup: 109
```

## Enable network proxy inside pods

values.yaml
```
network:
  proxy:
    enabled: true
    http: http://<proxy>:<port>
    https: http://<proxy>:<port>
    no_proxy: 10.0.0.0/1
```

## Enable frame destination either WebRTC or RTSP output

values.yaml
```
framedestination:
  webrtc:
    enabled: true
    # Leave localSignalingServerImageName empty if you want to deploy your own signalling server
    localSignalingServerImageName: ""
    # Replace the line below if you want to use your own signalling server (websocket signalling server)
    url: ws://$(WEBRTC_SERVER_SERVICE_HOST):$(WEBRTC_SERVER_SERVICE_PORT)
  rtsp:
    enabled: true
    port: 8554
```

## Customize Persistent Volume

values.yaml
```
persistentVolumeClaim:
  enabled: true
  models:
    storageClassName: "<storage-class-name>"
    accessModes: "ReadOnlyMany"
    volumeName: "<volume-name>"
    #Empty string must be explicitly set otherwise default StorageClass will be set
    size: 10Gi
    annotations: {}
  pipelines:
    storageClassName: "<storage-class-name>"
    accessModes: "ReadOnlyMany"
    volumeName: "<volume-name>"
    #Empty string must be explicitly set otherwise default StorageClass will be set
    size: 10Gi
    annotations: {}
  exts:
    storageClassName: "<storage-class-name>"
    accessModes: "ReadOnlyMany"
    volumeName: "<volume-name>"
    #Empty string must be explicitly set otherwise default StorageClass will be set
    size: 10Gi
    annotations: {}
```