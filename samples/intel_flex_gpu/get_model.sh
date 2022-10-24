#!/bin/bash -e
#
# Copyright (C) 2022 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

SOURCE_DIR=$(dirname "$(readlink -f "$0")")

model_dir=$SOURCE_DIR/models/object_detection/ssdlite_mobilenet_v2
mkdir -p $model_dir/FP16-INT8
wget https://github.com/dlstreamer/pipeline-zoo-models/raw/main/storage/ssdlite_mobilenet_v2_INT8/FP16-INT8/ssdlite_mobilenet_v2.bin -P $model_dir/FP16-INT8
wget https://github.com/dlstreamer/pipeline-zoo-models/raw/main/storage/ssdlite_mobilenet_v2_INT8/FP16-INT8/ssdlite_mobilenet_v2.xml -P $model_dir/FP16-INT8
wget https://github.com/dlstreamer/pipeline-zoo-models/raw/main/storage/ssdlite_mobilenet_v2_INT8/ssdlite_mobilenet_v2.json -P $model_dir

