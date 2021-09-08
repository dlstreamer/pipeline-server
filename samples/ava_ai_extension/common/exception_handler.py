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

import linecache
import sys
import logging

def log_exception(logger=None):
    ex_type, ex_value, ex_traceback = sys.exc_info()

    tb_frame = ex_traceback.tb_frame
    line_no = ex_traceback.tb_lineno
    file_name = tb_frame.f_code.co_filename

    linecache.checkcache(file_name)
    line = linecache.getline(file_name, line_no, tb_frame.f_globals)

    ex_message = 'Exception:\n\tFile name: {0}\n\tLine number: {1}\n\tLine: {2}\n\tValue: {3}'\
        .format(file_name, line_no, line.strip(), ex_value)

    if (logger):
        logger.info(ex_message)
    else:
        logging.info(ex_message)

    return ex_type, ex_value, ex_traceback
