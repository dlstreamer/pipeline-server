#!/bin/bash -e
#
# Copyright (C) 2022 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname "$SCRIPT_DIR")

pushd $SCRIPT_DIR
export USER_ID=$UID
export GROUP_ID=$GID
docker-compose up -d
popd
