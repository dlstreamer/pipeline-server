import os
import sys
import subprocess
import pytest
from check_directory import check_directory

class TestClassAliasVersion:
    # Utilizing the tmp_path fixture
    @pytest.mark.skip(reason="integrate once tool is integrated with vaserving")
    def test_w_alias_w_version(self, tmpdir):
        workdir_path = tmpdir.strpath
        model_download_tool_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../model_download_tool.sh')
        # Run the tool
        subprocess.call([model_download_tool_path, '--specific-model', 'mobilenet-ssd,object_detection,4', '--output-dir', workdir_path, '--quiet'])

        name = 'mobilenet-ssd'
        alias = 'object_detection'
        version = 4

        check_directory(workdir_path, name, alias, version)

    @pytest.mark.skip(reason="integrate once tool is integrated with vaserving")
    def test_w_alias_wo_version(self, tmpdir):
        workdir_path = tmpdir.strpath
        model_download_tool_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../model_download_tool.sh')

        # Run the tool
        subprocess.call([model_download_tool_path, '--specific-model', 'mobilenet-ssd,object_detection', '--output-dir', workdir_path, '--quiet'])

        name = 'mobilenet-ssd'
        alias = 'object_detection'

        check_directory(workdir_path, name, alias)

    @pytest.mark.skip(reason="integrate once tool is integrated with vaserving")
    def test_wo_alias_w_version(self, tmpdir):
        workdir_path = tmpdir.strpath
        model_download_tool_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../model_download_tool.sh')

        # Run the tool
        subprocess.call([model_download_tool_path, '--specific-model', 'mobilenet-ssd,,2', '--output-dir', workdir_path, '--quiet'])

        name = 'mobilenet-ssd'
        version = 2

        check_directory(workdir_path, name, None, version)

    @pytest.mark.skip(reason="integrate once tool is integrated with vaserving")
    def test_wo_alias_wo_version(self, tmpdir):
        workdir_path = tmpdir.strpath
        model_download_tool_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../model_download_tool.sh')

        # Run the tool
        subprocess.call([model_download_tool_path, '--specific-model', 'mobilenet-ssd', '--output-dir', workdir_path, '--quiet'])

        name = 'mobilenet-ssd'

        check_directory(workdir_path, name)
