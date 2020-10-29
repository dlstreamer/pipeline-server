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

import sys

import logging
import os
from media_stream_processor import MediaStreamProcessor
from arguments import parse_args
from samples.lva_ai_extension.common.exception_handler import log_exception

def _log_options(args):
    heading = "Options for {}".format(os.path.basename(__file__))
    banner = "="*len(heading)
    logging.info(banner)
    logging.info(heading)
    logging.info(banner)
    for arg in vars(args):
        logging.info("{} == {}".format(arg, getattr(args, arg)))
        logging.info(banner)


def main():
    try:
        # Get application arguments
        args = parse_args()

        _log_options(args)

        # Run stream processer loop
        msp = MediaStreamProcessor(args.grpc_server_address,
                                   args.sample_file,
                                   args.loop_count,
                                   args.use_shared_memory)
        msp.start()

    except:
        log_exception()
        exit(-1)

if __name__ == "__main__":
    # Set logging parameters
    logging.basicConfig(
        level=logging.INFO,
        format='[AIXC] [%(asctime)-15s] [%(threadName)-12.12s] [%(levelname)s]: %(message)s',
        handlers=[
            #logging.FileHandler(LOG_FILE_NAME),     # write in a log file
            logging.StreamHandler(sys.stdout)       # write in stdout
        ]
    )

    # Call Main logic
    main()

    logging.info('Client finished execution')

