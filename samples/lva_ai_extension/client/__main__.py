"""
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
"""
import logging
import os
import sys
import queue
import json
import time
import cv2
import jsonschema

from google.protobuf.json_format import MessageToDict
import samples.lva_ai_extension.common.grpc_autogen.inferencing_pb2 as inferencing_pb2
from samples.lva_ai_extension.common.exception_handler import log_exception
import samples.lva_ai_extension.common.extension_schema as extension_schema
from arguments import parse_args
from media_stream_processor import MediaStreamProcessor


class VideoSource:
    def __init__(self, filename, loop_count, scale_factor = 1.0):
        self._loop_count = loop_count
        self._filename = filename
        self._scale_factor = scale_factor
        self._open_video_source()

    def _open_video_source(self):
        self._vid_cap = cv2.VideoCapture(self._filename, cv2.CAP_GSTREAMER)
        if self._vid_cap is None or not self._vid_cap.isOpened():
            raise Exception("Error opening video source: {}".format(self._filename))

    def dimensions(self):
        width = int(self._vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH) * self._scale_factor)
        height = int(self._vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * self._scale_factor)
        return width, height

    def get_frame(self):
        ret, frame = self._vid_cap.read()
        if ret:
            width = int(self._vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH) * self._scale_factor)
            height = int(self._vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * self._scale_factor)
            dsize = (width, height)
            frame = cv2.resize(frame, dsize)
            return frame.tobytes()
        self._loop_count -= 1
        if self._loop_count > 0:
            self._open_video_source()
            ret, frame = self._vid_cap.read()
            if ret:
                width = int(self._vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH) * self._scale_factor)
                height = int(self._vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * self._scale_factor)
                dsize = (width, height)
                frame = cv2.resize(frame, dsize)
                return frame.tobytes()
        return None

    def close(self):
        self._vid_cap.release()


def _log_options(args):
    heading = "Options for {}".format(os.path.basename(__file__))
    banner = "=" * len(heading)
    logging.info(banner)
    logging.info(heading)
    logging.info(banner)
    for arg in vars(args):
        logging.info("{} == {}".format(arg, getattr(args, arg)))
        logging.info(banner)

def _log_entity(inference):
    tag = inference.entity.tag
    box = inference.entity.box
    attributes = []
    if inference.inference_id:
        attribute_string = "{}: {}".format('inferenceId', inference.inference_id)
        attributes.append(attribute_string)
    if inference.subtype:
        attribute_string = "{}: {}".format('subtype', inference.subtype)
        attributes.append(attribute_string)
    if inference.entity.id:
        attribute_string = "{}: {}".format('id', inference.entity.id)
        attributes.append(attribute_string)
    for attribute in inference.entity.attributes:
        attribute_string = "{}: {}".format(attribute.name, attribute.value)
        attributes.append(attribute_string)
    logging.info(
        "ENTITY - {} ({:.2f}) [{:.2f}, {:.2f}, {:.2f}, {:.2f}] {}".format(
            tag.value, tag.confidence, box.l, box.t, box.w, box.h, attributes
        )
    )

def _log_event(inference):
    name = inference.event.name
    attributes = []
    if inference.inference_id:
        attribute_string = "{}: {}".format('inferenceId', inference.inference_id)
        attributes.append(attribute_string)
    if inference.subtype:
        attribute_string = "{}: {}".format('subtype', inference.subtype)
        attributes.append(attribute_string)
    if inference.related_inferences:
        attribute_string = "{}: {}".format('relatedInferences', inference.related_inferences)
        attributes.append(attribute_string)
    for attribute in inference.event.properties:
        attribute_string = "{}: {}".format(attribute, inference.event.properties[attribute])
        attributes.append(attribute_string)
    logging.info(
        "EVENT - {}: {}".format(name, attributes)
    )
def _log_result(response, output, log_result=True):
    if not log_result:
        return
    if not response:
        return
    logging.debug("Inference result {}".format(response.ack_sequence_number))
    for inference in response.media_sample.inferences:
        if inference.type == inferencing_pb2.Inference.InferenceType.ENTITY: # pylint: disable=no-member
            _log_entity(inference)

        if inference.type == inferencing_pb2.Inference.InferenceType.EVENT: # pylint: disable=no-member
            _log_event(inference)

    # default value field is used to avoid not including values set to 0,
    # but it also causes empty lists to be included
    returned_dict = MessageToDict(
        response.media_sample, including_default_value_fields=True
    )
    output.write("{}\n".format(json.dumps(returned_dict)))

def _log_fps(start_time, frames_received, prev_fps_delta, fps_interval):
    delta = int(time.time() - start_time)
    if (fps_interval > 0) and (delta != prev_fps_delta) and (delta % fps_interval == 0):
        logging.info(
            "FPS: {} Frames Recieved: {}".format(
                (frames_received / delta), frames_received
            )
        )
        return delta
    return prev_fps_delta

