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

import argparse
from .exception_handler import PrintGetExceptionDetails
from enum import Enum

class ArgumentsType(Enum):
    CLIENT = 1
    SERVER = 2

class ArgumentParser:
    def __init__(self, argumentsType):
        try:
            self._argumentsType = argumentsType

            parser = argparse.ArgumentParser()

            if (self._argumentsType == ArgumentsType.SERVER):
                parser.add_argument('-p', nargs=1, metavar=('grpc_server_port'),
                                            help='Port number to serve gRPC server.')
            else:
                parser.add_argument('-s', nargs=1, metavar=('grpc_server_address'),
                                            help='gRPC server address.')
                
                parser.add_argument('-f', nargs=1, metavar=('sample_file'),
                                            help='Name of the sample video frame.')

                parser.add_argument('-l', nargs=1, metavar=('loop_count'),
                                            help='How many times to send sample video frame.')

                parser.add_argument('-m', action='store_const', dest='shm',
                                    const=True, default=False,                        
                                    help='set to use shared memory')      

            parser.add_argument('--version', action='version', version='%(prog)s 1.0')

            self._arguments = parser.parse_args()
        except:
            PrintGetExceptionDetails()
            raise

    def GetGrpcServerPort(self):
        if (self._arguments.p is not None):
            return self._arguments.p[0]
        else:
            raise Exception('Command line parameter for gRPC server port is missing.')

    def GetGrpcServerAddress(self):
        if (self._arguments.s is not None):
            return self._arguments.s[0]
        else:
            raise Exception('Command line parameter for gRPC server address is missing.')

    def GetSampleMediaAddress(self):
        if (self._arguments.f is not None):
            return self._arguments.f[0]
        else:
            raise Exception('Command line parameter for media file name is missing.')

    def GetLoopCount(self):
        if (self._arguments.f is not None):
            return int(self._arguments.l[0])
        else:
            raise Exception('Command line parameter for loop count is missing.')

    def GetSharedMemoryFlag(self):
        return self._arguments.shm
