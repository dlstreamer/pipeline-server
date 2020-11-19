'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import os
import shutil
import shlex
import yaml
import config as cfg

def load_document(document_path):
    document = None
    try:
        with open(document_path) as document_file:
            if document_path.endswith('.yml'):
                document = yaml.safe_load(document_file)
            else:
                print("Please make sure model list file is in correct yml file format.")
                print("Expected Schema: ")
                print("- model(Required): mobilenet-ssd")
                print("  alias(Optional): object_detection")
                print("  version(Optional): 1")
                print("  precision(Optional): [FP16,FP32]")
    except Exception as error:
        print("Exception while loading yaml file. File could be malformed. "\
              "Please check the format and retry.")
        print(error)
    return document

def print_action(action, details=None):
    details = [] if details is None else details
    banner = "="*len(action)
    print(banner)
    print(action)
    print(banner)
    for detail in details:
        print("\t{}".format(detail))
    print()

def create_directory(directory, remove=True):
    if remove:
        try:
            print_action("Removing: {}".format(directory))
            shutil.rmtree(directory, ignore_errors=True)
        except Exception as error:
            print(error)

    print_action("Creating: {}".format(directory))
    os.makedirs(directory, exist_ok=True)

def create_download_command(model_name, output_dir, precisions):
    if precisions is not None:
        cmd = "python3 {0} --name {1} --precisions {2} -o {3}"
        return shlex.split(cmd.format(cfg.model_downloader,
                                      model_name,
                                      ','.join(map(str, precisions)),
                                      output_dir))
    cmd = "python3 {0} --name {1} -o {2}"
    return shlex.split(cmd.format(cfg.model_downloader,
                                  model_name,
                                  output_dir))

def create_convert_command(model_name, output_dir, precisions):
    if precisions is not None:
        cmd = "python3 {0} -d {3} --name {1} --precisions {2} -o {3} --mo {4}"
        return shlex.split(cmd.format(cfg.model_converter,
                                      model_name,
                                      ','.join(map(str, precisions)),
                                      output_dir,
                                      cfg.model_optimizer))
    cmd = "python3 {0} -d {2} --name {1} -o {2} --mo {3}"
    return shlex.split(cmd.format(cfg.model_converter,
                                  model_name,
                                  output_dir,
                                  cfg.model_optimizer))
