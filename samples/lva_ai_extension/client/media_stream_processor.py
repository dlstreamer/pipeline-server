'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: MIT License
'''

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

import grpc
import logging
import cv2
import os
import time

import json
from google.protobuf.json_format import MessageToDict

from samples.lva_ai_extension.common.exception_handler import log_exception
from samples.lva_ai_extension.common.shared_memory import SharedMemoryManager

import samples.lva_ai_extension.common.grpc_autogen.media_pb2 as media_pb2
import samples.lva_ai_extension.common.grpc_autogen.extension_pb2 as extension_pb2
import samples.lva_ai_extension.common.grpc_autogen.extension_pb2_grpc as extension_pb2_grpc


class MediaStreamProcessor:
    class RequestGenerator():
        def __init__(self, parent):
            try:
                self._request_seq_num = 1
                self._media_stream_processor = parent

                self._descriptor_sent = False
            except:
                log_exception()
                raise

        def __iter__(self):
            return self

        def __next__(self):
            request = None
            if not self._descriptor_sent:
                # Return first message
                request = self._media_stream_processor.get_media_stream_descriptor_message(
                    self._request_seq_num)
                self._descriptor_sent = True
            else:
                if self._media_stream_processor.loop_count > 0:
                    request = self._media_stream_processor.get_media_sample_message(
                        self._request_seq_num)
                    self._media_stream_processor.loop_count -= 1
                else:
                    raise StopIteration

            self._request_seq_num += 1
            return request

    def __init__(self, grpc_server_address,
                 media_source_address,
                 loop_count,
                 use_shared_memory):
        try:
            self._grpc_server_address = grpc_server_address  # Full address including port number i.e. "localhost:44001"
            self._media_source_address = media_source_address # Full path to video file name, IP Camera address
            self.loop_count = loop_count # how many time the sample will be send to aix server
            self._use_shared_memory = use_shared_memory

            # Just make the sample frame ready to be sent to inference server
            self._image = cv2.imread(media_source_address, cv2.IMREAD_COLOR)
            self._height, self._width, _ = self._image.shape
            # AIX Server sample requires the images sent to pre-sized as 416x416 size. This size is requirement by Tiny Yolo V3.
            # You may prefer to update the sample server code to resize the received images into 416x416 independent from their original
            # size. But since LVA have the capability of sending any size image requested, why create redundent computation cycle?
            # So in this aix_client (which mimics LVA), we resize the sample video frames into 416x416 size.
#            self._cvImageSampleFrame = cv2.resize(self._cvImageSampleFrame, (416, 416), interpolation = cv2.INTER_AREA)

            # Shared Memory Manager to share data, keep track of reserved/released memory slots
            self._shared_memory_manager = SharedMemoryManager(os.O_RDWR | os.O_SYNC | os.O_CREAT,
                                                              name=None,
                                                              size=100*1024*1024) # auto name will be assigned

            # Create grpc commmunication channel / stub
            self._grpc_channel = grpc.insecure_channel(self._grpc_server_address)
            self._grpc_stub = extension_pb2_grpc.MediaGraphExtensionStub(
                self._grpc_channel)

            self._request_generator = self.RequestGenerator(self)

        except:
            log_exception()
            raise


    def get_media_stream_descriptor_message(self, sequence_number):
        msd_message = None
        try:
            smbtp = None                # shared_memory_buffer_transfer_properties
            if self._use_shared_memory:
                smbtp = extension_pb2.SharedMemoryBufferTransferProperties(
                    handle_name=self._shared_memory_manager.shm_file_name,
                    length_bytes=self._shared_memory_manager.shm_file_size
                )
            msd_message = extension_pb2.MediaStreamMessage(
                sequence_number=sequence_number,    # Counter, starting at 1
                ack_sequence_number=0,             # Initial value is 0

                media_stream_descriptor=extension_pb2.MediaStreamDescriptor(
                    graph_identifier=extension_pb2.GraphIdentifier(
                        media_services_arm_id='',
                        graph_instance_name='SampleGraph1',
                        graph_node_name='SampleGraph1'
                    ),

                    media_descriptor=media_pb2.MediaDescriptor(
                        timescale=90000,

                        video_frame_sample_format=media_pb2.VideoFrameSampleFormat(
                            encoding=media_pb2.VideoFrameSampleFormat.Encoding.Value('RAW'),
                            pixel_format=media_pb2.VideoFrameSampleFormat.PixelFormat.Value('BGR24'),

                            dimensions=media_pb2.Dimensions(
                                width=self._width,
                                height=self._height,
                            )
                        )
                    ),
                    shared_memory_buffer_transfer_properties=smbtp
                )
            )
        except:
            log_exception()
            raise

        return msd_message


    def get_media_sample_message(self, sequence_number):
        message = None

        try:
            content_reference = None
            content_bytes = None
            if self._use_shared_memory:
                # Memory might be full and may no media sample returned
                memory_slot = self.get_media_sample(sequence_number)
                while memory_slot is None:
                    logging.info('***************** Shared Memory Full *****************')
                    time.sleep(1)
                    memory_slot = self.get_media_sample(sequence_number)

                memory_slot_offfset = memory_slot[0]
                memory_slot_length = (memory_slot[1] - memory_slot[0]) + 1

                content_reference = media_pb2.ContentReference(
                        address_offset=memory_slot_offfset,
                        length_bytes=memory_slot_length
                    )
            else:
                content_bytes = media_pb2.ContentBytes(
                     bytes=self._image.tostring()
                )

            message = extension_pb2.MediaStreamMessage(
                sequence_number=sequence_number,                       # Counter
                ack_sequence_number=0,                                # Initial value is 0

                media_sample=extension_pb2.MediaSample(
                    timestamp=0,
                    content_reference=content_reference,
                    content_bytes=content_bytes
                )
            )
        except:
            log_exception()
            raise

        return message


    # Get sample from media streamer, writes in shared memory, returns offset & length
    def get_media_sample(self, sequence_number):
        try:
            content_bytes = self._image.tobytes()
            image_blob_length = len(content_bytes)

            # Get empty memory slot with size of JPEG data
            memory_slot = self._shared_memory_manager.get_empty_slot(sequence_number,
                                                                   image_blob_length)
            if memory_slot is None:
                return None

            self._shared_memory_manager.write_bytes(memory_slot[0], content_bytes)

        except:
            log_exception()
            raise
        return memory_slot


    def start(self, output_file):
        try:
            # Use "wait_for_ready" (still in grpc preview...) to handle failure in case server not ready yet
            sequence_iterator = self._grpc_stub.ProcessMediaStream(self._request_generator,
                                                                  wait_for_ready=True)

            # Send the first message (MediaStreamDescriptor) and receive its response
            response = next(sequence_iterator)
            ack_seq_no = response.ack_sequence_number
            logging.info('[Received] AckNum: {0}'.format(ack_seq_no))

            with open(output_file, "w") as f:
                for response in sequence_iterator:
                    ack_seq_no = response.ack_sequence_number
                    logging.info('[Received] AckNum: {0}'.format(ack_seq_no))

                    # Release the memory slot
                    self._shared_memory_manager.delete_slot(ack_seq_no)

                    # print inference result
                    logging.info(response)
                    media_sample_obj = MessageToDict(response.media_sample)
                    #Schema Validation requires that string representation of enums are lowercase
                    for inference in media_sample_obj["inferences"]:
                        inference["type"] = inference["type"].lower()
                    f.write("{}\n".format(json.dumps(media_sample_obj)))
        except StopIteration:
            pass
        except:
            log_exception()
            raise

