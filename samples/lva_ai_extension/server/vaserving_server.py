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

import logging
import os
import json
import time
import numpy as np
from queue import Queue

import inferencing_pb2
import media_pb2
import extension_pb2
import extension_pb2_grpc

from enum import Enum
from shared_memory import SharedMemoryManager

from vaserving.vaserving import VAServing
from vaserving.app_source import AppSource
from vaserving.app_destination import AppDestination
from vaserving.gstreamer_app_source import GStreamerAppSource
from vaserving.gstreamer_app_source import GvaFrameData
from vaserving.gstreamer_app_destination import GStreamerAppDestination

# Get debug flag from env variable (Returns None if not set)
# Set this environment variables in the IoTEdge Deployment manifest to activate debugging.
# You should also map the DebugOutputFolder on the host machine to write out the debug frames...
DEBUG = os.getenv('Debug')
DEBUG_OUTPUT_FOLDER = os.getenv('DebugOutputFolder')

class TransferType(Enum):
    BYTES = 1           # Embedded Content
    REFERENCE = 2       # Shared Memory
    HANDLE = 3          # Reserverd...

class State:
    def __init__(self, mediaStreamDescriptor):
        try:
            # media descriptor holding input data format
            self._mediaStreamDescriptor = mediaStreamDescriptor

            # Get how data will be transferred
            if self._mediaStreamDescriptor.WhichOneof("data_transfer_properties") is None:
                self._contentTransferType = TransferType.BYTES
            elif self._mediaStreamDescriptor.HasField("shared_memory_buffer_transfer_properties"):
                self._contentTransferType = TransferType.REFERENCE
            elif self._mediaStreamDescriptor.HasField("shared_memory_segments_transfer_properties"):
                self._contentTransferType = TransferType.HANDLE

            # Setup if shared mem used
            if self._contentTransferType == TransferType.REFERENCE:
                # Create shared memory accessor specific to the client
                self._sharedMemoryManager = SharedMemoryManager(
                    name=self._mediaStreamDescriptor.shared_memory_buffer_transfer_properties.handle_name,
                    size=self._mediaStreamDescriptor.shared_memory_buffer_transfer_properties.length_bytes)
            else:
                self._sharedMemoryManager = None

        except:
            print("Exception ocured in init")
            #PrintGetExceptionDetails()
            raise

