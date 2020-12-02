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
from media_graph_extension import MediaGraphExtension


def parse_args(args=None, program_name="VA Serving AI Extension"):

    parser = argparse.ArgumentParser(prog=program_name, fromfile_prefix_chars='@',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-p", action="store", dest="port",
                        help='Port number to serve gRPC server',
                        type=int, default=int(os.getenv('PORT', "5001")))

    parser.add_argument("--pipeline-name", action="store",
                        dest="pipeline",
                        help='name of the pipeline to run',
                        type=str, default=os.getenv('PIPELINE_NAME',
                                                    'object_detection'))

    parser.add_argument("--pipeline-version", action="store",
                        dest="version",
                        help='name of the pipeline to run',
                        type=str, default=os.getenv('PIPELINE_VERSION',
                                                    'person_vehicle_bike_detection'))
    parser.add_argument("--debug", action="store_true",
                        dest="debug",
                        help='Use debug pipeline',
                        default=(os.getenv('DEBUG_PIPELINE', None) is not None))

    parser.add_argument("--max-running-pipelines", action="store",
                        dest="max_running_pipelines",
                        type=int, default=int(os.getenv('MAX_RUNNING_PIPELINES', '10')))

    parser.add_argument("--parameters", action="store",
                        dest="parameters",
                        type=str, default=os.getenv('PARAMETERS', '{}'))

    if (isinstance(args, dict)):
        args = ["--{}={}".format(key, value)
                for key, value in args.items() if value]

    return parser.parse_args(args)

if __name__ == "__main__":

    args = parse_args()
    try:
        VAServing.start({'log_level': 'INFO', "ignore_init_errors":True,
                         'max_running_pipelines': args.max_running_pipelines})

        # create gRPC server and start running
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=args.max_running_pipelines))
        extension_pb2_grpc.add_MediaGraphExtensionServicer_to_server(
            MediaGraphExtension(args.pipeline, args.version, args.debug, args.parameters), server)
        server.add_insecure_port(f'[::]:{args.port}')
        print("Starting Protocol Server Application on port", args.port)
        server.start()
        server.wait_for_termination()
        VAServing.stop()

    except Exception:
        VAServing.stop()
        sys.exit(-1)
