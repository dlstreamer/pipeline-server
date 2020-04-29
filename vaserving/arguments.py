'''
* Copyright (C) 2019 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''
import os
import argparse
import json


def parse_options(args=None):

    parser = argparse.ArgumentParser(fromfile_prefix_chars='@',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--port", action="store", type=int,
                        dest="port", default=int(os.getenv('PORT', '8080')))
    parser.add_argument("--framework", action="store", dest="framework",
                        choices=['gstreamer', 'ffmpeg'],
                        default=os.getenv('FRAMEWORK', 'gstreamer'))
    parser.add_argument("--pipeline_dir", action="store", dest="pipeline_dir",
                        type=str, default=os.getenv("PIPELINE_DIR", 'pipelines'))
    parser.add_argument("--model_dir", action="store", dest="model_dir",
                        type=str, default=os.getenv("MODEL_DIR", 'models'))
    parser.add_argument("--network_preference", action="store",
                        dest="network_preference",
                        type=str, default=os.getenv('NETWORK_PREFERENCE', '{}'))
    parser.add_argument("--max_running_pipelines", action="store",
                        dest="max_running_pipelines",
                        type=int, default=int(os.getenv('MAX_RUNNING_PIPELINES', '1')))
    parser.add_argument("--log_level", action="store",
                        dest="log_level",
                        choices=['INFO', 'DEBUG'], default=os.getenv('LOG_LEVEL', 'INFO'))
    parser.add_argument("--config_path", action="store",
                        dest="config_path",
                        default=os.getenv('CONFIG_PATH',
                                          os.path.join(os.path.dirname(__file__) + "/..")))

    if (isinstance(args, dict)):
        args = ["--{}={}".format(key, value)
                for key, value in args.items() if value]

    result = parser.parse_args(args)
    parse_network_preference(result)
    return result


def parse_network_preference(options):
    try:
        options.network_preference = json.loads(options.network_preference)
    except Exception:
        options.network_prefernce = {}
