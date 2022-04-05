#!/bin/bash -e
#
# Copyright (C) 2022 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname "$SCRIPT_DIR")

pushd $SCRIPT_DIR
docker-compose down --volumes --remove-orphans
popd
