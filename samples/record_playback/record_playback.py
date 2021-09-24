#!/usr/bin/python3
'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import argparse
import os
import re
import sys
import time

from pathlib import Path
import gi
gi.require_version('Gst', '1.0')
# pylint: disable=wrong-import-position
from vaserving.vaserving import VAServing
# pylint: enable=wrong-import-position

# default video folder if not provided
default_video_folder = os.path.join("/tmp", "video_output")
default_metadata_record_path = os.path.join("/tmp", "metadata.txt")

# Options for record playback app
def get_options():
    """Process command line options"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--record',
                        action='store_true',
                        help='Set the sample to record mode, record a video source into segments '\
                        'and collect inference results')
    parser.add_argument('--playback', action='store_true',
                        help='Set the sample to playback mode, playback a recorded video and '\
                        'optionally display inference results')
    parser.add_argument('--input-video-path', required=True,
                        help='(Required) Specify the input source for record or playback. Record '\
                        'does not support a directory as an input source')
    parser.add_argument('--metadata-file-path',
                        help='Optional) Specify the metadata file path to record to or read for '\
                        'playback. In record mode, default is metadata.txt')
    parser.add_argument('--output-video-folder', default=default_video_folder,
                        help='(Optional) (Record mode only) Specify the output directory for '\
                        'recorded video segments. Default is the current directory')
    parser.add_argument('--max-time', type=int, default=2000000000,
                        help='(Optional) (Record mode only) Specify the segment size based on '\
                        'time. Default is 2000000000 ns')

    return parser.parse_args()

def gst_record(options):
    # If video path is a local directory and not a uri, append file:// to the path
    if os.path.isfile(options.input_video_path):
        options_source = "file://" + options.input_video_path
    else:
        options_source = options.input_video_path

    options_metadata_file = options.metadata_file_path
    if not options_metadata_file:
        options_metadata_file = default_metadata_record_path

    # Check if have write permissions for metadata file location
    try:
        with open(options_metadata_file, 'w') as _:
            pass
    except IOError:
        print("No write permissions for metadata file location")
        return -1

    # if metadata file already exists, delete it
    if os.path.exists(options_metadata_file):
        os.remove(options_metadata_file)

    # If output video directory doesn't exist
    if not os.path.isdir(options.output_video_folder):
        os.mkdir(options.output_video_folder)

    # Check if directory has write permissions
    try:
        file_check_write_permissions = os.path.join(options.output_video_folder, "checkDirWritable.txt")
        with open(file_check_write_permissions, 'w') as _:
            pass
        os.remove(file_check_write_permissions)
    except IOError:
        print("No write permissions for video output directory")
        return -1

    # Populate the request to provide to VAServing library
    request = {
        "source": {
            "type": "uri",
            "uri": options_source
            },
        "destination": {
            "type": "file",
            "path": options_metadata_file,
            "format": "json-lines"
            },
        "parameters": {
            "recording_prefix": options.output_video_folder,
            "max-size-time": options.max_time
            }
        }

    # Start the recording, once complete, stop VAServing
    record_playback_file_dir = os.path.dirname(os.path.realpath(__file__))
    VAServing.start({'log_level': 'INFO', 'pipeline_dir': os.path.join(record_playback_file_dir, "pipelines")})
    pipeline = VAServing.pipeline("object_detection", "segment_record")
    pipeline.start(request)
    status = pipeline.status()
    while (not status.state.stopped()):
        time.sleep(0.1)
        status = pipeline.status()
    VAServing.stop()

# Used by playback
# If given a file instead of a folder to playback, check to see if file is in the
# <unix_timestamp>_<starting_pts>
# if it is, return the starting pts to use as an offset
def get_timestamp_from_filename(file_path):
    file_name = Path(file_path).stem
    #regex \d*_(\d*)\.mp4
    if re.fullmatch(r"\d*_\d*", file_name):
        match = re.search(r"\d*_(\d*)", file_name)
        start_pts = match.group(1)
        return int(start_pts)
    print("Warning, playing back video that does not conform to <unixtimestamp>_<pts> filename. "\
          "Assuming metadata file and video file timestamps match")
    return 0

def gst_playback(options):
    location = ""
    start_pts = 0
    if os.path.isdir(options.input_video_path):
        location = options.input_video_path + "/*.mp4"
    else:
        start_pts = get_timestamp_from_filename(options.input_video_path)
        location = options.input_video_path

    # Populate the request to provide to VAServing library
    module = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'preproc_callbacks/insert_metadata.py')
    metadata_args = {"metadata_file_path": options.metadata_file_path, "offset_timestamp": start_pts}
    request = {
        "source": {
            "type": "path",
            "path": location
        },
        "parameters": {
            "module": module,
            "kwarg": metadata_args
            }
        }

    # Start the recording, once complete, stop VAServing
    record_playback_file_dir = os.path.dirname(os.path.realpath(__file__))
    VAServing.start({'log_level': 'INFO', 'pipeline_dir': os.path.join(record_playback_file_dir, "pipelines")})
    pipeline = VAServing.pipeline("recording_playback", "playback")
    pipeline.start(request)
    status = pipeline.status()
    while (not status.state.stopped()):
        time.sleep(0.1)
        status = pipeline.status()
    VAServing.stop()

def launch_pipeline(options):
    """Playback the video with metadata inserted back into the video"""
    #if options.record and options.playback:
        # Error, please specify one or the other
        # TODO: Write error message and exit
    if options.record:
        # Record
        gst_record(options)
    elif options.playback:
        # Playback
        gst_playback(options)
    else:
        # Default behavior is record
        gst_record(options)

def main():
    """Program entrypoint"""
    try:
        options = get_options()
    except Exception as error:
        print(error)
        sys.exit(1)
    launch_pipeline(options)


if __name__ == "__main__":
    main()
