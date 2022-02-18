'''
* Copyright (C) 2019 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import pytest
import re
import time
import sys
sys.path.append('/home/pipeline-server/client') # Temp fix before PYTHONPATH updated
import pipeline_client

SERVER_ADDRESS = "http://localhost:8080"

def test_pipeline_client(service, test_case, test_filename, generate, capsys):
    show_request = test_case.get('show_request', False)
    if test_case['test_function'] == 'run':
        server_address = test_case.get('server_address', SERVER_ADDRESS)
        request = pipeline_client.REQUEST_TEMPLATE
        request['source']['uri'] = test_case['uri']
        instance_id = pipeline_client.start_pipeline(server_address, test_case['pipeline'], request, show_request=show_request)
        assert instance_id is not None
        time.sleep(test_case['sleep_time_sec'])
        status = pipeline_client.get_pipeline_status(server_address, instance_id)
        assert status['state'] == 'RUNNING'
        pipeline_client.stop_pipeline(server_address, instance_id)
        status = pipeline_client.get_pipeline_status(server_address, instance_id)
        assert status['state'] == 'ABORTED'
    elif test_case['test_function'] == 'run_with_bad_detection_device':
        server_address = test_case.get('server_address', SERVER_ADDRESS)
        request = pipeline_client.REQUEST_TEMPLATE
        request['source']['uri'] = test_case['uri']
        request.update({'parameters' : {'detection-device' : test_case['detection_device']}})
        instance_id = pipeline_client.start_pipeline(server_address, test_case['pipeline'], request, show_request=show_request)
        with pytest.raises(ValueError):
            pipeline_client.wait_for_pipeline_completion(server_address, instance_id)
            captured = capsys.readouterr()
            assert test_case['expected_output'] in captured.out
        del request['parameters']
    elif test_case['test_function'] == 'start_pipeline':
        server_address = test_case.get('server_address', SERVER_ADDRESS)
        request = pipeline_client.REQUEST_TEMPLATE
        request['source']['uri'] = test_case['uri']
        try:
            instance_id = pipeline_client.start_pipeline(server_address, test_case['pipeline'], request, show_request=show_request)
            assert instance_id == test_case['expected_id']
            captured = capsys.readouterr()
            assert test_case['expected_output'] in captured.out
        except RuntimeError as exception:
            assert test_case['expected_output'] in str(exception)
    elif test_case['test_function'] == 'stop_pipeline':
        server_address = test_case.get('server_address', SERVER_ADDRESS)
        pipeline_client.stop_pipeline(server_address, test_case['instance_id'])
        captured = capsys.readouterr()
        assert test_case['expected_output'] in captured.out
    elif test_case['test_function'] == 'list_pipelines':
        server_address = test_case.get('server_address', SERVER_ADDRESS)
        if show_request:
            with pytest.raises(SystemExit):
                pipeline_client._list(server_address, 'pipelines', True)
            captured = capsys.readouterr()
            assert test_case['expected_output'] in captured.out
        else:
            pipeline_client._list(server_address, 'pipelines')
            captured = capsys.readouterr()
            assert re.fullmatch(test_case['regex'], captured.out) is not None
    elif test_case['test_function'] == 'list_models':
        server_address = test_case.get('server_address', SERVER_ADDRESS)
        if test_case['show_request']:
            with pytest.raises(SystemExit):
                pipeline_client._list(server_address, 'models', True)
            captured = capsys.readouterr()
            assert test_case['expected_output'] in captured.out
        else:
            pipeline_client._list(server_address, 'models')
            captured = capsys.readouterr()
            assert re.fullmatch(test_case['regex'], captured.out) is not None
    elif test_case['test_function'] == 'tags':
        server_address = test_case.get('server_address', SERVER_ADDRESS)
        request = pipeline_client.REQUEST_TEMPLATE
        request['source']['uri'] = test_case['uri']
        request['tags'] = test_case['tags']
        with pytest.raises(SystemExit):
            pipeline_client.start_pipeline(server_address, test_case['pipeline'], request, show_request=show_request)
        captured = capsys.readouterr()
        print("")
        print(test_case['expected_output'])
        print(captured.out)
        assert test_case['expected_output'] == captured.out
    else:
        pytest.fail()
