'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''


# define logging settings here

LOG_LEVEL = "INFO"
LOG_ATTRS = ['levelname', 'asctime', 'message', 'module']


def set_log_level(level):
    # pylint: disable=global-statement
    global LOG_LEVEL
    LOG_LEVEL = level
