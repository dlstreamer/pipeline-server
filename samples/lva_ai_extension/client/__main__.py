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

from google.protobuf.json_format import MessageToDict
from samples.lva_ai_extension.common.exception_handler import log_exception
from arguments import parse_args
from media_stream_processor import MediaStreamProcessor


class VideoSource:
    def __init__(self, filename, loop_count):
        self._loop_count = loop_count
        self._filename = filename
        self._open_video_source()

    def _open_video_source(self):
        self._vid_cap = cv2.VideoCapture(self._filename, cv2.CAP_GSTREAMER)
        if self._vid_cap is None or not self._vid_cap.isOpened():
            logging.error("Error opening video source: {}".format(self._filename))
            sys.exit(1)

    def dimensions(self):
        width = int(self._vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self._vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return width, height

    def get_frame(self):
        ret, frame = self._vid_cap.read()
        if ret:
            return frame.tobytes()
        else:
            self._loop_count -= 1
            if self._loop_count > 0:
                self._open_video_source()
                ret, frame = self._vid_cap.read()
                if ret:
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


def _log_result(response, output, log_result=True):
    if not log_result:
        return
    if not response:
        return
    if isinstance(response, Exception):
        logging.error(response)
        return
    logging.info("Inference result {}".format(response.ack_sequence_number))
    for inference in response.media_sample.inferences:
        tag = inference.entity.tag
        box = inference.entity.box
        log_message = "- {} ({:.2f}) [{:.2f}, {:.2f}, {:.2f}, {:.2f}]"\
                     .format(tag.value, tag.confidence, box.l, box.t, box.w, box.h)
        if inference.entity.id:
            log_message += " id:{} ".format(inference.entity.id)
        attributes = []
        for attribute in inference.entity.attributes:
            attribute_string = "{}: {}".format(attribute.name, attribute.value)
            attributes.append(attribute_string)
        logging.info(
            "- {} ({:.2f}) [{:.2f}, {:.2f}, {:.2f}, {:.2f}] {}".format(
                tag.value, tag.confidence, box.l, box.t, box.w, box.h, attributes
            )
        )
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


def main():
    try:
        args = parse_args()
        _log_options(args)
        frame_delay = 1 / args.frame_rate if args.frame_rate > 0 else 0
        frame_source = None
        frame_queue = queue.Queue(args.frame_queue_size)
        result_queue = queue.Queue()
        frames_received = 0
        prev_fps_delta = 0
        start_time = None
        frame_source = VideoSource(args.sample_file, args.loop_count)
        width, height = frame_source.dimensions()
        image = frame_source.get_frame()

        if not image:
            logging.error(
                "Error getting frame from video source: {}".format(args.sample_file)
            )
            sys.exit(1)

        msp = MediaStreamProcessor(
            args.grpc_server_address,
            args.use_shared_memory,
            args.frame_queue_size,
            len(image),
        )

        msp.start(width, height, frame_queue, result_queue)

        with open(args.output_file, "w") as output:
            start_time = time.time()
            result = True
            while image and result:
                frame_queue.put(image)
                while not result_queue.empty():
                    result = result_queue.get()
                    frames_received += 1
                    prev_fps_delta = _log_fps(
                        start_time, frames_received, prev_fps_delta, args.fps_interval
                    )
                    _log_result(result, output)
                image = frame_source.get_frame()
                time.sleep(frame_delay)

            if result:
                frame_queue.put(None)
                result = result_queue.get()
            while result:
                frames_received += 1
                prev_fps_delta = _log_fps(
                    start_time, frames_received, prev_fps_delta, args.fps_interval
                )
                _log_result(result, output)
                result = result_queue.get()

        frame_source.close()
        delta = time.time() - start_time
        logging.info(
            "Start Time: {} End Time: {} Frames Recieved: {} FPS: {}".format(
                start_time,
                start_time + delta,
                frames_received,
                (frames_received / delta) if delta > 0 else None,
            )
        )

    except Exception:
        log_exception()
        sys.exit(-1)


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
    main()

    logging.info("Client finished execution")
