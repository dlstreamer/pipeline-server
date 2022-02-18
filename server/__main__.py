#!/usr/bin/env python3
'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import sys
import connexion
from server.common.utils import logging
from server.pipeline_server import PipelineServer

logger = logging.get_logger('main', is_static=True)

def main(options):
    try:
        app = connexion.App(__name__, port=options.port, specification_dir='rest_api/', server='tornado')
        app.add_api('dlstreamer-pipeline-server.yaml',
                    arguments={'title': 'Pipeline Server API'})
        logger.info("Starting Tornado Server on port: %s", options.port)
        app.run(port=options.port, server='tornado')
    except (KeyboardInterrupt, SystemExit):
        logger.info("Keyboard Interrupt or System Exit")
    except Exception as error:
        logger.error("Error Starting Tornado Server: %s", error)
    PipelineServer.stop()
    logger.info("Exiting")

if __name__ == '__main__':
    try:
        PipelineServer.start()
    except Exception as error:
        logger.error("Error Starting Pipeline Server: %s", error)
        sys.exit(1)
    try:
        main(PipelineServer.options)
    except Exception as error:
        logger.error("Unexpected Error: %s", error)
