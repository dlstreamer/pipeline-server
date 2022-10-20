'''
* Copyright (C) 2019 Intel Corporation.
*
* SPDX-License-Identifier: MIT License
*
'''
import sys
import json
import argparse
import os
from urllib.parse import urlparse
import pipeline_client


def get_typed_value(value):
    try:
        return json.loads(value)
    except ValueError:
        return value

def add_common_arguments(parser):
    parser.add_argument("--show-request", action='store_true', help='Print HTTP requests and exit')
    parser.add_argument("--server-address", type=str, default="http://localhost:8080", help='Server address')

def add_instance_arguments(parser):
    parser.add_argument('pipeline', type=str, help='Pipeline name/version tuple')
    parser.add_argument('instance', type=str, help='Pipeline instance id')

def add_request_arguments(parser):
    parser.add_argument('pipeline', type=str, help='Pipeline in the form of name/version tuple')
    parser.add_argument('uri', type=str, nargs="?", default=None, help='Location of the content to play/analyze')
    parser.add_argument('--destination', action='append', nargs=2, metavar=('key', 'value'), type=str, \
        help='Update destination information with key and value pair')
    parser.add_argument('--rtsp-path', type=str, help='RTSP endpoint path')
    parser.add_argument('--webrtc-peer-id', type=str, help='WebRTC server side peer id')
    parser.add_argument('--parameter', action='append', nargs=2, metavar=('key', 'value'), type=get_typed_value, \
        dest='parameters', help='Update request parameter with key and value pair')
    parser.add_argument('--parameter-file', type=str, dest='parameter_file', help='Update request parameter \
        with key and value pairs from file. Parameters from this file take precedence over those set by --parameter')
    parser.add_argument('--request-file', type=str, dest='request_file', \
        help='Update any/all sections of request with values from file')
    parser.add_argument('--tag', action='append', nargs=2, metavar=('key', 'value'), type=str, \
        dest='tags', help='Update request tags with key and value pair')
    parser.add_argument('--number-of-streams', type=int, default=1, dest="streams", help='Set number of streams')
    parser.add_argument("--status-only", action='store_true', help='Only show status')

def parse_args(program_name="Pipeline Client"):
    """Process command line options"""
    #pylint: disable=too-many-statements
    parser = argparse.ArgumentParser(
        prog=program_name,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    subparsers = parser.add_subparsers(dest='subparsers')

    parser_run = subparsers.add_parser('run', help='Start specified pipeline with specified source. \
        Meta-data will be displayed as pipeline runs. Once pipeline ends the average fps is displayed')
    parser_run.set_defaults(command=pipeline_client.run)
    add_request_arguments(parser_run)
    add_common_arguments(parser_run)

    parser_start = subparsers.add_parser('start', help='start specified pipeline')
    parser_start.set_defaults(command=pipeline_client.start)
    add_request_arguments(parser_start)
    add_common_arguments(parser_start)

    parser_status = subparsers.add_parser('status', help='Print status of specified pipeline')
    parser_status.set_defaults(command=pipeline_client.status)
    add_instance_arguments(parser_status)
    add_common_arguments(parser_status)

    parser_wait = subparsers.add_parser('wait', help='Connect to a running pipeline and wait until completion')
    parser_wait.set_defaults(command=pipeline_client.wait)
    add_instance_arguments(parser_wait)
    add_common_arguments(parser_wait)

    parser_stop = subparsers.add_parser('stop', help='Stop a specified pipeline')
    parser_stop.set_defaults(command=pipeline_client.stop)
    add_instance_arguments(parser_stop)
    add_common_arguments(parser_stop)

    parser_list_pipelines = subparsers.add_parser('list-pipelines', help='List loaded pipelines')
    parser_list_pipelines.set_defaults(command=pipeline_client.list_pipelines)
    add_common_arguments(parser_list_pipelines)

    parser_list_models = subparsers.add_parser('list-models', help='List loaded models')
    parser_list_models.set_defaults(command=pipeline_client.list_models)
    add_common_arguments(parser_list_models)

    parser_list_instances = subparsers.add_parser('list-instances', help='List active pipeline instances')
    parser_list_instances.set_defaults(command=pipeline_client.list_instances)
    add_common_arguments(parser_list_instances)

    parser.add_argument("--quiet", action="store_false",
                        dest="verbose", default=True,
                        help="Pass this flag to reduce amount of logging.")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    if args.subparsers in ['start', 'run'] and not args.uri and not args.request_file:
        parser.error("at least one of uri or --request-file is required")

    if urlparse(args.server_address).scheme == "https" and not os.environ["ENV_CERT"]:
        parser.error("ENV_CERT environment must be set if you are using HTTPS")

    return args
