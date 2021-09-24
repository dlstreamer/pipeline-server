'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import sys
import os
import shutil
import subprocess
import tempfile
import shlex
from glob import glob
import requests
import yaml
from jsonschema import Draft7Validator, FormatChecker
from mdt_schema import model_list_schema

MODEL_OPTIMIZER_ROOT = (
    "/opt/intel/dldt"
    if os.path.isdir("/opt/intel/dldt")
    else "/opt/intel/openvino/deployment_tools"
)
OPEN_MODEL_ZOO_ROOT = os.path.join(MODEL_OPTIMIZER_ROOT, "open_model_zoo")
MODEL_DOWNLOADER_PATH = os.path.join(
    OPEN_MODEL_ZOO_ROOT, "tools/downloader/downloader.py"
)
MODEL_CONVERTER_PATH = os.path.join(
    OPEN_MODEL_ZOO_ROOT, "tools/downloader/converter.py"
)
MODEL_OPTIMIZER_PATH = (
    os.path.join(MODEL_OPTIMIZER_ROOT, "model-optimizer/mo.py")
    if MODEL_OPTIMIZER_ROOT == "/opt/intel/dldt"
    else os.path.join(MODEL_OPTIMIZER_ROOT, "model_optimizer/mo.py")
)

MODEL_PROC_ROOT = "/opt/intel/dl_streamer/samples/model_proc"
DL_STREAMER_REPO_ROOT = (
    "https://raw.githubusercontent.com/openvinotoolkit/dlstreamer_gst"
)
DLSTREAMER_VERSION_FILE = "/opt/intel/openvino/data_processing/dl_streamer/version.txt"
MODEL_PROC_SEARCH_PATH  = "/opt/intel/openvino/data_processing/dl_streamer/samples/model_proc/**/{0}.json"

def _validate_schema(model_list):
    try:
        validator = Draft7Validator(model_list_schema, format_checker=FormatChecker())
        validator.validate(model_list)
    except Exception as error:
        print("Yaml input schema validation error.")
        print(error)
        sys.exit(1)


def _load_model_list(model_list_path):
    model_list = None
    try:
        with open(model_list_path) as model_list_file:
            model_list = yaml.safe_load(model_list_file)
    except Exception:
        print("Exception while loading yaml file. File could be malformed.")
        print("Please make sure model list file is in correct yml file format.")
        print("Expected Schema: ")
        print("- model(Required): mobilenet-ssd")
        print("  alias(Optional): object_detection")
        print("  version(Optional): 1")
        print("  precision(Optional): [FP16,FP32]")

    if model_list is None:
        sys.exit(1)
    else:
        _validate_schema(model_list)
    return model_list


def _find_downloaded_model(model_name, download_dir):
    for root, directories, _ in os.walk(download_dir):
        if model_name in directories:
            return os.path.abspath(os.path.join(root, model_name))
    return None

def _copy_datadev_model_proc(target_dir, model_name, dl_streamer_version):
    result = None
    with open(DLSTREAMER_VERSION_FILE) as local_version:
        version = "v" + local_version.readline()
        if version.startswith(dl_streamer_version):
            model_proc = None
            search_path = MODEL_PROC_SEARCH_PATH.format(model_name)
            for model_proc in glob(search_path, recursive=True):
                break
            if model_proc:
                try:
                    result = shutil.copy(model_proc, os.path.join(target_dir, "{}.json".format(model_name)))
                    print("Copied model_proc to: {}".format(result))
                except PermissionError:
                    print("Permission denied copying model_proc")
                except:
                    print("Unexpected error:", sys.exc_info())
    return result

def _download_model_proc(target_dir, model_name, dl_streamer_version):
    model_proc = None
    if os.path.isdir(MODEL_PROC_ROOT):
        for root, _, files in os.walk(MODEL_PROC_ROOT):
            for filepath in files:
                if os.path.splitext(filepath)[0] == model_name:
                    model_proc = os.path.join(root, filepath)
    if model_proc:
        shutil.move(model_proc, os.path.join(target_dir, "{}.json".format(model_name)))
    else:
        url = "{0}/{1}/samples/model_proc/{2}.json".format(
            DL_STREAMER_REPO_ROOT, dl_streamer_version, model_name
        )
        response = requests.get(url)
        with tempfile.TemporaryDirectory() as temp_dir:
            if response.status_code == 200:
                with open(
                        "{0}/{1}.json".format(temp_dir, model_name), "wb"
                ) as out_file:
                    out_file.write(response.content)
                print(
                    "Downloaded {0} model-proc file from gst-video-analytics repo".format(
                        model_name
                    )
                )
                model_proc = os.path.abspath(
                    "{0}/{1}.json".format(temp_dir, model_name)
                )
                shutil.move(model_proc, os.path.join(target_dir, "{}.json".format(model_name)))
            else:
                print("WARNING: model-proc not found in gst-video-analytics repo!")


