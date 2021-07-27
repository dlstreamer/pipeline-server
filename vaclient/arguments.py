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
import vaclient

def parse_args(program_name="Video Analytics Serving Client"):
    """Process command line options"""
    parser = argparse.ArgumentParser(
        prog=program_name,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    subparsers = parser.add_subparsers()

    parser_run = subparsers.add_parser('run', help='Start specified pipeline with specified source. \
        Meta-data will be displayed as pipeline runs. Once pipeline ends the average fps is displayed')
    parser_run.set_defaults(command=vaclient.run)
    parser_run.add_argument('pipeline', type=str, help='Vaserving pipeline which to run instance of. \
        In the form of pipeline_name/pipeline_version')
    parser_run.add_argument('uri', type=str, help='Location of the content to play/analyze')
    parser_run.add_argument('--destination', action='append', nargs=2, metavar=('key', 'value'), type=str, \
        help='Update destination information with key and value pair')
    parser_run.add_argument('--rtsp-path', type=str, help='RTSP endpoint path')
    parser_run.add_argument('--parameter', action='append', nargs=2, metavar=('key', 'value'), type=str, \
        dest='parameters', help='Update request parameter with key and value pair')
    parser_run.add_argument('--parameter-file', type=str, dest='parameter_file', help='Update request parameter \
        with key and value pairs from file. Parameters from this file take precedence over those set by --parameter')
    parser_run.add_argument('--tag', action='append', nargs=2, metavar=('key', 'value'), type=str, \
        dest='tags', help='Update request tags with key and value pair')
    parser_run.add_argument("--show-request", action='store_true', help='Print HTTP requests and exit')

    parser_start = subparsers.add_parser('start', help='start specified pipeline')
    parser_start.set_defaults(command=vaclient.start)
    parser_start.add_argument('pipeline', type=str, help='Vaserving pipeline which to run instance of. \
        In the form of pipeline_name/pipeline_version')
    parser_start.add_argument('uri', type=str, help='Location of the content to play/analyze')
    parser_start.add_argument('--destination', action='append', nargs=2, metavar=('key', 'value'), type=str, \
        help='Update destination information with key and value pair')
    parser_start.add_argument('--rtsp-path', type=str, help='RTSP endpoint path')
    parser_start.add_argument('--parameter', action='append', nargs=2, metavar=('key', 'value'), type=str, \
        dest='parameters', help='Update requeset parameter with key and value pair')
    parser_start.add_argument('--parameter-file', type=str, dest='parameter_file', help='Update request parameter \
        with key and value pairs from file. Parameters from this file take precedence over those set by --parameter')
    parser_start.add_argument('--tag', action='append', nargs=2, metavar=('key', 'value'), type=str, \
        dest='tags', help='Update request tags with key and value pair')
    parser_start.add_argument("--show-request", action='store_true', help='Print HTTP requests and exit')

    parser_status = subparsers.add_parser('status', help='Print status of specified pipeline')
    parser_status.set_defaults(command=vaclient.status)
    parser_status.add_argument('pipeline', type=str, \
        help='Vaserving pipeline_name/pipeline_version which to get status of')
    parser_status.add_argument('instance', type=int, help='Pipeline instance id which to get status of.')
    parser_status.add_argument("--show-request", action='store_true', help='Print HTTP requests and exit')

    parser_wait = subparsers.add_parser('wait', help='Connect to a running pipeline and wait until completion')
    parser_wait.set_defaults(command=vaclient.wait)
    parser_wait.add_argument('pipeline', type=str, help='Vaserving pipeline_name/pipeline_version which to wait on')
    parser_wait.add_argument('instance', type=int, help='Pipeline instance id which to wait on')
    parser_wait.add_argument("--show-request", action='store_true', help='Print HTTP requests and exit')

    parser_stop = subparsers.add_parser('stop', help='Stop a specified pipeline')
    parser_stop.set_defaults(command=vaclient.stop)
    parser_stop.add_argument('pipeline', type=str, help='Vaserving pipeline_name/pipeline_version which to stop')
    parser_stop.add_argument('instance', type=int, help='Pipeline instance id which to stop')
    parser_stop.add_argument("--show-request", action='store_true', help='Print HTTP requests and exit')

    parser_list_pipelines = subparsers.add_parser('list-pipelines', help='List pipelines that are loaded by vaserving')
    parser_list_pipelines.set_defaults(command=vaclient.list_pipelines)
    parser_list_pipelines.add_argument("--show-request", action='store_true', help='Print HTTP requests and exit')

    parser_list_models = subparsers.add_parser('list-models', help='List models that are loaded by vaserving')
    parser_list_models.set_defaults(command=vaclient.list_models)
    parser_list_models.add_argument("--show-request", action='store_true', help='Print HTTP requests and exit')

    parser.add_argument("--quiet", action="store_false",
                        dest="verbose", default=True,
                        help="Pass this flag to reduce amount of logging.")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return parser.parse_args()
