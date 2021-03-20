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
import template

def parse_args(program_name="Video Analytics Serving Client"):
    """Process command line options"""
    parser = argparse.ArgumentParser(
        prog=program_name,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--pipeline", action="store", dest="pipeline",
                        default="object_detection",
                        help="One of the supported pipelines you want to launch; "
                             "e.g., 'object_detection' or 'emotion_recognition'.")
    parser.add_argument("--version", action="store", dest="version",
                        default="1",
                        help="Version associated with the pipeline to launch; "
                             "e.g., '1' or '2'.")
    parser.add_argument("--source", action="store", dest="source",
                        default=template.REQUEST_TEMPLATE['source']['uri'],
                        help="Location of the content to play/analyze.")
    parser.add_argument("--destination", action="store", dest="destination",
                        default=template.REQUEST_TEMPLATE['destination']['path'],
                        help="Output file for storing analysis results.")
    parser.add_argument("--repeat", action="store", dest="repeat",
                        type=int, default=1,
                        help="Number of times to launch this pipeline.")
    parser.add_argument("--quiet", action="store_false",
                        dest="verbose", default=True,
                        help="Pass this flag to reduce amount of logging.")
    parser.add_argument("--list-pipelines", action="store_true",
                        default=False,
                        help="Pass this flag to get supported pipelines.")
    parser.add_argument("--list-models", action="store_true",
                        default=False,
                        help="Pass this flag to get supported models.")

    return parser.parse_args()
