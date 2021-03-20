#!/usr/bin/python3
'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

#nosec skips pybandit hits
REQUEST_TEMPLATE = {
    "source": {
        "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true",
        "type": "uri"
    },
    "destination": {
        "path": "/tmp/results.txt",  # nosec
        "type": "file",
        "format": "json-lines"
    }
}
