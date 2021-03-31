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

import os
import json
from queue import Queue
import tempfile
import time
import datetime
from enum import Enum
import jsonschema

import samples.lva_ai_extension.common.grpc_autogen.inferencing_pb2 as inferencing_pb2
import samples.lva_ai_extension.common.grpc_autogen.media_pb2 as media_pb2
import samples.lva_ai_extension.common.grpc_autogen.extension_pb2 as extension_pb2
import samples.lva_ai_extension.common.grpc_autogen.extension_pb2_grpc as extension_pb2_grpc

from samples.lva_ai_extension.common.shared_memory import SharedMemoryManager
from samples.lva_ai_extension.common.exception_handler import log_exception
import samples.lva_ai_extension.common.extension_schema as extension_schema

from vaserving.vaserving import VAServing
from vaserving.pipeline import Pipeline
from vaserving.gstreamer_app_source import GvaFrameData
from vaserving.common.utils.logging import get_logger


class TransferType(Enum):
    BYTES = 1  # Embedded Content
    REFERENCE = 2  # Shared Memory
    HANDLE = 3  # Reserved


class State:
    def __init__(self, media_stream_descriptor):
        try:
            # media descriptor holding input data format
            self.media_stream_descriptor = media_stream_descriptor

            # Get how data will be transferred
            if (
                    self.media_stream_descriptor.WhichOneof("data_transfer_properties")
                    is None
            ):
                self.content_transfer_type = TransferType.BYTES
            elif self.media_stream_descriptor.HasField(
                    "shared_memory_buffer_transfer_properties"
            ):
                self.content_transfer_type = TransferType.REFERENCE
            elif self.media_stream_descriptor.HasField(
                    "shared_memory_segments_transfer_properties"
            ):
                self.content_transfer_type = TransferType.HANDLE

            # Setup if shared mem used
            if self.content_transfer_type == TransferType.REFERENCE:
                # Create shared memory accessor specific to the client
                self.shared_memory_manager = SharedMemoryManager(
                    name=self.media_stream_descriptor.shared_memory_buffer_transfer_properties.handle_name,
                    size=self.media_stream_descriptor.shared_memory_buffer_transfer_properties.length_bytes,
                )
            else:
                self.shared_memory_manager = None

        except:
            log_exception(get_logger("State"))
            raise


