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
from samples.ava_ai_extension.common.exception_handler import log_exception
from samples.ava_ai_extension.common.shared_memory import SharedMemoryManager
from samples.ava_ai_extension.common.grpc_autogen import media_pb2
from samples.ava_ai_extension.common.grpc_autogen import extension_pb2
from samples.ava_ai_extension.common.grpc_autogen import extension_pb2_grpc

class MediaStreamProcessor:
    class RequestGenerator:
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
                logging.info(
                    "MediaStreamDescriptor request #{}".format(self._request_seq_num)
                )
                request = extension_pb2.MediaStreamMessage(
                    sequence_number=self._request_seq_num,
                    ack_sequence_number=0,
                    media_stream_descriptor=self._descriptor,
                )
            else:
                logging.debug("MediaSample request #{}".format(self._request_seq_num))
                image = self._queue.get()
                if image is None:
                    raise StopIteration
                media_sample = extension_pb2.MediaSample(
                    timestamp=0, content_bytes=media_pb2.ContentBytes(bytes=image)
                )
                if self._shared_memory_manager:
                    media_sample = self.get_shared_memory_request(media_sample)
                request = extension_pb2.MediaStreamMessage(
                    sequence_number=self._request_seq_num,
                    ack_sequence_number=0,
                    media_sample=media_sample,
                )

            self._request_seq_num += 1
            return request

        def get_memory_slot(self, sequence_number, content_bytes):
            try:
                memory_slot = self._shared_memory_manager.get_empty_slot(
                    sequence_number, len(content_bytes)
                )
                if memory_slot is None:
                    return None

                self._shared_memory_manager.write_bytes(memory_slot[0], content_bytes)

            except Exception:
                log_exception()
                raise
            return memory_slot

        def get_shared_memory_request(self, media_sample):
            memory_slot = self.get_memory_slot(
                self._request_seq_num, media_sample.content_bytes.bytes
            )
            while memory_slot is None:
                logging.info("***************** Shared Memory Full *****************")
                time.sleep(1)
                memory_slot = self.get_memory_slot(
                    self._request_seq_num, media_sample.content_bytes.bytes
                )

            memory_slot_offset = memory_slot[0]
            memory_slot_length = (memory_slot[1] - memory_slot[0]) + 1

            content_reference = media_pb2.ContentReference(
                address_offset=memory_slot_offset, length_bytes=memory_slot_length
            )
            media_sample = extension_pb2.MediaSample(
                timestamp=0, content_reference=content_reference
            )
            return media_sample

    def __init__(
            self, grpc_server_address, use_shared_memory, frame_queue_size, frame_size
    ):
        try:
            # Full address including port number i.e. "localhost:44001"
            self._grpc_server_address = grpc_server_address
            self._shared_memory_manager = None
            if use_shared_memory:
                shared_memory_size = (
                    frame_queue_size * frame_size
                    if frame_queue_size
                    else 100 * frame_size
                )
                self._shared_memory_manager = SharedMemoryManager(
                    os.O_RDWR | os.O_SYNC | os.O_CREAT,
                    name=None,
                    size=shared_memory_size,
                )
            self._grpc_channel = grpc.insecure_channel(self._grpc_server_address)
            self._grpc_stub = extension_pb2_grpc.MediaGraphExtensionStub(
                self._grpc_channel
            )
            self._stop = False
            self._thread = None

        except Exception:
            log_exception()
            raise

    def get_media_stream_descriptor(self, width, height, extension_config):
        try:
            smbtp = None
            if self._shared_memory_manager:
                smbtp = extension_pb2.SharedMemoryBufferTransferProperties(
                    handle_name=self._shared_memory_manager.shm_file_name,
                    length_bytes=self._shared_memory_manager.shm_file_size,
                )
            media_stream_descriptor = extension_pb2.MediaStreamDescriptor(
                graph_identifier=extension_pb2.GraphIdentifier(
                    media_services_arm_id="",
                    graph_instance_name="SampleGraph1",
                    graph_node_name="SampleGraph1",
                ),
                extension_configuration=extension_config,
                media_descriptor=media_pb2.MediaDescriptor(
                    timescale=90000,
                    video_frame_sample_format=media_pb2.VideoFrameSampleFormat(
                        encoding=media_pb2.VideoFrameSampleFormat.Encoding.Value("RAW"),
                        pixel_format=media_pb2.VideoFrameSampleFormat.PixelFormat.Value(
                            "BGR24"
                        ),
                        dimensions=media_pb2.Dimensions(
                            width=width,
                            height=height,
                        ),
                    ),
                ),
                shared_memory_buffer_transfer_properties=smbtp,
            )
        except Exception:
            log_exception()
            raise

        return media_stream_descriptor

    def start(self, width, height, frame_queue, result_queue, extension_config):
        descriptor = self.get_media_stream_descriptor(width, height, extension_config)
        request_generator = self.RequestGenerator(
            descriptor, self._shared_memory_manager, frame_queue
        )
        # Use "wait_for_ready" (still in grpc preview...)
        # to handle failure in case server not ready yet
        sequence_iterator = self._grpc_stub.ProcessMediaStream(
            request_generator, wait_for_ready=True
        )
        response = next(sequence_iterator)
        ack_seq_no = response.ack_sequence_number
        logging.info("[Received] AckNum: {0}".format(ack_seq_no))
        self._thread = threading.Thread(
            target=self.run, args=(sequence_iterator, result_queue)
        )
        self._thread.start()

    def stop(self):
        self._stop = True
        if self._thread:
            self._thread.join()

    def run(self, sequence_iterator, result_queue):
        try:
            for response in sequence_iterator:
                if self._stop:
                    break
                ack_seq_no = response.ack_sequence_number
                logging.debug("[Received] AckNum: {0}".format(ack_seq_no))
                result_queue.put(response)
                if self._shared_memory_manager:
                    self._shared_memory_manager.delete_slot(ack_seq_no)
        except Exception as error:
            result_queue.put(error)

        # Signal end of stream
        result_queue.put(None)
