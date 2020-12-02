'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import argparse

def parse_args(args=None):
    parser = argparse.ArgumentParser(description="Download & Convert models from Open Model Zoo.")
    parser.add_argument('--output-dir', required=False, default=".",
                        help='path where to save models')
    parser.add_argument('--model-list', default="models/models.list.yml",
                        help='input file with model names')
    parser.add_argument("--force", required=False, dest="force", action="store_true",
                        default=False, help='force the download')

    args = parser.parse_args(args)
    return args
