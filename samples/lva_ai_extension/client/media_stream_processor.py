import grpc
import logging
import cv2
import os
import time

from utils.exception_handler import PrintGetExceptionDetails
from utils.shared_memory import SharedMemoryManager

import media_pb2
import extension_pb2
import extension_pb2_grpc


class MediaStreamProcessor:
    class RequestGenerator():
        def __init__(self, parent):
            try:
                self._requestSeqNum = 1
                self._mediaStreamProcessor = parent

                self._descriptorSent = False
            except:
                PrintGetExceptionDetails()
                raise

        def __iter__(self):
            return self

        def __next__(self):
            if self._descriptorSent is not True:
                # Return first message
                mediaSampleMessage = self._mediaStreamProcessor.GetMediaStreamDescriptorMessage(self._requestSeqNum)
                self._descriptorSent = True
            else:
                if self._mediaStreamProcessor._loopCount > 0:
                    mediaSampleMessage = self._mediaStreamProcessor.GetMediaSampleMessage(self._requestSeqNum)
                    self._mediaStreamProcessor._loopCount -= 1
                else:
                    raise StopIteration
            
            self._requestSeqNum += 1
            return mediaSampleMessage

    def __init__(self, grpcServerAddress, mediaSourceAddress, loopCount, sharedMemoryFlag):
        try:
            self._grpcServerAddress = grpcServerAddress  # Full address including port number i.e. "localhost:44001"
            self._mediaSourceAddress = mediaSourceAddress # Full path to video file name, IP Camera address
            self._loopCount = loopCount # how many time the sample will be send to aix server
            self._useSharedMemory = sharedMemoryFlag

            # Just make the sample frame ready to be sent to inference server
            self._cvImageSampleFrame = cv2.imread(mediaSourceAddress, cv2.IMREAD_COLOR)
            # AIX Server sample requires the images sent to pre-sized as 416x416 size. This size is requirement by Tiny Yolo V3. 
            # You may prefer to update the sample server code to resize the received images into 416x416 independent from their original 
            # size. But since LVA have the capability of sending any size image requested, why create redundent computation cycle? 
            # So in this aix_client (which mimics LVA), we resize the sample video frames into 416x416 size.
            self._cvImageSampleFrame = cv2.resize(self._cvImageSampleFrame, (416, 416), interpolation = cv2.INTER_AREA)

            # Shared Memory Manager to share data, keep track of reserved/released memory slots
            self._sharedMemoryManager = SharedMemoryManager(os.O_RDWR | os.O_SYNC | os.O_CREAT, name=None, size=10*1024*1024) # auto name will be assigned

            # Create grpc commmunication channel / stub
            self._grpcChannel = grpc.insecure_channel(self._grpcServerAddress)
            self._grpcStub = extension_pb2_grpc.MediaGraphExtensionStub(self._grpcChannel)

            self._requestGenerator = self.RequestGenerator(self)

        except:
            PrintGetExceptionDetails()
            raise


    def GetMediaStreamDescriptorMessage(self, sequenceNumber):
        msdMessage = None
        try:
            smbtp = None                # shared_memory_buffer_transfer_properties
            if self._useSharedMemory:
                    smbtp = extension_pb2.SharedMemoryBufferTransferProperties (
                        handle_name = self._sharedMemoryManager._shmFileName,
                        length_bytes = self._sharedMemoryManager._shmFileSize
                    )
            msdMessage = extension_pb2.MediaStreamMessage(
                sequence_number = sequenceNumber,                                       # Counter, starting at 1
                ack_sequence_number = 0,                                                # Initial value is 0

                media_stream_descriptor = extension_pb2.MediaStreamDescriptor(
                    graph_identifier = extension_pb2.GraphIdentifier( 
                        media_services_arm_id = '',
                        graph_instance_name = 'SampleGraph1',
                        graph_node_name = 'SampleGraph1'
                    ),

                    media_descriptor = media_pb2.MediaDescriptor(
                        timescale = 90000,

                        video_frame_sample_format = media_pb2.VideoFrameSampleFormat(
                            encoding = media_pb2.VideoFrameSampleFormat.Encoding.Value('RAW'),
                            pixel_format = media_pb2.VideoFrameSampleFormat.PixelFormat.Value('BGR24'),

                            dimensions = media_pb2.Dimensions(
                                width = 416,
                                height = 416,
                            )
                        )
                    ),
                    shared_memory_buffer_transfer_properties = smbtp
                )
            )
        except:
            PrintGetExceptionDetails()
            raise

        return msdMessage


    def GetMediaSampleMessage(self, sequenceNumber):
        msMessage = None

        try:
            contentReference = None
            contentBytes = None
            if self._useSharedMemory:
                # Memory might be full and may no media sample returned
                memorySlot = self.GetMediaSample(sequenceNumber)
                while memorySlot is None:
                    logging.info('***************** Shared Memory Full *****************')
                    time.sleep(0.1)
                    memorySlot = self.GetMediaSample(sequenceNumber)

                memorySlotOffset = memorySlot[0]
                memorySlotLength = (memorySlot[1] - memorySlot[0]) + 1

                contentReference = media_pb2.ContentReference(
                        address_offset = memorySlotOffset,
                        length_bytes = memorySlotLength
                    )
            else:
                contentBytes = media_pb2.ContentBytes(
                     bytes = self._cvImageSampleFrame.tostring()
                )

            msMessage = extension_pb2.MediaStreamMessage(
                sequence_number = sequenceNumber,                       # Counter
                ack_sequence_number = 0,                                # Initial value is 0

                media_sample = extension_pb2.MediaSample(
                    timestamp = 0,
                    content_reference = contentReference,
                    content_bytes = contentBytes
                )
            )
        except:
            PrintGetExceptionDetails()
            raise

        return msMessage


    # Get sample from media streamer, writes in shared memory, returns offset & length
    def GetMediaSample(self, sequenceNumber):
        try:
            contentBytes = self._cvImageSampleFrame.tobytes()
            imageBlobLength = len(contentBytes)

            # Get empty memory slot with size of JPEG data
            memorySlot = self._sharedMemoryManager.GetEmptySlot(sequenceNumber, imageBlobLength)
            if memorySlot is None:
                return None

            self._sharedMemoryManager.WriteBytes(memorySlot[0], contentBytes)

        except:
            PrintGetExceptionDetails()
            raise
        return memorySlot


    def Start(self):
        try:
            # Use "wait_for_ready" (still in grpc preview...) to handle failure in case server not ready yet
            sequenceIterator = self._grpcStub.ProcessMediaStream(self._requestGenerator, wait_for_ready=True)

            # Send the first message (MediaStreamDescriptor) and receive its response
            mediaStreamMessageResponse = next(sequenceIterator)
            ackSeqNo = mediaStreamMessageResponse.ack_sequence_number
            logging.info('[Received] AckNum: {0}'.format(ackSeqNo))

            for mediaStreamMessageResponse in sequenceIterator:
                ackSeqNo = mediaStreamMessageResponse.ack_sequence_number
                logging.info('[Received] AckNum: {0}'.format(ackSeqNo))
                
                # Release the memory slot
                self._sharedMemoryManager.DeleteSlot(ackSeqNo)

                # print inference result
                logging.info(mediaStreamMessageResponse)
        except StopIteration:
            pass
        except:
            PrintGetExceptionDetails()
            raise

