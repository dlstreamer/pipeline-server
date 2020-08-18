import os
import sys
import subprocess
import pytest
from check_directory import check_directory

# Utilizing the tmp_path fixture
@pytest.mark.skip(reason="integrate once tool is integrated with vaserving")
def test_default_models(tmpdir):
    workdir_path = tmpdir.strpath
    model_folder_path = os.path.join(workdir_path, 'models')
    model_download_tool_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../model_download_tool.sh')
    model_csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../models.csv')
    # Run the tool
    subprocess.call([model_download_tool_path, '--model-list', model_csv_path, '--output-dir', workdir_path, '--quiet'])

    # Set the path of expected output based on the csv file
    model_names = ["mobilenet-ssd", "emotions-recognition-retail-0003", "face-detection-adas-0001", "face-detection-retail-0004", "face-reidentification-retail-0095", "landmarks-regression-retail-0009"]
    model_alias = ["object_detection", "emotions_recognition", "face_detection_adas", "face_detection_retail", "face_reidentification", "landmarks_regression"]
    version = 1
    
    for num, name in enumerate(model_names):
        current_name = name
        current_alias = model_alias[num]
        current_version = version

        check_directory(workdir_path, current_name, current_alias, current_version)
