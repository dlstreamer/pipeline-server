'''
* Copyright (C) 2022 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''
from tests.common import results_processing
import os
import json

if os.environ['FRAMEWORK'] == "gstreamer":
    import gi
    # pylint: disable=wrong-import-order, wrong-import-position
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst
    # pylint: enable=wrong-import-order, wrong-import-position
else:
    print("TODO: Handle FFmpeg base image requirements")

def _check_plugins(needed, expect_missing):
    print("Plugin Check")
    missing = list(filter(lambda p: Gst.Registry.get().find_plugin(p) is None, needed))
    if missing:
        print("Missing gstreamer plugins: {}".format(missing))
        assert(missing == expect_missing), "Missing GStreamer Plugins: {}".format(missing)
        return False
    print("Successfully found required gstreamer plugins: {}".format(needed))
    return True

def test_image_requirements(PipelineServer, test_case, test_filename, generate):
    if "required_plugins" in test_case:
        needed = test_case["required_plugins"]
        expect_missing = test_case["expect_missing"]
        if generate:
            print("Generating list of available plugins found within test image...")
            plugins = Gst.Registry.get().get_plugin_list()
            results = []
            for plugin in plugins:
                results.append(plugin.get_name())
            test_case["generated_available_plugins"] = results
            with open(test_filename+'.generated', "w") as test_output:
                json.dump(test_case, test_output, indent=4)
        if expect_missing:
            assert not _check_plugins(needed, expect_missing), "Even expected missing plugins were found in test image!"
        else:
            assert _check_plugins(needed, expect_missing), "One or more plugins missing from test image!"
        return
