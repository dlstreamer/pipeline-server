#!/usr/bin/env python3
'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import sys
from threading import Thread
import connexion

from vaserving.common.utils import logging
from vaserving.vaserving import VAServing

logger = logging.get_logger('main', is_static=True)


def main(options):
    try:
        app = connexion.App(__name__, specification_dir='rest_api/')
        app.add_api('video-analytics-serving.yaml',
                    arguments={'title': 'Video Analytics Serving API'})
        logger.info("Starting Tornado Server on port: %s", options.port)
        app.run(server='tornado', port=options.port)
    except Exception as error:
        logger.error("Error Starting Tornado Server")
        

if __name__ == '__main__':

    try:
        VAServing.start()
    except Exception as error:
        print(error)
        logger.error("Getopt Error!")
        sys.exit(1)

    thread = Thread(target=main, args=[VAServing.options])
    thread.daemon = True
    thread.start()

    thread.join()

    VAServing.stop()

    logger.info("Exiting")
