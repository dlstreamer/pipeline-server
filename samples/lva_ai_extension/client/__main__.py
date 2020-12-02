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
import logging
import os
import sys
import queue
import json
import cv2
from google.protobuf.json_format import MessageToDict
from samples.lva_ai_extension.common.exception_handler import log_exception
from arguments import parse_args
from media_stream_processor import MediaStreamProcessor


class ImageSource:
    def __init__(self, filename, count):
        self._image = cv2.imread(filename, cv2.IMREAD_COLOR)
        self._count = count

    def dimensions(self):
        height, width, _ = self._image.shape
        return width, height

    def get_frame(self):
        frame = self._image.tobytes() if self._count > 0 else None
        self._count -= 1
        return frame

    def close(self):
        pass


class VideoSource:
    def __init__(self, filename):
        self._vid_cap = cv2.VideoCapture(filename)

    def dimensions(self):
        height = int(self._vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(self._vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        return width, height

    def get_frame(self):
        ret, frame = self._vid_cap.read()
        return frame.tobytes() if ret else None

    def close(self):
        self._vid_cap.release()


def _log_options(args):
    heading = "Options for {}".format(os.path.basename(__file__))
    banner = "="*len(heading)
    logging.info(banner)
    logging.info(heading)
    logging.info(banner)
    for arg in vars(args):
        logging.info("{} == {}".format(arg, getattr(args, arg)))
        logging.info(banner)

def print_result(response, output):
    logging.info("Inference result {}".format(response.ack_sequence_number))
    for inference in response.media_sample.inferences:
        tag = inference.entity.tag
        box = inference.entity.box
        atrributes = []
        for attribute in inference.entity.attributes:
            attribute_string = "{}: {}".format(attribute.name, attribute.value)
            atrributes.append(attribute_string)
        logging.info("- {} ({:.2f}) [{:.2f}, {:.2f}, {:.2f}, {:.2f}] {}"\
                     .format(tag.value, tag.confidence, box.l, box.t, box.w, box.h, atrributes))
    response_dict = MessageToDict(response.media_sample)
    if response_dict.get("inferences"):
        for inference in response_dict["inferences"]:
            inference["type"] = inference["type"].lower()
    output.write("{}\n".format(json.dumps(response_dict)))

def main():
    try:
        args = parse_args()
        _log_options(args)
        frame_source = None
        frame_queue = queue.Queue()
        result_queue = queue.Queue()
        msp = MediaStreamProcessor(args.grpc_server_address,
                                   args.use_shared_memory)

        _, extension = os.path.splitext(args.sample_file)
        if extension in ['.png', '.jpg']:
            frame_source = ImageSource(args.sample_file, args.loop_count)
        elif extension in ['.mp4']:
            frame_source = VideoSource(args.sample_file)
        else:
            print("{}: unsupported file type".format(args.sample_file))
            sys.exit(1)

        width, height = frame_source.dimensions()
        print("{} {}".format(width, height))
        msp.start(width, height, frame_queue, result_queue)

        with open(args.output_file, "w") as output:
            image = frame_source.get_frame()
            while image:
                frame_queue.put(image)
                while not result_queue.empty():
                    result = result_queue.get()
                    print_result(result, output)
                image = frame_source.get_frame()
            frame_queue.put(None)

            result = result_queue.get()
            while result:
                print_result(result, output)
                result = result_queue.get()

        frame_source.close()

    except Exception:
        log_exception()
        sys.exit(-1)

if __name__ == "__main__":
    # Set logging parameters
    logging.basicConfig(
        level=logging.INFO,
        format='[AIXC] [%(asctime)-15s] [%(threadName)-12.12s] [%(levelname)s]: %(message)s',
        handlers=[
            #logging.FileHandler(LOG_FILE_NAME),    # write in a log file
            logging.StreamHandler(sys.stdout)       # write in stdout
        ]
    )

    # Call Main logic
    main()

    logging.info('Client finished execution')
