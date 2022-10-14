#!/bin/bash -e
#
# Copyright (C) 2022 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

docker rm -f nginx || true
docker network rm my_bridge
