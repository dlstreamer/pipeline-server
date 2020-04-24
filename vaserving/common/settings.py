'''
* Copyright (C) 2019 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''


# define logging settings here

LOG_LEVEL = "INFO"
LOG_ATTRS = ['levelname', 'asctime', 'message', 'name']

def set_log_level(level):
    # pylint: disable=W0603
    global LOG_LEVEL
    LOG_LEVEL = level
