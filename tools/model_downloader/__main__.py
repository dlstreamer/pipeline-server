#!/usr/bin/env python3
'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import sys
import os
from arguments import parse_args
import downloader


def _print_args(args):
    package_name = os.path.basename(os.path.dirname(__file__))
    heading = "Arguments for {}".format(package_name)
    banner = "=" * len(heading)
    print(banner)
    print(heading)
    print(banner)
    for arg in vars(args):
        print("\t{} == {}".format(arg, getattr(args, arg)))
    print()


def main():
    args = parse_args()
    _print_args(args)

    if (
            os.path.isfile(downloader.MODEL_DOWNLOADER_PATH)
            and os.path.isfile(downloader.MODEL_CONVERTER_PATH)
            and os.path.isfile(downloader.MODEL_OPTIMIZER_PATH)
    ):
        downloader.download_and_convert_models(
            args.model_list, args.output_dir, args.force, args.dl_streamer_version
        )
    else:
        print(
            "Intel(R) distribution of OpenVINO(TM) Toolkit tools not "
            "found. Please check if all dependent tools are installed and try again."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
