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
import time
import threading
import grpc
from samples.lva_ai_extension.common.exception_handler import log_exception
from samples.lva_ai_extension.common.shared_memory import SharedMemoryManager
import samples.lva_ai_extension.common.grpc_autogen.media_pb2 as media_pb2
import samples.lva_ai_extension.common.grpc_autogen.extension_pb2 as extension_pb2
import samples.lva_ai_extension.common.grpc_autogen.extension_pb2_grpc as extension_pb2_grpc



class MediaStreamProcessor:

    class RequestGenerator():
        def __init__(self, descriptor, shared_memory_manager, queue):
            try:
                self._request_seq_num = 1
                self._descriptor = descriptor
                self._shared_memory_manager = shared_memory_manager
                self._queue = queue
            except:
                log_exception()
                raise

        def __iter__(self):
            return self

        def __next__(self):
            if self._request_seq_num == 1:
                logging.info("MediaStreamDescriptor request #{}".format(self._request_seq_num))
                request = extension_pb2.MediaStreamMessage(
                    sequence_number=self._request_seq_num,
                    ack_sequence_number=0,
                    media_stream_descriptor=self._descriptor)
            else:
                logging.info("MediaSample request #{}".format(self._request_seq_num))
                image = self._queue.get()
                if image is None:
                    raise StopIteration
                media_sample = extension_pb2.MediaSample(
                    timestamp=0,
                    content_bytes=media_pb2.ContentBytes(
                        bytes=image
                    )
                )
                if self._shared_memory_manager:
                    media_sample = self.get_shared_memory_request(media_sample)
                request = extension_pb2.MediaStreamMessage(
                    sequence_number=self._request_seq_num,
                    ack_sequence_number=0,
                    media_sample=media_sample
                )
            self._request_seq_num += 1
            return request

        def get_memory_slot(self, sequence_number, content_bytes):
            try:
                memory_slot = self._shared_memory_manager.get_empty_slot(sequence_number,
                                                                         len(content_bytes))
                if memory_slot is None:
                    return None

                self._shared_memory_manager.write_bytes(memory_slot[0], content_bytes)

            except Exception:
                log_exception()
                raise
            return memory_slot

        def get_shared_memory_request(self, media_sample):
            memory_slot = self.get_memory_slot(self._request_seq_num, media_sample.content_bytes.bytes)
            while memory_slot is None:
                logging.info('***************** Shared Memory Full *****************')
                time.sleep(1)
                memory_slot = self.get_memory_slot(self._request_seq_num, media_sample.content_bytes.bytes)

            memory_slot_offset = memory_slot[0]
            memory_slot_length = (memory_slot[1] - memory_slot[0]) + 1

            content_reference = media_pb2.ContentReference(
                address_offset=memory_slot_offset,
                length_bytes=memory_slot_length
            )
            media_sample = extension_pb2.MediaSample(
                timestamp=0,
                content_reference=content_reference
            )
            return media_sample


    def __init__(self, grpc_server_address,
                 use_shared_memory):
        try:
            self._grpc_server_address = grpc_server_address  # Full address including port number i.e. "localhost:44001"
            self._shared_memory_manager = None
            if use_shared_memory:
                self._shared_memory_manager = SharedMemoryManager(os.O_RDWR | os.O_SYNC | os.O_CREAT,
                                                                  name=None,
                                                                  size=100*1024*1024)
            self._grpc_channel = grpc.insecure_channel(self._grpc_server_address)
            self._grpc_stub = extension_pb2_grpc.MediaGraphExtensionStub(
                self._grpc_channel)

        except Exception:
            log_exception()
            raise


    def get_media_stream_descriptor(self, width, height):
        try:
            smbtp = None
            if self._shared_memory_manager:
                smbtp = extension_pb2.SharedMemoryBufferTransferProperties(
                    handle_name=self._shared_memory_manager.shm_file_name,
                    length_bytes=self._shared_memory_manager.shm_file_size
                )
            media_stream_descriptor = extension_pb2.MediaStreamDescriptor(
                graph_identifier=extension_pb2.GraphIdentifier(
                    media_services_arm_id='',
                    graph_instance_name='SampleGraph1',
                    graph_node_name='SampleGraph1'
                ),

                media_descriptor=media_pb2.MediaDescriptor(
                    timescale=90000,
                    # pylint: disable=no-member
                    # E1101: Class 'VideoFrameSampleFormat' has no 'Encoding' member (no-member)
                    # E1101: Class 'VideoFrameSampleFormat' has no 'PixelFormat' member (no-member)
                    video_frame_sample_format=media_pb2.VideoFrameSampleFormat(
                        encoding=media_pb2.VideoFrameSampleFormat.Encoding.Value('RAW'),
                        pixel_format=media_pb2.VideoFrameSampleFormat.PixelFormat.Value('BGR24'),

                        dimensions=media_pb2.Dimensions(
                            width=width,
                            height=height,
                        )
                    )
                ),
                shared_memory_buffer_transfer_properties=smbtp
            )
        except Exception:
            log_exception()
            raise

        return media_stream_descriptor


    def start(self, width, height, frame_queue, result_queue):
        descriptor = self.get_media_stream_descriptor(width, height)
        request_generator = self.RequestGenerator(descriptor, self._shared_memory_manager, frame_queue)
        # Use "wait_for_ready" (still in grpc preview...) to handle failure in case server not ready yet
        sequence_iterator = self._grpc_stub.ProcessMediaStream(request_generator,
                                                               wait_for_ready=True)
        response = next(sequence_iterator)
        ack_seq_no = response.ack_sequence_number
        logging.info('[Received] AckNum: {0}'.format(ack_seq_no))
        thread = threading.Thread(target=self.run, args=(sequence_iterator, result_queue))
        thread.start()

    def run(self, sequence_iterator, result_queue):
        for response in sequence_iterator:
            ack_seq_no = response.ack_sequence_number
            logging.info('[Received] AckNum: {0}'.format(ack_seq_no))
            result_queue.put(response)
            if self._shared_memory_manager:
                self._shared_memory_manager.delete_slot(ack_seq_no)

        # Signal end of stream
        result_queue.put(None)
