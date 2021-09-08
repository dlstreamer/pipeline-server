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

import argparse
import os
import sys
from concurrent import futures
import grpc
import extension_pb2_grpc  # pylint: disable=import-error
from vaserving.vaserving import VAServing
from vaserving.common.utils.logging import get_logger
from media_graph_extension import MediaGraphExtension
from samples.ava_ai_extension.common.exception_handler import log_exception

PROGRAM_NAME = "DL Streamer Edge AI Extension"

def parse_args(args=None, program_name=PROGRAM_NAME):

    parser = argparse.ArgumentParser(
        prog=program_name,
        fromfile_prefix_chars="@",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-p",
        action="store",
        dest="port",
        help="Port number to serve gRPC server",
        type=int,
        default=int(os.getenv("PORT", "5001")),
    )

    parser.add_argument(
        "--pipeline-name",
        action="store",
        dest="pipeline_name",
        help="name of the pipeline to run",
        type=str,
        default=os.getenv("PIPELINE_NAME", "object_detection"),
    )

    parser.add_argument(
        "--pipeline-version",
        action="store",
        dest="pipeline_version",
        help="name of the pipeline to run",
        type=str,
        default=os.getenv("PIPELINE_VERSION", "person_vehicle_bike_detection"),
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        dest="debug",
        help="Use debug pipeline",
        default=(os.getenv("DEBUG_PIPELINE", None) is not None),
    )

    parser.add_argument(
        "--max-running-pipelines",
        action="store",
        dest="max_running_pipelines",
        type=int,
        default=int(os.getenv("MAX_RUNNING_PIPELINES", "10")),
    )

    if isinstance(args, dict):
        args = ["--{}={}".format(key, value) for key, value in args.items() if value]

    return parser.parse_known_args(args)


def append_default_server_args(va_serving_args, max_running_pipelines):
    va_serving_args.append("--max_running_pipelines")
    va_serving_args.append(str(max_running_pipelines))
    return va_serving_args


if __name__ == "__main__":

    args, va_serving_args = parse_args()
    logger = get_logger("Main")
    server = None
    try:
        server_args = append_default_server_args(
            va_serving_args, args.max_running_pipelines
        )

        try:
            VAServing.start(server_args)
        except Exception as error:
            logger.error(error)
            logger.error("Exception encountered during VAServing start")
            raise

        if (
                (args.pipeline_name and not args.pipeline_version)
                or (not args.pipeline_name and args.pipeline_version)
        ):
            logger.error("Pipeline name or version set but not both")
            raise ValueError('Pipeline name or version set but not both')

        # create gRPC server and start running
        server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=args.max_running_pipelines)
        )
        extension_pb2_grpc.add_MediaGraphExtensionServicer_to_server(
            MediaGraphExtension(
                args.pipeline_name,
                args.pipeline_version,
                args.debug,
            ),
            server,
        )
        server.add_insecure_port(f"[::]:{args.port}")
        logger.info("Starting %s on port: %d", PROGRAM_NAME, args.port)
        server.start()
        server.wait_for_termination()

    except (KeyboardInterrupt, SystemExit, Exception):
        log_exception()
        sys.exit(-1)
    finally:
        if server:
            server.stop(None)
        VAServing.stop()
