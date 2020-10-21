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

import tempfile
import mmap
import os
import logging
from .exception_handler import PrintGetExceptionDetails

# ***********************************************************************************
# Shared memory management 
#
class SharedMemoryManager:
    def __init__(self, shmFlags=None, name=None, size=None):
        try:
            self._shmFilePath = '/dev/shm'
            self._shmFileName = name
            if self._shmFileName is None:
                self._shmFileName = next(tempfile._get_candidate_names())

            self._shmFileSize = size
            if self._shmFileSize is None:
                self._shmFileSize = 1024 * 1024 * 10     # Bytes (10MB)

            self._shmFileFullPath = os.path.join(self._shmFilePath, self._shmFileName)
            self._shmFlags = shmFlags

            # See the NOTE section here: https://docs.python.org/2/library/os.html#os.open for details on shmFlags
            if self._shmFlags is None:
                self._shmFile = open(self._shmFileFullPath, 'r+b')            
                self._shm = mmap.mmap(self._shmFile.fileno(), self._shmFileSize)
            else:
                self._shmFile = os.open(self._shmFileFullPath, self._shmFlags)            
                os.ftruncate(self._shmFile, self._shmFileSize)
                self._shm = mmap.mmap(self._shmFile, self._shmFileSize, mmap.MAP_SHARED, mmap.PROT_WRITE | mmap.PROT_READ)

            # Dictionary to host reserved mem blocks
            # self._mem_slots[sequenceNo] = [Begin, End]        (closed interval)
            self._memSlots = dict()

            logging.info('Shared memory name: {0}'.format(self._shmFileFullPath))
        except:
            PrintGetExceptionDetails()
            raise

    def ReadBytes(self, memorySlotOffset, memorySlotLength):
        try:
            # This is Non-Zero Copy operation
            # self._shm.seek(memorySlotOffset, os.SEEK_SET)
            # bytesRead = self._shm.read(memorySlotLength)
            # return bytesRead

            #Zero-copy version
            return memoryview(self._shm)[memorySlotOffset:memorySlotOffset+memorySlotLength].toreadonly()

        except:
            PrintGetExceptionDetails()
            raise

    def WriteBytes(self, memorySlotOffset, bytesToWrite):
        try:
            #Zero-copy version
            memoryview(self._shm)[memorySlotOffset:memorySlotOffset+len(bytesToWrite)] = bytesToWrite

        except:
            PrintGetExceptionDetails()
            raise

    # Returns None if no availability
    # Returns closed interval [Begin, End] address with available slot
    def GetEmptySlot(self, seqNo, sizeNeeded):
        address = None

        if sizeNeeded < 1:
            return address

        # Empty memory
        if len(self._memSlots) < 1:
            if self._shmFileSize >= sizeNeeded:
                self._memSlots[seqNo] = (0, sizeNeeded - 1)
                address = (0, sizeNeeded - 1)
            else:
                address = None
        else:
            self._memSlots = {k: v for k, v in sorted(
                self._memSlots.items(), key=lambda item: item[1])}

            # find an available memory gap = sizeNeeded
            prevSlotEnd = 0
            for k, v in self._memSlots.items():
                if (v[0] - prevSlotEnd - 1) >= sizeNeeded:
                    address = (prevSlotEnd + 1, prevSlotEnd + sizeNeeded)
                    self._memSlots[seqNo] = (address[0], address[1])
                    break
                else:
                    prevSlotEnd = v[1]

            # no gap in between, check last possible gap
            if address is None:
                if (self._shmFileSize - prevSlotEnd + 1) >= sizeNeeded:
                    address = (prevSlotEnd + 1, prevSlotEnd + sizeNeeded)
                    self._memSlots[seqNo] = (address[0], address[1])

        # interval [Begin, End]
        return address

    def DeleteSlot(self, seqNo):
        try:
            del self._memSlots[seqNo]
            return True
        except KeyError:
            return False

    def __del__(self):
        try:
            if self._shmFlags is None:
                self._shmFile.close()
            else:
                os.close(self._shmFile)
        except:
            PrintGetExceptionDetails()
            raise

