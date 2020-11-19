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
from .exception_handler import log_exception

# ***********************************************************************************
# Shared memory management
#
class SharedMemoryManager:
    def __init__(self, shm_flags=None, name=None, size=None):
        try:
            #nosec skips pybandit hits
            self.shm_file_path = '/dev/shm'     # nosec
            self.shm_file_name = name
            if self.shm_file_name is None:
                self.shm_file_name = next(tempfile._get_candidate_names())

            self.shm_file_size = size
            if self.shm_file_size is None:
                self.shm_file_size = 1024 * 1024 * 10     # Bytes (10MB)

            self._shm_file_full_path = os.path.join(self.shm_file_path,
                                                    self.shm_file_name)
            self._shm_flags = shm_flags

            # See the NOTE section here: https://docs.python.org/2/library/os.html#os.open
            # for details on shmFlags
            if self._shm_flags is None:
                self._shm_file = open(self._shm_file_full_path, 'r+b')
                self._shm = mmap.mmap(self._shm_file.fileno(), self.shm_file_size)
            else:
                self._shm_file = os.open(self._shm_file_full_path, self._shm_flags)
                os.ftruncate(self._shm_file, self.shm_file_size)
                self._shm = mmap.mmap(self._shm_file,
                                      self.shm_file_size,
                                      mmap.MAP_SHARED,
                                      mmap.PROT_WRITE | mmap.PROT_READ)

            # Dictionary to host reserved mem blocks
            # self._mem_slots[sequenceNo] = [Begin, End]        (closed interval)
            self._mem_slots = dict()

            logging.info('Shared memory name: {0}'.format(self._shm_file_full_path))
        except:
            log_exception()
            raise

    def read_bytes(self, memory_slot_offset, memory_slot_length):
        try:
            # This is Non-Zero Copy operation
            # self._shm.seek(memorySlotOffset, os.SEEK_SET)
            # bytesRead = self._shm.read(memorySlotLength)
            # return bytesRead

            #Zero-copy version
            return memoryview(self._shm)[memory_slot_offset:memory_slot_offset+memory_slot_length]

        except:
            log_exception()
            raise

    def write_bytes(self, memory_slot_offset, bytes_to_write):
        try:
            #Zero-copy version
            memoryview(self._shm)[memory_slot_offset:
                                  memory_slot_offset+
                                  len(bytes_to_write)] = bytes_to_write

        except:
            log_exception()
            raise

    # Returns None if no availability
    # Returns closed interval [Begin, End] address with available slot
    def get_empty_slot(self, seq_no, size_needed):
        address = None

        if size_needed < 1:
            return address

        # Empty memory
        if len(self._mem_slots) < 1:
            if self.shm_file_size >= size_needed:
                self._mem_slots[seq_no] = (0, size_needed - 1)
                address = (0, size_needed - 1)
            else:
                address = None
        else:
            self._mem_slots = {k: v for k, v in sorted(
                self._mem_slots.items(), key=lambda item: item[1])}

            # find an available memory gap = sizeNeeded
            prev_slot_end = 0
            for _, memory_slot in self._mem_slots.items():
                if (memory_slot[0] - prev_slot_end - 1) >= size_needed:
                    address = (prev_slot_end + 1, prev_slot_end + size_needed)
                    self._mem_slots[seq_no] = (address[0], address[1])
                    break
                prev_slot_end = memory_slot[1]

            # no gap in between, check last possible gap
            if address is None:
                if (self.shm_file_size - prev_slot_end + 1) >= size_needed:
                    address = (prev_slot_end + 1, prev_slot_end + size_needed)
                    self._mem_slots[seq_no] = (address[0], address[1])

        # interval [Begin, End]
        return address

    def delete_slot(self, seq_no):
        try:
            del self._mem_slots[seq_no]
            return True
        except KeyError:
            return False

    def __del__(self):
        try:
            if self._shm_flags is None:
                self._shm_file.close()
            else:
                os.close(self._shm_file)
        except:
            log_exception()
            raise
