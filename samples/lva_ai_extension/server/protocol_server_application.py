'''
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

'''
* Copyright (C) 2019 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import os
import json
import time
import resource
import subprocess
import argparse
import shutil
import gi
from queue import Queue
from gstgva.util import libgst, gst_buffer_data, GVAJSONMeta
from gstgva.video_frame import VideoFrame
from threading import Thread
from contextlib import contextmanager

from vaserving_server import VAServingServer
import grpc
import extension_pb2_grpc
from concurrent import futures

# pylint: disable=wrong-import-order, wrong-import-position
gi.require_version('Gst', '1.0')
gi.require_version('GstApp', '1.0')
from gi.repository import Gst, GstApp
# pylint: enable=wrong-import-order, wrong-import-position

source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))

def parse_args(args=None,program_name="Protocol Server Application Sample"):

    parser = argparse.ArgumentParser(prog=program_name,fromfile_prefix_chars='@',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-p', nargs=1, metavar=('grpc_server_port'),
                                    help='Port number to serve gRPC server')

    if (isinstance(args, dict)):
        args = ["--{}={}".format(key, value)
                for key, value in args.items() if value]

    return parser.parse_args(args)


if __name__=="__main__":

    args = parse_args()
    try:
        grpcServerPort = 0
        if (args.p is not None):
            grpcServerPort = args.p[0]
        else:
            grpcServerPort = 5001
        # create gRPC server and start running
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=3))
        extension_pb2_grpc.add_MediaGraphExtensionServicer_to_server(VAServingServer(), server)
        server.add_insecure_port(f'[::]:{grpcServerPort}')
        print("Starting Protocol Server Application")
        server.start()
        server.wait_for_termination()
    except:
        exit(-1)

