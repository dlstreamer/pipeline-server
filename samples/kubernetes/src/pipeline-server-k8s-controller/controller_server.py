#!/usr/bin/env python3
'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import os
import json
import logging
import tornado.ioloop
import tornado.web
import requests
from kubectl import KubeCtl

k8s_release_name = os.getenv("MY_RELEASE_NAME")
k8s_namespace = os.getenv("MY_NAMESPACE")
kubectl = KubeCtl(k8s_namespace)
logger = logging.getLogger("controller_server")
logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

# pylint: disable=W0223
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        logger.info("HTTP GET Request")
        json_output = []
        worker_hostnames = kubectl.get_pods_names(k8s_release_name + "-pipeline-server")
        for worker_hostname in worker_hostnames:
            ip_address = kubectl.get_pod_ip_from_name(worker_hostname)
            req = requests.get('http://' + ip_address + ':8080/pipelines/status')
            try:
                if req.json():
                    logger.info(req.json())
                    json_output += req.json()
            except Exception as err:
                logger.error("Error in JSON output from worker nodes - {}".format(err))
                return tornado.web.HTTPError(400)
        if json_output:
            self.write(json.dumps(json_output, indent=4) + "\n")
        else:
            self.write("[]\n")
        return None

class RunServer(tornado.web.Application):
    def __init__(self, log_level = "INFO"):
        # pylint: disable=global-statement
        global logger
        handlers = [ (r"/pipelines/status", MainHandler), ]
        settings = {'debug': False}
        logger.setLevel(log_level)
        super().__init__(handlers, **settings)

    def run_server(self):
        logger.info("Starting Tornado Server")
        self.listen(8080)
        tornado.ioloop.IOLoop.instance().start()

    def stop_server(self):
        logger.info("Stopping Tornado Server")
        tornado.ioloop.IOLoop.instance().stop()
