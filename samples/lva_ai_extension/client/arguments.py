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

def parse_args(args=None, program_name="AI Extension Sample Client"):
    parser = argparse.ArgumentParser(prog=program_name, fromfile_prefix_chars='@',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-s', metavar=('grpc_server_address'),
                        dest="grpc_server_address",
                        help='gRPC server address.',
                        default="localhost:5001")
    parser.add_argument('-f', metavar=('sample_file'),
                        dest="sample_file",
                        help='Name of the sample video frame.',
                        default="/home/video-analytics-serving/samples/lva_ai_extension/sampleframes/sample01.png")
    parser.add_argument('-l', metavar=('loop_count'),
                        dest="loop_count",
                        help='How many times to send sample video frame.',
                        type=int,
                        default=1)
    parser.add_argument('-m', action='store_const',
                        dest='use_shared_memory',
                        const=True,
                        default=False,
                        help='set to use shared memory')
    #nosec skips pybandit hits
    parser.add_argument('-o', metavar=('output_file'),
                        dest="output_file",
                        help='Output file path',
                        default="/tmp/results.jsonl")  # nosec
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    if (isinstance(args, dict)):
        args = ["--{}={}".format(key, value)
                for key, value in args.items() if value]
    return parser.parse_args(args)
