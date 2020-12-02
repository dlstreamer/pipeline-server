'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import os

mo_root = "/opt/intel/dldt" if os.path.isdir("/opt/intel/dldt") else "/opt/intel/openvino/deployment_tools"
omz_root = os.path.join(mo_root, "open_model_zoo")

model_downloader = os.path.join(omz_root, "tools/downloader/downloader.py")
model_converter = os.path.join(omz_root, "tools/downloader/converter.py")
model_optimizer = os.path.join(mo_root, "model-optimizer/mo.py") \
    if mo_root == "/opt/intel/dldt" else os.path.join(mo_root, "model_optimizer/mo.py")
model_proc_root = "/opt/intel/dl_streamer/samples/model_proc"

base_gst_video_analytics_repo_root = "https://raw.githubusercontent.com/openvinotoolkit/dlstreamer_gst"
base_gst_video_analytics_version = "v1.2.1"
base_gst_video_analytics_repo_url = "{root}/{version}/samples/model_proc/"\
    .format(root=base_gst_video_analytics_repo_root, version=base_gst_video_analytics_version)
