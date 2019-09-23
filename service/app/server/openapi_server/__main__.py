#!/usr/bin/env python3
'''
* Copyright (C) 2019 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import sys
import os
import connexion
import asyncio
from openapi_server import encoder

sys.path.append(os.path.dirname(__file__) + "/../../")

from common.settings import CONFIG_PATH
from common.settings import MAX_RUNNING_PIPELINES
from modules.PipelineManager import PipelineManager
from modules.ModelManager import ModelManager
from threading import Thread

from common.utils import logging

from optparse import OptionParser

logger = logging.get_logger('main', is_static=True)


def get_options():
    parser = OptionParser()
    parser.add_option("-p", "--port", action="store", type="int", dest="port", default=8080)
    parser.add_option("--framework", action="store", dest="framework",
                      choices=['gstreamer', 'ffmpeg'], default='gstreamer')
    parser.add_option("--pipeline_dir", action="store", dest="pipeline_dir",
                      type="string", default='pipelines/gstreamer')
    parser.add_option("--model_dir", action="store", dest="model_dir",
                      type="string", default='models')

    return parser.parse_args()


def gobject_mainloop():
    from gi.repository import Gst, GObject
    mainloop = GObject.MainLoop()
    try:
        mainloop.run()
    except KeyboardInterrupt:
        pass


def main(options):
    PipelineManager.load_config(os.path.join(CONFIG_PATH, options.pipeline_dir), MAX_RUNNING_PIPELINES)
    ModelManager.load_config(os.path.join(CONFIG_PATH, options.model_dir))
    app = connexion.App(__name__, specification_dir='./openapi/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('openapi.yaml', arguments={'title': 'Video Analytics Serving API'})
    logger.info("Starting Tornado Server on port: {p}".format(p=options.port))
    app.run(server='tornado', port=options.port)


if __name__ == '__main__':

    try:
        options, args = get_options()
    except Exception as error:
        print(error)
        logger.error("Getopt Error!")
        exit(1)

    thread = Thread(target=main, args=[options])
    thread.daemon = True
    thread.start()

    if (options.framework == "gstreamer"):
        gobject_mainloop()
    else:
        thread.join()

    logger.info("Exiting")
