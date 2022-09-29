'''
* Copyright (C) 2019 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import os
import json
import requests
import pytest
import urllib

TIMEOUT = 30

#@pytest.mark.parametrize("test_case",[0],indirect=["test_case"])
def test_rest_api(service, test_case, test_filename, generate):
    url = urllib.parse.urljoin(service.host, test_case['path'])
    if test_case["verb"] == "get":
        response = requests.get(url,
                                json=test_case["body"],
                                timeout=TIMEOUT)
    elif test_case["verb"] == "delete":
        response = requests.delete(url,
                                   json=test_case["body"],
                                   timeout=TIMEOUT)
    elif test_case["verb"] == "post":
        response = requests.post(url,
                                 json=test_case["body"],
                                 timeout=TIMEOUT)
    else:
        assert False, "Unknown Test Case Verb"
    if generate:
        test_case["status_code"] = response.status_code
        with open(test_filename+'.generated', "w") as test_output:
            json.dump(test_case, test_output, indent=4)
    else:
        assert test_case["status_code"] == response.status_code, "Status Code Mismatch"
        if "result" in test_case:
            comparison = json.loads(response.text)
            expected = test_case["result"]
            assert type(comparison) == type(expected), "Response Type Mismatch"
            if isinstance(expected, list):
                if 'sort_key' in test_case:
                    sort_key = test_case['sort_key']
                    if 'secondary_sort_key' in test_case:
                        secondary_sort_key = test_case['secondary_sort_key']
                        # Sort with primary and secondary keys
                        expected = sorted(expected, key=lambda x: (x[sort_key], str(x[secondary_sort_key])))
                        comparison = sorted(comparison, key=lambda x: (x[sort_key], str(x[secondary_sort_key])))
                        assert comparison == expected, "Response Value Mismatch"
                    else:
                        # Sort with primary key only
                        expected = sorted(expected, key=lambda x: x[sort_key])
                        comparison = sorted(comparison, key=lambda x: x[sort_key])
                        assert comparison == expected, "Response Value Mismatch"
                else:
                    assert len(comparison) == len(expected), "Response List Length Mismatch"
                    for entry in expected:
                        assert entry in comparison, "Response Value Mismatch"