class VAServingServer(extension_pb2_grpc.MediaGraphExtensionServicer):
    def __init__(self):
        return

    def GenerateMediaStreamMessageFromGVASample(self, gvaSample):
        buffer = gvaSample.sample.get_buffer()
        caps = gvaSample.sample.get_caps()
        ih = caps.get_structure(0).get_value('height')
        iw = caps.get_structure(0).get_value('width')
        messages = list(gvaSample.video_frame.messages())
        jsonMessage = json.loads(messages[0])

        msg = extension_pb2.MediaStreamMessage()
        msg.ack_sequence_number = jsonMessage["sequence_number"]
        msg.media_sample.timestamp = jsonMessage["timestamp"]
        regions = list(gvaSample.video_frame.regions())

        if regions is not None:
            for roi in regions:
                inference = msg.media_sample.inferences.add()

                attributes = []
                obj_label = None
                obj_confidence = 0
                obj_left = 0
                obj_width = 0
                obj_top = 0
                obj_width = 0

                obj_label = roi.label()
                obj_confidence = roi.confidence()
                obj_left = roi.meta().x
                obj_top = roi.meta().y
                obj_width = roi.meta().w
                obj_height = roi.meta().h
                attr_name = "object"
                attr_label = roi.label()
                attr_confidence = roi.confidence()
                attributes.append([attr_name, attr_label, attr_confidence])

                if obj_label is not None:
                    try:
                        entity = inferencing_pb2.Entity(
                                                tag = inferencing_pb2.Tag(
                                                    value = obj_label,
                                                    confidence = obj_confidence
                                                ),
                                                box = inferencing_pb2.Rectangle(
                                                    l = obj_left,
                                                    t = obj_top,
                                                    w = obj_width,
                                                    h = obj_height
                                                )
                                            )

                        for attr in attributes:
                            attribute = inferencing_pb2.Attribute(
                                name = attr[0],
                                value = attr[1],
                                confidence = attr[2]
                            )

                            entity.attributes.append(attribute)
                    except:
                        print("Exception occured in GenerateMediaStreamMessageFromGVASample")
                        #PrintGetExceptionDetails()

                    inference.entity.CopyFrom(entity)

        return msg


    def ProcessMediaSample(self, clientState, mediaStreamMessageRequest, input_queue):
        retVal = False

        try:
            # Get reference to raw bytes
            if clientState._contentTransferType == TransferType.BYTES:
                rawBytes = memoryview(mediaStreamMessageRequest.media_sample.content_bytes.bytes)
            elif clientState._contentTransferType == TransferType.REFERENCE:
                # Data sent over shared memory buffer
                addressOffset = mediaStreamMessageRequest.media_sample.content_reference.address_offset
                lengthBytes = mediaStreamMessageRequest.media_sample.content_reference.length_bytes
                
                # Get memory reference to (in readonly mode) data sent over shared memory
                rawBytes = clientState._sharedMemoryManager.ReadBytes(addressOffset, lengthBytes)

            # Get encoding details of the media sent by client
            encoding = clientState._mediaStreamDescriptor.media_descriptor.video_frame_sample_format.encoding                        

            # Handle RAW content (Just place holder for the user to handle each variation...)
            if encoding == clientState._mediaStreamDescriptor.media_descriptor.video_frame_sample_format.Encoding.RAW:
                pixelFormat = clientState._mediaStreamDescriptor.media_descriptor.video_frame_sample_format.pixel_format
                capsFormat = None

                if pixelFormat == media_pb2.VideoFrameSampleFormat.PixelFormat.RGBA:
                    capsFormat = 'RGBA'
                elif pixelFormat == media_pb2.VideoFrameSampleFormat.PixelFormat.RGB24:
                    capsFormat = 'RGB'
                elif pixelFormat == media_pb2.VideoFrameSampleFormat.PixelFormat.BGR24:
                    capsFormat = 'BGR'
                if capsFormat is not None:
                    caps = ''.join(("video/x-raw,format=",
                            capsFormat,
                            ",width=",
                            str(clientState._mediaStreamDescriptor.media_descriptor.video_frame_sample_format.dimensions.width),
                            ",height=",
                            str(clientState._mediaStreamDescriptor.media_descriptor.video_frame_sample_format.dimensions.height)))
                    new_sample = GvaFrameData(bytes(rawBytes),
                                              caps,
                                              message = {'sequence_number':mediaStreamMessageRequest.sequence_number,
                                                         'timestamp':mediaStreamMessageRequest.media_sample.timestamp})
                    retVal = input_queue.put(new_sample)
                    #TODO: determine how to send valid return value
                    #retVal = 0

            else:
                logging.info('Sample format is not RAW')
        
        except:
            print("Exception occured in ProcessMediaSample")
            #PrintGetExceptionDetails()
            raise
        
        return retVal

    # gRPC stubbed function
    # client/gRPC will call this function to send frames/descriptions
    def ProcessMediaStream(self, requestIterator, context):
        VAServing.start({'log_level': 'INFO', "ignore_init_errors":True})
        # Auto increment counter. Increases per client requests
        responseSeqNum = 1

        # First message from the client is (must be) MediaStreamDescriptor
        mediaStreamMessageRequest = next(requestIterator)

        # Extract message IDs
        requestSeqNum = mediaStreamMessageRequest.sequence_number
        requestAckSeqNum = mediaStreamMessageRequest.ack_sequence_number

        # State object per client       
        clientState = State(mediaStreamMessageRequest.media_stream_descriptor)
        
        logging.info('[Received] SeqNum: {0:07d} | AckNum: {1}\nMediaStreamDescriptor:\n{2}'.format(requestSeqNum, requestAckSeqNum, clientState._mediaStreamDescriptor))

        # First message response ...
        mediaStreamMessage =    extension_pb2.MediaStreamMessage(
                                    sequence_number = responseSeqNum,
                                    ack_sequence_number = requestSeqNum,
                                    media_stream_descriptor = extension_pb2.MediaStreamDescriptor(
                                        media_descriptor = media_pb2.MediaDescriptor(
                                            timescale = clientState._mediaStreamDescriptor.media_descriptor.timescale
                                        )
                                    )
                                )
        yield mediaStreamMessage

        detect_input = Queue()
        detect_output = Queue()
        # Start object detection pipeline
        # It will wait until it receives frames via the detect_input queue
        detect_pipeline = VAServing.pipeline("object_detection", "person_vehicle_bike_detection")
        detect_pipeline.start(source={"type": "application",
                                      "class": "GStreamerAppSource",
                                      "input": detect_input,
                                      "mode": "push"},
                              destination={"type": "application",
                                           "class": "GStreamerAppDestination",
                                           "output": detect_output,
                                           "mode": "frames"})


        # Process rest of the MediaStream message sequence
        for mediaStreamMessageRequest in requestIterator:
            try:
                # Read request id, sent by client
                requestSeqNum = mediaStreamMessageRequest.sequence_number

                logging.info('[Received] SeqNum: {0:07d}'.format(requestSeqNum))

                self.ProcessMediaSample(clientState, mediaStreamMessageRequest, detect_input)
                if context.is_active():
                    while (not detect_output.empty()):
                        gvaSample = detect_output.get()
                        mediaStreamMessage = self.GenerateMediaStreamMessageFromGVASample(gvaSample)
                        responseSeqNum += 1
                        yield mediaStreamMessage
                else:
                    break
            except:
                print("Exception occured in ProcessMediaStream")

        #After the server has finished processing all the request iterator objects
        #Push a None object into the input queue.
        #When the None object comes out of the output queue, we know we've finished processing all requests
        detect_input.put(None)
        returned_output = detect_output.get()
        while (returned_output != None):
            gvaSample = returned_output
            mediaStreamMessage = self.GenerateMediaStreamMessageFromGVASample(gvaSample)
            yield mediaStreamMessage
            returned_output = detect_output.get()
        VAServing.stop()

        #print("Done processing messages")
        logging.info('Done processing messages')
        logging.info('MediaStreamDescriptor:\n{0}'.format(clientState._mediaStreamDescriptor))        
