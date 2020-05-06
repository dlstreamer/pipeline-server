'''
* Copyright (C) 2019 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import os
import json
import requests
from collections import namedtuple
import pytest
import urllib

#        launch_response = requests.post(
 #           pipeline_url, json=request, timeout=TIMEOUT)
  #      if launch_response.status_code == 200:
   #         instance_id = int(launch_response.text)
    #        return instance_id

TIMEOUT = 30


#@pytest.mark.parametrize("test_case",[0],indirect=["test_case"])
def test_rest_api(service,test_case,test_filename,generate):
  
    url = urllib.parse.urljoin(service.host,test_case['path'])

    if (test_case["verb"]=="get"):
        response = requests.get(url,
                                json = test_case["body"],
                                timeout=TIMEOUT)
    else:
        assert False, "Unknown Test Case Verb"

    if (generate):
        test_case["status_code"]=response.status_code
        test_case["result"]=json.loads(response.text)
        with open(test_filename+'.generated',"w") as test_output:
            json.dump(test_case,test_output, indent=4)
    else:
        assert test_case["status_code"]==response.status_code, "Status Code Mismatch"
        assert test_case["result"]==json.loads(response.text), "Response Text Mismatch"

