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

Port forward port 443 from HAProxy
```sh
$ POD_NAME=$(kubectl get pods | grep haproxy | cut -d' ' -f1)
$ kubectl --namespace default port-forward $POD_NAME 8080:443
```

Example #1: Get status of all pipeline instances
```
$ curl --cacert server.crt https://localhost:8080/pipelines/status
[]
```

Example #2: Submit work request (launch pipeline instance)
```sh
$ curl --cacert cert/server.crt https://localhost:8080/pipelines/object_detection/person_vehicle_bike -X POST -H "Content-Type: application/json" -d '{
   "source":{
      "uri":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true",
      "type":"uri"
   },
   "destination":{
      "frame":{
         "type":"rtsp",
         "path":"ps1"
      }
   }
}'
```
```
"c6f2476444f811ed81550242ac120003"
```

Step 7: Using Pipeline Client

Pipeline Client also supports submitting work requests on Kubernetes Clusters with HTTPS. Test your setup using the [Pipeline Client HTTPS example](/client/README.md#using-https-with-pipeline-client).