'''
* Copyright (C) 2022 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import sys
import json
import os
import requests

TARGET_FPS = int(os.getenv('TARGET_FPS', "-1"))
MAX_RUNNING_PIPELINES = int(os.getenv('MAX_RUNNING_PIPELINES', "-1"))
AVAILABLE = 100
NO_OF_RUNNING_PIPELINES = 0
if TARGET_FPS > 0 or MAX_RUNNING_PIPELINES > 0:
    try:
        status_all = requests.get('http://localhost:8080/pipelines/status')
        if status_all.status_code == 200:
            status_array = json.loads(status_all.text)
            for status in status_array:
                if status["state"] == "RUNNING":
                    NO_OF_RUNNING_PIPELINES += 1
                    if NO_OF_RUNNING_PIPELINES >= MAX_RUNNING_PIPELINES > 0:
                        AVAILABLE = 0
                        break
                    if status["avg_fps"] <= TARGET_FPS:
                        AVAILABLE = 0
                        break
    except Exception:
        pass

print("{}%".format(AVAILABLE))
sys.stdout.flush()
sys.exit()
