'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: MIT License
*
*****
*
* MIT License
*
* Copyright (c) Microsoft Corporation.
*
* Permission is hereby granted, free of charge, to any person obtaining a copy
* of this software and associated documentation files (the "Software"), to deal
* in the Software without restriction, including without limitation the rights
* to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
* copies of the Software, and to permit persons to whom the Software is
* furnished to do so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included in all
* copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
* IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
* AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
* LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
* OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
* SOFTWARE
'''

import sys
import argparse

def parse_args(args=None, program_name="DL Streamer Edge AI Extension Client"):
    parser = argparse.ArgumentParser(
        prog=program_name,
        fromfile_prefix_chars="@",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-s",
        metavar=("grpc_server_address"),
        dest="grpc_server_address",
        help="gRPC server address.",
        default=None,
    )
    parser.add_argument(
        "--server-ip",
        dest="grpc_server_ip",
        help="gRPC server ip.",
        default="localhost",
    )

    parser.add_argument(
        "--server-port",
        dest="grpc_server_port",
        help="gRPC server port.",
        type=int,
        default=5001,
    )

    parser.add_argument(
        "-f",
        "--sample-file-path",
        metavar=("sample_file"),
        dest="sample_file",
        help="Name of the sample video frame.",
        default="/home/video-analytics-serving/samples/lva_ai_extension/sampleframes/sample01.png",
    )
    parser.add_argument(
        "--max-frames",
        metavar=("max_frames"),
        dest="max_frames",
        help="How many frames to send from video.",
        type=int,
        default=sys.maxsize,
    )
    parser.add_argument(
        "-l",
        "--loop-count",
        metavar=("loop_count"),
        dest="loop_count",
        help="How many times to loop the source after it finishes.",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--fps-interval",
        dest="fps_interval",
        help="How often to report FPS (every N seconds)",
        type=int,
        default=2,
    )
    parser.add_argument(
        "--frame-rate",
        dest="frame_rate",
        help="How many frames to send per second (-1 is no limit)",
        type=int,
        default=-1,
    )
    parser.add_argument(
        "--frame-queue-size",
        dest="frame_queue_size",
        help="Max number of frames to buffer in client (0 is no limit)",
        type=int,
        default=200,
    )
    parser.add_argument(
        "-m",
        "--shared-memory",
        action="store_const",
        dest="use_shared_memory",
        const=True,
        default=False,
        help="set to use shared memory",
    )
    # nosec skips pybandit hits
    parser.add_argument(
        "-o",
        "--output-file-path",
        metavar=("output_file"),
        dest="output_file",
        help="Output file path",
        default="/tmp/results.jsonl",
    )  # nosec

    parser.add_argument(
        "--pipeline-name",
        action="store",
        dest="pipeline_name",
        help="name of the pipeline to run",
        type=str,
        default="",
    )

    parser.add_argument(
        "--pipeline-version",
        action="store",
        dest="pipeline_version",
        help="name of the pipeline to run",
        type=str,
        default="",
    )

    parser.add_argument(
        "--pipeline-parameters",
        action="store",
        dest="pipeline_parameters",
        type=str,
        default="",
    )

    parser.add_argument(
        "--pipeline-extensions",
        action="store",
        dest="pipeline_extensions",
        type=str,
        default="",
    )

    parser.add_argument(
        "--frame-destination",
        action="store",
        dest="frame_destination",
        type=str,
        default="",
    )

    parser.add_argument(
        "--extension-config",
        action="store",
        dest="extension_config",
        help="extension config in .json file path or as string",
        default="",
    )  # nosec

    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    if isinstance(args, dict):
        args = ["--{}={}".format(key, value) for key, value in args.items() if value]
    result = parser.parse_args(args)
    if not result.grpc_server_address:
        result.grpc_server_address = "{}:{}".format(
            result.grpc_server_ip, result.grpc_server_port
        )
    return result
