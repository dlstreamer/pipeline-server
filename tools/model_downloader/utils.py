'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import os
import shutil
import yaml
import shlex
import config as cfg

def load_document(document_path):
    document = None
    try:
        with open(document_path) as document_file:
            if document_path.endswith('.yml'):
                document = yaml.full_load(document_file)
            else:
                print("Model list is not of correct format. It must be a .yml file.")
    except Exception as error:
        print(error)
    return document
    
def print_action(action,details=[]):
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
            shutil.rmtree(directory,ignore_errors=True)
        except Exception as error:
            print(error)

    print_action("Creating: {}".format(directory))
    os.makedirs(directory,exist_ok=True)

def create_download_command(model_name, output_dir, precisions):
    if precisions != None:
        return shlex.split("python3 {0} --name {1} --precisions {2} -o {3}".format(cfg.model_downloader,
                                                              model_name,
                                                              ','.join(map(str,precisions)),
                                                              output_dir))
    else:
        return shlex.split("python3 {0} --name {1} -o {2}".format(cfg.model_downloader,
                                                              model_name,
                                                              output_dir))

def create_convert_command(model_name, output_dir, precisions):
    if precisions != None:
        return shlex.split("python3 {0} -d {3} --name {1} --precisions {2} -o {3} --mo {4}".format(cfg.model_converter,
                                                                              model_name,
                                                                              ','.join(map(str,precisions)),
                                                                              output_dir,
                                                                              cfg.model_optimizer))
    else:
        return shlex.split("python3 {0} -d {2} --name {1} -o {2} --mo {3}".format(cfg.model_converter,
                                                                              model_name,
                                                                              output_dir,
                                                                              cfg.model_optimizer))