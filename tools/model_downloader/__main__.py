#!/usr/bin/env python3
'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import sys
import os
import config as cfg
from arguments import parse_args
from downloader import download

package_name = os.path.basename(os.path.dirname(__file__))

def print_args(args):
    heading = "Arguments for {}".format(package_name)
    banner = "="*len(heading)
    print(banner)
    print(heading)
    print(banner)
    for arg in vars(args):
        print("\t{} == {}".format(arg, getattr(args, arg)))
    print()


if __name__ == '__main__':

    args = parse_args()
    print_args(args)

    if (os.path.isfile(cfg.model_downloader) and
            os.path.isfile(cfg.model_converter) and
            os.path.isfile(cfg.model_optimizer)):
        download(args.model_list, args.output_dir, args.force)
    else:
        print("Necessary tools needed from Intel(R) distribution of OpenVINO(TM) Toolkit not "\
              "found. Please check if all dependant tools are installed and try again.")
        sys.exit(1)
