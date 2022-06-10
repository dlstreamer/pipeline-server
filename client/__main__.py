#!/usr/bin/python3
'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import sys
from arguments import parse_args

def main():
    """Program entrypoint"""
    try:
        args = parse_args()
        args.command(args)
    except Exception as error:
        print(error)
        sys.exit(1)

if __name__ == "__main__":
    main()
