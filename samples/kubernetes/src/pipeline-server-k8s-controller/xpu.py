#!/usr/bin/env python3
'''
* Copyright (C) 2022 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''
from enum import Enum, auto

class Xpu(Enum):
    CPU = auto()
    GPU = auto()
