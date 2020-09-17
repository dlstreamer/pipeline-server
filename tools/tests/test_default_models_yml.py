import os
import sys
import subprocess
import pytest
from check_directory import check_directory_yml

# Test the default models from models.list.yml
@pytest.mark.skip(reason="skipping until permission issue on openvino-data-dev image is resolved")
def test_default_models_yml(tmpdir,capfd):
    workdir_path = tmpdir.strpath
    model_folder_path = os.path.join(workdir_path, 'models')
    model_download_tool_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../model_downloader')
    model_yml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../model_downloader/models.list.yml')
    # Run the tool
    results = subprocess.run(['python3', model_download_tool_path, '--model-list', model_yml_path, '--output-dir', workdir_path, '--force'])

    # Set the path of expected output based on the yml file
    model_names = ["mobilenet-ssd", "emotions-recognition-retail-0003", "face-detection-adas-0001", "face-detection-retail-0004", "landmarks-regression-retail-0009"]
    version = 1
    if results.returncode != 0:
        captured = capfd.readouterr()
        assert 'Necessary tools needed from OpenVINO not found' in captured.out
    else:
        for num, name in enumerate(model_names):
            current_name = name
            current_version = version
        
            check_directory_yml(workdir_path, current_name, current_version)
