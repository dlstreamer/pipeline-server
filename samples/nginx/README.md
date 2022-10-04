# Securing Pipeline Server using NGINX

Clone Pipeline Server repository and enter into NGINX directory:

```
git clone https://github.com/dlstreamer/pipeline-server
cd samples/nginx-tls-https/ 
```

The scripts in this directory provides an example of using NGINX to secure HTTP traffic to Pipeline Server using SSL/TLS encryption.

> **Warning** Those certificates generated from this scripts are only for development and testing purposes. Do not use these certificates for production use, follow best practices of your organization. For ensuring “fast fail”, certificates generated here will expire after a single day.

> **Warning** Review the NGINX configurations and adjust them according to your organization's policies: you are responsible for the settings and using a secured configurations.

![tlsnginx](/docs/images/tls_nginx_pipeline_server.png)

## Prerequisites

| |                  |
|---------------------------------------------|------------------|
| **Pipeline Server** | Refer to the main README.md to [build Pipeline Server](/) or docker pull the image from Docker Hub . |
| **OpenSSL** | `generate_cert.sh` requires OpenSSL in order to generate a self-signed certificate. |

| Script Name                  | Description                                                                                                                                                                                                                                        |
|------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| generate_cert.sh            | Expects one argument for directory. e.g. `./generate_certs.sh <your-directory>`                                                                                                                                                                    |
| run_nginx_pipeline_server.sh | Creates an isolated bridged docker network and launches a nginx docker with port 8443 enabled together with pipeline server docker with HTTP web disabled. Takes one argument for user to define TLS port, by default this is set to be port 8443. |

# Quick Start

1. Build Pipeline Server image from [building an image](/).
2. Run `./generate_cert.sh .` (This script accept one argument to `generate_cert.sh <your_directory>`) this will generate a `cert` directory, please make sure that this cert directory is placed in the same location as the `run_nginx_pipeline_server.sh` for `docker` to find it. It will generate a self-signed certificates (for testing only - follow your organization process for requesting and generating the server certificates)
3. From here, you can run and execute Pipeline Server and NGINX using `./run_nginx_pipeline_server.sh` (This launches NGINX with port 8443 by default, but you can change this port by `./run_nginx_pipeline_server.sh --tls-port <your-desired-port-number>`). This will create a docker network to isolate HTTP endpoint on Pipeline Server and expose only NGINX on port 443 for HTTPS. You can verify your output by running starting a pipeline and you should see an output on RTSP using VLC as shown below:
4. After stopping the server, run `./clean.sh` this will remove the bridged network and the nginx server once it's done.

# Rate Limiting

Inside `nginx.conf`, we have enabled rate limiting to limit the number of request to prevent overloading the server. Currently this is set default to 10 request per second.

This will set a default behaviour of NGINX to reject if a request comes sooner than 1 request every 100 milliseconds (ms) between 2 consecutive request calls. Exceeding this "rate" will give [Error Code 503 Service Unavailable](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/503).

You can adjust this value as shown below if you require busting request or faster request calls between requests:

`nginx.conf`
```
limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s;
```