#!/usr/bin/python3
'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import argparse
import json
import os
import re
import sys
import time

from pathlib import Path
import gi
gi.require_version('Gst', '1.0')
# pylint: disable=wrong-import-position
from gi.repository import GObject, Gst
from vaserving.vaserving import VAServing
# pylint: enable=wrong-import-position

Gst.init(sys.argv)

# global variable for videoconvert so that decodebin can link to it
global videoconvert1

# default video folder if not provided
current_dir = os.getcwd()
default_video_folder = os.path.join(current_dir, "video_output")
default_metadata_record_path = os.path.join(current_dir, "metadata.txt")

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

    # Populate the request to provide to VAServing library
    string_request = ('{{'
                      '"source": {{'
                      '"type": "uri",'
                      '"uri": "{source}"'
                      '}},'
                      '"destination": {{'
                      '"type": "file",'
                      '"path": "{fp}",'
                      '"format": "json-lines"'
                      '}},'
                      '"parameters": {{'
                      '"recording_prefix": "{output_video_folder}",'
                      '"max-size-time": {max_size_chunks}'
                      '}}'
                      '}}')
    string_request = string_request.format(source=options_source,
                                           fp=options_metadata_file,
                                           output_video_folder=options.output_video_folder,
                                           max_size_chunks=options.max_time)
    request = json.loads(string_request)

    # Start the recording, once complete, stop VAServing
    VAServing.start({'log_level': 'INFO'})
    pipeline = VAServing.pipeline("object_detection", "2")
    pipeline.start(request)
    status = pipeline.status()
    while (not status.state.stopped()):
        time.sleep(0.1)
        status = pipeline.status()
    VAServing.stop()

# Used by playback
# Gst msgbus callback to determine if error or end-of-stream occured
def on_message(_: Gst.Bus, message: Gst.Message, loop: GObject.MainLoop):
    message_type = message.type
    if message_type == Gst.MessageType.EOS:
        print("End of stream")
        loop.quit()

    elif message_type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(err, debug)
        loop.quit()

    return True

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

# Used by playback
def create_missing_output_directory(options):
    if not os.path.exists(options.output_video_folder):
        os.mkdir(options.output_video_folder)

# Used by playback
# Dynamically link decodebin to the videoconvert element
def decodebin_pad_added(_, pad):
    string = pad.query_caps(None).to_string()
    if string.startswith('video/x-raw'):
        pad.link(videoconvert1.get_static_pad('sink'))

# Create a Gstreamer Playback Pipeline
def create_gst_playback_pipeline(options):
    global videoconvert1
    # PIPELINE="splitfilesrc ! decodebin ! videoconvert ! video/x-raw,format=BGRx ! \
    # gvapython module=insert_metadata.py ! \
    # gvawatermark ! videoconvert ! ximagesink"
    pipeline = Gst.Pipeline()

    start_pts = 0
    if os.path.isdir(options.input_video_path):
        src = Gst.ElementFactory.make("splitfilesrc")
        src.set_property("location", options.input_video_path + "/*.mp4")
    else:
        src = Gst.ElementFactory.make("filesrc")
        start_pts = get_timestamp_from_filename(options.input_video_path)
        src.set_property("location", options.input_video_path)

    decodebin = Gst.ElementFactory.make("decodebin")
    videoconvert1 = Gst.ElementFactory.make("videoconvert")
    capsfilter = Gst.ElementFactory.make("capsfilter")
    caps = Gst.caps_from_string("video/x-raw, format=(string){BGRx}")
    capsfilter.set_property("caps", caps)

    # Attach the insert_metadata module to gvapython
    play_script_dir = os.path.dirname(os.path.abspath(__file__))
    insert_metadata_script = os.path.join(play_script_dir, 'preproc_callbacks/insert_metadata.py')
    gvapython = Gst.ElementFactory.make("gvapython")
    gvapython.set_property("module", insert_metadata_script)
    gvapython.set_property("class", "FrameInfo")

    insert_preproc_metadata_arguments = '{{ "metadata_file_path" : "{input_file}" , '\
                                        '"offset_timestamp" : {timestamp} }}'
    insert_preproc_metadata_arguments = insert_preproc_metadata_arguments.format(
        input_file=options.metadata_file_path, timestamp=start_pts)
    gvapython.set_property("kwarg", insert_preproc_metadata_arguments)

    gvawatermark = Gst.ElementFactory.make("gvawatermark")
    videoconvert2 = Gst.ElementFactory.make("videoconvert")
    ximagesink = Gst.ElementFactory.make("ximagesink")

    pipeline.add(src, decodebin, videoconvert1, capsfilter, gvapython, gvawatermark,
                 videoconvert2, ximagesink)

    src.link(decodebin)

    # dynamic linking for decodebin
    decodebin.connect("pad-added", decodebin_pad_added)

    # link the rest of the elements
    videoconvert1.link(capsfilter)
    capsfilter.link(gvapython)
    gvapython.link(gvawatermark)
    gvawatermark.link(videoconvert2)
    videoconvert2.link(ximagesink)

    return pipeline

def gst_playback(options):
    # Playback
    pipeline = create_gst_playback_pipeline(options)

    bus = pipeline.get_bus()
    bus.add_signal_watch()
    pipeline.set_state(Gst.State.PLAYING)
    loop = GObject.MainLoop()
    bus.connect("message", on_message, loop)

    try:
        loop.run()
    except Exception:
        loop.quit()

    pipeline.set_state(Gst.State.NULL)
    del pipeline

# Playback video
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
