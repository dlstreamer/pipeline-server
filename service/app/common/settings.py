'''
* Copyright (C) 2019 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

"""
    define service level settings for Video Analytics Serving here
"""

import os

CONFIG_PATH = os.path.dirname(__file__) + "/../../"
MAX_RUNNING_PIPELINES = 1

LOG_LEVEL = "INFO"
LOG_ATTRS = ['levelname', 'asctime', 'message', 'name']
