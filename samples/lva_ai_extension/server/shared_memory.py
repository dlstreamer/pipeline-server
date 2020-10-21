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
#from exception_handler import PrintGetExceptionDetails

# ***********************************************************************************
# Shared memory management 
#
class SharedMemoryManager:
    def __init__(self, name, size):
        try:
            self._shmFilePath = '/dev/shm'
            self._shmFileName = name

            self._shmFileSize = size
            self._shmFileFullPath = os.path.join(self._shmFilePath, self._shmFileName)
            self._shmFile = open(self._shmFileFullPath, 'r+b')            
            self._shm = mmap.mmap(self._shmFile.fileno(), self._shmFileSize)
            self._memSlots = dict()

            logging.info('Shared memory name: {0}'.format(self._shmFileFullPath))
        except:
#            PrintGetExceptionDetails()
            raise

    def ReadBytes(self, memorySlotOffset, memorySlotLength):
        try:
            # This is Non-Zero Copy operation
            # self._shm.seek(memorySlotOffset, os.SEEK_SET)
            # bytesRead = self._shm.read(memorySlotLength)
            # return bytesRead

            #Zero-copy version
            return memoryview(self._shm)[memorySlotOffset:memorySlotOffset+memorySlotLength]

        except:
#            PrintGetExceptionDetails()
            raise

 


    def __del__(self):
        try:            
            self._shmFile.close()
        except:
#            PrintGetExceptionDetails()
            raise