class MediaGraphExtension(extension_pb2_grpc.MediaGraphExtensionServicer):
    def __init__(
            self,
            pipeline,
            version,
            debug=False,
            input_queue_size=1,
    ):
        self._pipeline = pipeline
        self._version = version
        self._input_queue_size = input_queue_size
        self._logger = get_logger("MediaGraphExtension")
        self._debug = debug
        self._extension_config_schema = extension_schema.extension_config
        self._extension_config_validator = jsonschema.Draft7Validator(schema=self._extension_config_schema,
                                                                      format_checker=jsonschema.draft7_format_checker)

    def _generate_media_stream_message(self, gva_sample):
        message = json.loads(list(gva_sample.video_frame.messages())[0])

        msg = extension_pb2.MediaStreamMessage()
        msg.ack_sequence_number = message["sequence_number"]
        msg.media_sample.timestamp = message["timestamp"]

        for region in gva_sample.video_frame.regions():
            inference = msg.media_sample.inferences.add()

            attributes = []
            obj_id = None
            obj_label = None
            obj_confidence = 0
            obj_left = 0
            obj_width = 0
            obj_top = 0
            obj_height = 0

            for tensor in region.tensors():
                name = tensor.name()

                if name == "detection":
                    obj_confidence = region.confidence()
                    obj_label = region.label()

                    obj_left, obj_top, obj_width, obj_height = region.normalized_rect()

                    inference.type = (
                        # pylint: disable=no-member
                        inferencing_pb2.Inference.InferenceType.ENTITY
                    )
                    if region.object_id():  # Tracking
                        obj_id = str(region.object_id())
                elif tensor["label"]:  # Classification
                    attr_name = name
                    attr_label = tensor["label"]
                    attr_confidence = region.confidence()
                    attributes.append([attr_name, attr_label, attr_confidence])
            if obj_label is not None:
                try:
                    entity = inferencing_pb2.Entity(
                        tag=inferencing_pb2.Tag(
                            value=obj_label, confidence=obj_confidence
                        ),
                        box=inferencing_pb2.Rectangle(
                            l=obj_left, t=obj_top, w=obj_width, h=obj_height
                        ),
                    )
                    for attr in attributes:
                        attribute = inferencing_pb2.Attribute(
                            name=attr[0], value=attr[1], confidence=attr[2]
                        )
                        entity.attributes.append(attribute)
                    if obj_id:
                        entity.id = obj_id
                except:
                    log_exception(self._logger)
                    raise

                inference.entity.CopyFrom(entity)

        return msg

    def _generate_gva_sample(self, client_state, request):

        new_sample = None

        try:
            # Get reference to raw bytes
            if client_state.content_transfer_type == TransferType.BYTES:
                raw_bytes = memoryview(request.media_sample.content_bytes.bytes)
            elif client_state.content_transfer_type == TransferType.REFERENCE:
                # Data sent over shared memory buffer
                address_offset = request.media_sample.content_reference.address_offset
                length_bytes = request.media_sample.content_reference.length_bytes

                # Get memory reference to (in readonly mode) data sent over shared memory
                raw_bytes = client_state.shared_memory_manager.read_bytes(
                    address_offset, length_bytes
                )

            # Get encoding details of the media sent by client
            encoding = (
                client_state.media_stream_descriptor.media_descriptor.video_frame_sample_format.encoding
            )

            # Handle RAW content (Just place holder for the user to handle each variation...)
            if (
                    encoding
                    == client_state.media_stream_descriptor.media_descriptor.video_frame_sample_format.Encoding.RAW
            ):
                pixel_format = (
                    client_state.media_stream_descriptor.media_descriptor.video_frame_sample_format.pixel_format
                )
                caps_format = None

                if pixel_format == media_pb2.VideoFrameSampleFormat.PixelFormat.RGBA:
                    caps_format = "RGBA"
                elif pixel_format == media_pb2.VideoFrameSampleFormat.PixelFormat.RGB24:
                    caps_format = "RGB"
                elif pixel_format == media_pb2.VideoFrameSampleFormat.PixelFormat.BGR24:
                    caps_format = "BGR"
                if caps_format is not None:
                    caps = "".join(
                        (
                            "video/x-raw,format=",
                            caps_format,
                            ",width=",
                            str(
                                client_state.media_stream_descriptor.
                                media_descriptor.video_frame_sample_format.dimensions.width
                            ),
                            ",height=",
                            str(
                                client_state.media_stream_descriptor.
                                media_descriptor.video_frame_sample_format.dimensions.height
                            ),
                        )
                    )
                    new_sample = GvaFrameData(
                        bytes(raw_bytes),
                        caps,
                        message={
                            "sequence_number": request.sequence_number,
                            "timestamp": request.media_sample.timestamp,
                        },
                    )
            else:
                self._logger.info("Sample format is not RAW")
        except:
            log_exception(self._logger)
            raise
        return new_sample

    def _get_queued_samples(self, queue, block=False):
        samples = []
        if block:
            samples.append(queue.get())
        while not queue.empty():
            samples.append(queue.get())
        return samples

    def _validate_ext_config_against_schema(self, extension_config):
        try:
            self._extension_config_validator.validate(extension_config)
        except jsonschema.exceptions.ValidationError as err:
            self._logger.error("Error occured during validation: {}".format(err.message))
            raise

    def _set_debug_properties(self, pipeline_version, pipeline_parameters):
        if self._debug:
            pipeline_version = "debug_" + pipeline_version
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            location = os.path.join(
                tempfile.gettempdir(), "vaserving", self._version, timestamp
            )
            os.makedirs(os.path.abspath(location))
            debug_parameters = {
                "location": os.path.join(location, "frame_%07d.jpeg")
            }

            pipeline_parameters.update(debug_parameters)
        return pipeline_version, pipeline_parameters

    def _set_pipeline_properties(self, request):
        # Set deployment pipeline name, version, and args if set
        pipeline_name = self._pipeline
        pipeline_version = self._version
        pipeline_parameters = {}

        # Set pipeline values if passed through request
        extension_configuration = None
        if request.media_stream_descriptor.extension_configuration:
            # Load the extension_config
            try:
                extension_configuration = json.loads(request.media_stream_descriptor.extension_configuration)
            except ValueError:
                self._logger.error("Decoding extension_configuration field has failed: {}".format(
                    request.media_stream_descriptor.extension_configuration))
                raise
            # Validate the extension_config against the schema
            self._validate_ext_config_against_schema(extension_configuration)

            # If extension_config has pipeline values, set the properties
            if "pipeline" in extension_configuration:
                pipeline_request = extension_configuration.get("pipeline")
                pipeline_name = pipeline_request["name"]
                pipeline_version = pipeline_request["version"]
                if pipeline_request.get("parameters"):
                    pipeline_parameters = pipeline_request["parameters"]

            # Reject pipeline if it has debug in its version
            if pipeline_version.startswith("debug"):
                raise ValueError("Cannot specify debug pipelines in request")

        # Set debug properties if debug flag is set
        pipeline_version, pipeline_parameters = self._set_debug_properties(pipeline_version, pipeline_parameters)

        return pipeline_name, pipeline_version, pipeline_parameters

    # gRPC stubbed function
    # client/gRPC will call this function to send frames/descriptions
    def ProcessMediaStream(self, requestIterator, context):
        requests_received = 0
        responses_sent = 0
        # First message from the client is (must be) MediaStreamDescriptor
        request = next(requestIterator)
        requests_received += 1
        # Extract message IDs
        request_seq_num = request.sequence_number
        request_ack_seq_num = request.ack_sequence_number
        # State object per client
        client_state = State(request.media_stream_descriptor)
        self._logger.info(
            "[Received] SeqNum: {0:07d} | "
            "AckNum: {1}\nMediaStreamDescriptor:\n{2}".format(
                request_seq_num,
                request_ack_seq_num,
                client_state.media_stream_descriptor,
            )
        )
        # First message response ...
        media_stream_message = extension_pb2.MediaStreamMessage(
            sequence_number=1,
            ack_sequence_number=request_seq_num,
            media_stream_descriptor=extension_pb2.MediaStreamDescriptor(
                media_descriptor=media_pb2.MediaDescriptor(
                    timescale=client_state.media_stream_descriptor.media_descriptor.timescale
                )
            ),
        )

        responses_sent += 1
        yield media_stream_message

        pipeline_name, pipeline_version, pipeline_parameters = self._set_pipeline_properties(request)

        self._logger.info("Pipeline Name : {}".format(pipeline_name))
        self._logger.info("Pipeline Version : {}".format(pipeline_version))
        self._logger.info("Pipeline Parameters : {}".format(pipeline_parameters))
        detect_input = Queue(maxsize=self._input_queue_size)
        detect_output = Queue()
        # Start object detection pipeline
        # It will wait until it receives frames via the detect_input queue
        detect_pipeline = VAServing.pipeline(pipeline_name, pipeline_version)
        detect_pipeline.start(
            source={
                "type": "application",
                "class": "GStreamerAppSource",
                "input": detect_input,
                "mode": "push",
            },
            destination={
                "type": "application",
                "class": "GStreamerAppDestination",
                "output": detect_output,
                "mode": "frames",
            },
            parameters=pipeline_parameters,
        )

        # Process rest of the MediaStream message sequence
        for request in requestIterator:
            try:
                if requests_received - responses_sent >= self._input_queue_size:
                    queued_samples = self._get_queued_samples(detect_output, block=True)
                else:
                    queued_samples = []
                # Read request id, sent by client
                request_seq_num = request.sequence_number
                self._logger.debug("[Received] SeqNum: {0:07d}".format(request_seq_num))
                requests_received += 1
                gva_sample = self._generate_gva_sample(client_state, request)
                detect_input.put(gva_sample)
                queued_samples.extend(self._get_queued_samples(detect_output))
                if context.is_active():
                    # If any processed samples are queued, drain them and yield back to client
                    for gva_sample in queued_samples:
                        if gva_sample:
                            media_stream_message = self._generate_media_stream_message(
                                gva_sample
                            )
                            responses_sent += 1
                            self._logger.debug(
                                "[Sent] AckSeqNum: {0:07d}".format(
                                    media_stream_message.ack_sequence_number
                                )
                            )
                            yield media_stream_message
                else:
                    break
                if detect_pipeline.status().state.stopped():
                    break
            except:
                log_exception(self._logger)
                raise

        if detect_pipeline.status().state.stopped():
            try:
                raise Exception("Pipeline encountered an issue, pipeline state: {}".format(
                    detect_pipeline.status().state))
            except:
                log_exception(self._logger)
                raise

        # After the server has finished processing all the request iterator objects
        # Push a None object into the input queue.
        # When the None object comes out of the output queue, we know we've finished
        # processing all requests
        gva_sample = None
        if not detect_pipeline.status().state.stopped():
            detect_input.put(None)
            gva_sample = detect_output.get()
        while gva_sample:
            media_stream_message = self._generate_media_stream_message(gva_sample)
            responses_sent += 1
            self._logger.debug(
                "[Sent] AckSeqNum: {0:07d}".format(
                    media_stream_message.ack_sequence_number
                )
            )
            if context.is_active():
                yield media_stream_message
            gva_sample = detect_output.get()

        # One final check on the pipeline to ensure it worked properly
        status = detect_pipeline.wait(10)
        if (not status) or (status.state == Pipeline.State.ERROR):
            raise Exception("Pipeline did not complete successfully")

        self._logger.info(
            "Done processing messages: Received: {}, Sent: {}".format(
                requests_received, responses_sent
            )
        )
        self._logger.info(
            "MediaStreamDescriptor:\n{0}".format(client_state.media_stream_descriptor)
        )