def validate_extension_config(extension_config):
    try:
        validator = jsonschema.Draft4Validator(schema=extension_schema.extension_config,
                                               format_checker=jsonschema.draft4_format_checker)
        validator.validate(extension_config)
    except jsonschema.exceptions.ValidationError as err:
        raise Exception("Error validating pipeline request: {},: error: {}".format(extension_config, err.message))

def create_extension_config(args):
    extension_config = {}
    pipeline_config = {}
    if args.pipeline_name:
        pipeline_config["name"] = args.pipeline_name
    if args.pipeline_version:
        pipeline_config["version"] = args.pipeline_version
    if args.pipeline_parameters:
        try:
            pipeline_config["parameters"] = json.loads(args.pipeline_parameters)
        except ValueError:
            raise Exception("Issue loading pipeline parameters: {}".format(args.pipeline_parameters))
    if args.frame_destination:
        try:
            pipeline_config["frame-destination"] = json.loads(args.frame_destination)
        except ValueError:
            raise Exception("Issue loading frame destination: {}".format(args.frame_destination))
    if args.pipeline_extensions:
        try:
            pipeline_config["pipeline_extensions"] = json.loads(args.pipeline_extensions)
        except ValueError:
            raise Exception("Issue loading pipeline extensions: {}".format(args.pipeline_extensions))

    if len(pipeline_config) > 0:
        extension_config.setdefault("pipeline", pipeline_config)

    return extension_config

def main():
    msp = None
    frame_source = None
    try:
        args = parse_args()
        _log_options(args)
        frame_delay = 1 / args.frame_rate if args.frame_rate > 0 else 0
        frame_queue = queue.Queue(args.frame_queue_size)
        result_queue = queue.Queue()
        frames_sent = 0
        frames_received = 0
        prev_fps_delta = 0
        start_time = None
        frame_source = VideoSource(args.sample_file, args.loop_count, args.scale_factor)
        width, height = frame_source.dimensions()
        image = frame_source.get_frame()

        if not image:
            raise Exception("Error getting frame from video source: {}".format(args.sample_file))

        extension_config = {}
        if args.extension_config:
            if args.extension_config.endswith(".json"):
                with open(args.extension_config, "r") as config:
                    extension_config = json.loads(config.read())
            else:
                extension_config = json.loads(args.extension_config)
        else:
            extension_config = create_extension_config(args)

        validate_extension_config(extension_config)
        logging.info("Extension Configuration: {}".format(extension_config))

        msp = MediaStreamProcessor(
            args.grpc_server_address,
            args.use_shared_memory,
            args.frame_queue_size,
            len(image),
        )

        msp.start(width, height, frame_queue, result_queue, json.dumps(extension_config))

        with open(args.output_file, "w") as output:
            start_time = time.time()
            result = True
            while image and result and frames_sent < args.max_frames:
                frame_queue.put(image)
                while not result_queue.empty():
                    result = result_queue.get()
                    if isinstance(result, Exception):
                        raise result
                    frames_received += 1
                    prev_fps_delta = _log_fps(
                        start_time, frames_received, prev_fps_delta, args.fps_interval
                    )
                    _log_result(result, output)
                image = frame_source.get_frame()
                time.sleep(frame_delay)
                frames_sent += 1

            if result:
                frame_queue.put(None)
                result = result_queue.get()
            while result:
                if isinstance(result, Exception):
                    raise result
                frames_received += 1
                prev_fps_delta = _log_fps(
                    start_time, frames_received, prev_fps_delta, args.fps_interval
                )
                _log_result(result, output)
                result = result_queue.get()

        delta = time.time() - start_time
        logging.info(
            "Start Time: {} End Time: {} Frames: Tx {} Rx {} FPS: {}".format(
                start_time,
                start_time + delta,
                frames_sent,
                frames_received,
                (frames_received / delta) if delta > 0 else None,
            )
        )

        if frames_sent != frames_received:
            raise Exception("Sent {} requests, received {} responses".format(
                frames_sent, frames_received))

        return True

    except (KeyboardInterrupt, SystemExit, Exception):
        log_exception()
        return False
    finally:
        if msp:
            msp.stop()
        if frame_source:
            frame_source.close()

if __name__ == "__main__":
    # Set logging parameters
    logging.basicConfig(
        level=logging.INFO,
        format="[AIXC] [%(asctime)-15s] [%(threadName)-12.12s] [%(levelname)s]: %(message)s",
        handlers=[
            # logging.FileHandler(LOG_FILE_NAME),    # write in a log file
            logging.StreamHandler(sys.stdout)  # write in stdout
        ],
    )

    # Call Main logic
    if not main():
        sys.exit(1)
    logging.info("Client finished execution")