def _create_convert_command(model_name, output_dir, precisions):
    if precisions:
        cmd = "python3 {0} -d {3} --name {1} --precisions {2} -o {3} --mo {4}"
        return shlex.split(
            cmd.format(
                MODEL_CONVERTER_PATH,
                model_name,
                ",".join(map(str, precisions)),
                output_dir,
                MODEL_OPTIMIZER_PATH,
            )
        )
    cmd = "python3 {0} -d {2} --name {1} -o {2} --mo {3}"
    return shlex.split(
        cmd.format(MODEL_CONVERTER_PATH, model_name, output_dir, MODEL_OPTIMIZER_PATH)
    )


def _create_download_command(model_name, output_dir, precisions):
    if precisions:
        cmd = "python3 {0} --name {1} --precisions {2} -o {3}"
        return shlex.split(
            cmd.format(
                MODEL_DOWNLOADER_PATH,
                model_name,
                ",".join(map(str, precisions)),
                output_dir,
            )
        )
    cmd = "python3 {0} --name {1} -o {2}"
    return shlex.split(cmd.format(MODEL_DOWNLOADER_PATH, model_name, output_dir))


def _run_command(command, model_name, step):
    print(" ".join(command))
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        print("Error occured while {0} {1} model.".format(step, model_name))
        print("Please remove from input yml file and try again.")
        sys.exit(1)


def _download_model(model_name, output_dir, precisions):
    command = _create_download_command(model_name, output_dir, precisions)
    _run_command(command, model_name, "downloading")


def _convert_model(model_name, output_dir, precisions):
    command = _create_convert_command(model_name, output_dir, precisions)
    _run_command(command, model_name, "converting")


def _get_model_properties(model, model_list_path, target_root):
    result = model
    if not isinstance(model, dict):
        result = {}
        result["model"] = model
    result.setdefault("alias", result["model"])
    result.setdefault("version", 1)
    result.setdefault("precision", None)
    result.setdefault("model-proc", None)
    if result["model-proc"]:
        result["model-proc"] = os.path.abspath(
            os.path.join(os.path.dirname(model_list_path), result["model-proc"])
        )
    result["target-dir"] = os.path.join(target_root,
                                        result["alias"],
                                        str(result["version"]))
    return result


def _download_and_convert_model(
        target_root, model, force, model_list_path, dl_streamer_version
):
    model_properties = _get_model_properties(model, model_list_path, target_root)
    model_name = model_properties["model"]
    precision = model_properties["precision"]
    model_proc = model_properties["model-proc"]
    target_dir = model_properties["target-dir"]

    if (not force) and (os.path.isdir(target_dir)):
        print("Model Directory {0} Exists - Skipping".format(target_dir))
        return

    if os.path.isdir(target_dir):
        shutil.rmtree(target_dir)

    with tempfile.TemporaryDirectory() as output_dir:
        _download_model(model_name, output_dir, precision)
        _convert_model(model_name, output_dir, precision)
        downloaded_model_path = _find_downloaded_model(model_name, output_dir)
        for path in os.listdir(downloaded_model_path):
            source = os.path.join(downloaded_model_path, path)
            target = os.path.join(target_dir, path)
            if os.path.isdir(source):
                shutil.move(source, target)

        if model_proc:
            if os.path.isfile(model_proc):
                shutil.copy(model_proc, target_dir)
            else:
                print("Error, model-proc {} specified but not found", model_proc)
                sys.exit(1)
        else:
            if _copy_datadev_model_proc(target_dir, model_name, dl_streamer_version) is None:
                _download_model_proc(target_dir, model_name, dl_streamer_version)


def download_and_convert_models(
        model_list_path, output_dir, force, dl_streamer_version
):
    model_list = _load_model_list(model_list_path)
    target_root = os.path.join(output_dir, "models")
    os.makedirs(target_root, exist_ok=True)

    for model in model_list:
        _download_and_convert_model(
            target_root, model, force, model_list_path, dl_streamer_version
        )
