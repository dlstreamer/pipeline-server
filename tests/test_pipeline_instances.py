'''
* Copyright (C) 2019 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import time
from server.pipeline import Pipeline
import signal
import sys

PAUSE = 0.1

def wait_for_pipeline_state(pipeline_manager, pipelines, target_states):
    matches_target_state = False
    print("Waiting for {} pipelines to be {}".format(len(pipelines), target_states))
    timed_out = False
    start_time = time.time()
    max_time = 4 * len(pipelines)
    while not matches_target_state and not timed_out:
        matches_target_state = True
        statuses = pipeline_manager.get_all_instance_status()
        # print(statuses)
        assert len(statuses) == len(pipelines), "Incorrect number of instance entries"
        for index, status in enumerate(statuses):
            result = pipeline_manager.get_instance_summary(status["id"])
            assert result, "get_instance_parameters failed"
            expected_pipeline = pipelines[index]
            pipeline = result["request"]["pipeline"]
            assert pipeline["name"] == expected_pipeline["name"], "Pipeline name mismatch"
            assert pipeline["version"] == expected_pipeline["version"], "Pipeline version mismatch"
            if status["state"] not in target_states:
                matches_target_state = False
        time.sleep(PAUSE)
        if time.time() - start_time > max_time:
            timed_out = True
    print("Pipelines {} in {:.2f}s".format(target_states, time.time() - start_time))
    assert not timed_out, "Timed out waiting for pipeline states to reach {}".format(target_states)

def test_pipeline_instances(PipelineServer, test_case, test_filename, generate, numerical_tolerance, skip_sources):
    PipelineServer.start(test_case["options"])
    pipeline_instances = []
    test_case_pipelines = []
    iterations = test_case.get("iterations", 1)
    for _ in range(iterations):
        for tc in test_case["pipelines"]:
            pipeline_instance = PipelineServer.pipeline(tc["name"], tc["version"])
            assert pipeline_instance is not None, "Failed to Load Pipeline!"
            pipeline_instance.start(tc["request"])
            pipeline_instances.append(pipeline_instance)
            test_case_pipelines.append(tc)
    if "start_delay" in test_case:
        time.sleep(test_case["start_delay"])
    wait_for_pipeline_state(PipelineServer.pipeline_manager, test_case_pipelines, [Pipeline.State.COMPLETED, Pipeline.State.RUNNING])
    if "abort_delay" in test_case:
        abort_delay = test_case["abort_delay"]
        print("Pipelines running - stop in {}s".format(abort_delay))
        time.sleep(abort_delay)
    for pipeline_instance in pipeline_instances:
        pipeline_instance.stop()
    wait_for_pipeline_state(PipelineServer.pipeline_manager, test_case_pipelines, [Pipeline.State.COMPLETED, Pipeline.State.ABORTED])
    PipelineServer.stop()
