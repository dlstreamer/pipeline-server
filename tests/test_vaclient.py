'''
* Copyright (C) 2019 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import pytest
import re
import time
import sys
sys.path.append('/home/video-analytics-serving/vaclient') # Temp fix before PYTHONPATH updated
import vaclient

def test_vaclient(service, test_case, test_filename, generate, capsys):
    if test_case['test_function'] == 'run':
        request = vaclient.REQUEST_TEMPLATE
        request['source']['uri'] = test_case['uri']
        instance_id = vaclient.start_pipeline(request, test_case['pipeline'], show_request=False)
        assert instance_id is not None
        assert instance_id > 0
        time.sleep(test_case['sleep_time_sec'])
        status = vaclient.get_pipeline_status(test_case['pipeline'], instance_id)
        assert status['state'] == 'RUNNING'
        vaclient.stop_pipeline(test_case['pipeline'], instance_id)
        status = vaclient.get_pipeline_status(test_case['pipeline'], instance_id)
        assert status['state'] == 'ABORTED'
    elif test_case['test_function'] == 'start_pipeline':
        request = vaclient.REQUEST_TEMPLATE
        request['source']['uri'] = test_case['uri']
        instance_id = vaclient.start_pipeline(request, test_case['pipeline'], show_request=False)
        assert instance_id == test_case['expected_id']
        captured = capsys.readouterr()
        assert test_case['expected_output'] in captured.out
    elif test_case['test_function'] == 'stop_pipeline':
        vaclient.stop_pipeline(test_case['pipeline'], test_case['instance_id'])
        captured = capsys.readouterr()
        assert test_case['expected_output'] in captured.out
    elif test_case['test_function'] == 'list_pipelines':
        if test_case['show_request']:
            with pytest.raises(SystemExit):
                vaclient._list('pipelines', True)
            captured = capsys.readouterr()
            assert test_case['expected_output'] in captured.out
        else:
            vaclient._list('pipelines')
            captured = capsys.readouterr()
            assert re.fullmatch(test_case['regex'], captured.out) is not None
    elif test_case['test_function'] == 'list_models':
        if test_case['show_request']:
            with pytest.raises(SystemExit):
                vaclient._list('models', True)
            captured = capsys.readouterr()
            assert test_case['expected_output'] in captured.out
        else:
            vaclient._list('models')
            captured = capsys.readouterr()
            assert re.fullmatch(test_case['regex'], captured.out) is not None
    else:
        pytest.fail()
