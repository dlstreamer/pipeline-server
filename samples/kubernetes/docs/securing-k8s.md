# Securing Kubernetes with SSL/TLS

Step 1: Generate a certificate

```sh
$ samples/nginx-tls-https/generate_cert.sh .
```

Step 2: Merge certificate and key into PEM (HAProxy requirement)

```sh
$ sudo cat server.crt server.key | sudo tee server.pem
```

Step 3: Create ConfigMap for SSL certificate

```sh
$ kubectl create configmap config-map-cert-haproxy --from-file=server.pem
```

Step 4: Edit values.yaml for HAProxy to find the certificate

`values.yaml`
```yaml
haproxy:
  service:
    type: NodePort
  extraVolumeMounts:
    - mountPath: /usr/local/etc/haproxy/servers.map
      name: haproxy-map
      subPath: servers.map
    - mountPath: /etc/ssl/server.pem
      name: haproxy-cert
      subPath: server.pem
  extraVolumes:
    - configMap:
        name: server-maps-haproxy
      name: haproxy-map
    - configMap:
        name: config-map-cert-haproxy
      name: haproxy-cert
```

Step 5: Edit haproxy-template.cfg with 443 SSL binding

`samples/kubernetes/src/pipeline-server-k8s-controller/haproxy-template.cfg`
```
.
.
.
frontend myfrontend
  bind :443 ssl crt /etc/ssl/server.pem
  acl is_controller_api path_end pipelines/status
  acl is_post method POST
.
.
.

```

Step 6: Test your setup

You can test your setup by providing the `server.crt` into the curl when querying.

![httpsk8s](/docs/images/0031-https-k8s.png)

```sh
$ kubectl --namespace default port-forward $POD_NAME 8080:443
$ curl --cacert server.crt https://localhost:8080/pipelines/status
[]
```

Step 7: Using Pipeline Client

Pipeline Client also support Kubernetes Cluster with HTTPS, you can test your setup using Pipeline Client and the same `server.crt` when querying.

```sh
$ client/pipeline_client.sh run object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4\?raw\=true --server-address https://localhost:8443 --server-cert samples/nginx-tls-https/cert/server.crt

.
.
.

Starting pipeline object_detection/person_vehicle_bike, instance = 1843e91040da11edbaf2b62e8c582e09
Pipeline running - instance_id = 1843e91040da11edbaf2b62e8c582e09
No results will be displayed. Unable to read from file /tmp/results.jsonl
avg_fps: 593.75
Done
```