'''
* Copyright (C) 2019 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import os
import json

from vaserving.vaserving import VAServing

source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__) + "/.."))

request = {
    "source": {
        "uri": "file:///home/video-analytics-serving/samples/classroom.mp4",
        "type": "uri"
    },
    "destination": {
        "type": "file",
        "path": "/home/video-analytics-serving/tests/results.txt",
        "format": "json-lines"
    }
}


def test_vaserving():

    pipeline_tests = [("object_detection",
                       1, 'pinwheel.ts', 'object_detection.results.json'),
                      ("emotion_recognition",
                       1, 'classroom.mp4', 'emotion_recognition.results.json')]

    VAServing.start({'log_level': 'INFO'})

    output_files = []

    for pipeline, version, input_file, output_file in pipeline_tests:
        pipeline = VAServing.pipeline(pipeline, version)
        input_file = "file://{}".format(os.path.abspath(
            os.path.join(source_dir, 'samples', input_file)))
        output_file = "{}".format(os.path.abspath(
            os.path.join(source_dir, 'tests', output_file)))
        output_files.append(output_file)
        pipeline.start(request, source={'uri': input_file}, destination={
            'path': output_file})

    VAServing.wait()

    for pipeline in VAServing.pipeline_instances():
        print(pipeline.name())
        print(pipeline.status().state.name)

    for output_file in output_files:
        with open(output_file) as file:
            for x in file:
                if (len(x.strip()) != 0):
                    print(json.loads(x))

    VAServing.stop()

# def test_gstreamer():
#     model_manager = ModelManager()
#     model_manager.load_config(os.path.join(source_dir, "models"))
#     pipeline_manager = PipelineManager()
#     pipeline_manager.load_config(os.path.join(
#         source_dir, "pipelines"), 5)
#     pipelines = pipeline_manager.get_loaded_pipelines()
#     assert(len(pipelines) == 2)
#     for x in pipelines:
#         instance_id, error = pipeline_manager.create_instance(
#             x["name"], x["version"], request)
#         # pipeline_manager.stop_instance(
#         #   x["name"], x["version"], instance_id)
#         status = pipeline_manager.get_instance_status(
#             x["name"], x["version"], instance_id)

#         while(status["state"] not in ["COMPLETED", "ABORTED", "ERROR"]):
#             print(status)
#             time.sleep(1)
#             status = pipeline_manager.get_instance_status(
#                 x["name"], x["version"], instance_id)

#     GStreamerPipeline._mainloop.quit()
