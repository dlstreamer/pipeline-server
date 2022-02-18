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

def test_initialization(PipelineServer, test_case, test_filename, generate):
    test_prefix = os.path.splitext(os.path.basename(test_filename))[0]
    test_model_dir = os.path.join(os.path.dirname(test_filename),
                                  "{0}_models".format(test_prefix))
    test_pipeline_dir = os.path.join(os.path.dirname(test_filename),
                                     "{0}_pipelines".format(test_prefix))
    if "model_dir" not in test_case["options"]:
        if os.path.isdir(test_model_dir):
            test_case["options"]["model_dir"] = test_model_dir

    if ("pipeline_dir" not in test_case["options"]):
        if (os.path.isdir(test_pipeline_dir)):
            test_case["options"]["pipeline_dir"] = test_pipeline_dir

    if ("exception" in test_case):
        exception_class = None
        if (test_case["exception"]["type"] in globals()):
            exception_class = globals()[test_case["exception"]["type"]]
        elif (test_case["exception"]["type"] in __builtins__):
            exception_class = __builtins__[test_case["exception"]["type"]]

        with pytest.raises(exception_class) as exception:
            PipelineServer.start(test_case["options"])

        if("value" in test_case["exception"]):
            assert(str(exception.value) == test_case["exception"]["value"])
    else:
        PipelineServer.start(test_case["options"])

    PipelineServer.stop()
