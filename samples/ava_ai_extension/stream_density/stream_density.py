import sys
import json
import parse
import time
from datetime import datetime
from enum import Enum, auto

class State(Enum):
    WAITING = auto()
    STARTING = auto()
    RUNNING = auto()
    STOPPING = auto()
    FINISHED = auto()

max_running_pipelines = 0
num_pipelines_running = 0
num_pipelines_stopped = 0
state = State.FINISHED
prev_state = State.FINISHED
achieved_stream_density = True
average_fps = 0
target_fps = 30

# 2021-10-11 20:17:10,017
def get_time(log_str):
    date = datetime.strptime(log_str, '%Y-%m-%d %H:%M:%S,%f')
    return date

with sys.stdin as log_file:
    for line in log_file:
        try:
            if state == State.FINISHED:
                state = State.WAITING
                print("Waiting for stream to start...")
                stream_density = 0
                stream_count = 0
                num_pipelines_running = 0
                average_fps = 0
                start_times = {}
                skip_test = False

            log_message = json.loads(line)
            if "levelname" in log_message and "message" in log_message:
                message = log_message["message"]
                result = parse.parse("Setting Pipeline {:d} State to RUNNING", message)
                if result:
                    instance = result[0]
                    start_time = get_time(log_message["asctime"])
                    if num_pipelines_running == 0:
                        print("Test started {}".format(start_time))
                        state = State.STARTING
                    num_pipelines_running += 1
                    print("Stream {} started.".format(num_pipelines_running))
                    start_times[instance] = start_time

                #Pipeline Ended Status: PipelineStatus(avg_fps=52.518904949277804, avg_pipeline_latency=None, elapsed_time=11.34829568862915, id=7, start_time=1633743733.8381126, state=<State.COMPLETED: 3>)
                else:
                    result = parse.parse("Pipeline Ended Status: PipelineStatus(avg_fps={:f}, avg_pipeline_latency=None, elapsed_time={:f}, id={:d}, start_time={:f}, state=<State.COMPLETED: {:d}>)", message)
                    if result:
                        (fps, elapsed_time, instance, start_time, status) = result
                        if status == 3:
                            if state != State.STOPPING:
                                num_pipelines_stopped = 1
                                stream_density = 0
                                stream_count = num_pipelines_running
                                state = State.STOPPING
                            fps = int(fps + 0.5)
                            average_fps = average_fps + fps
                            duration = int( (get_time(log_message["asctime"]) - start_times[instance]).total_seconds() + 0.5 )
                            if fps >= 30:
                                stream_density += 1
                            num_pipelines_running -= 1
                            if num_pipelines_running == 0:
                                state = State.FINISHED
                            if duration > 10:
                                print("Stream {} ended, duration = {}s, fps = {}".format(num_pipelines_stopped, duration, fps))
                            else:
                                print("Stream {} ended, duration = {}s".format(num_pipelines_stopped, duration))
                                skip_test = True
                            num_pipelines_stopped += 1
                if state != prev_state:
                    # print("state = {}".format(state))
                    if state == State.FINISHED:
                        if skip_test:
                            print("Test finished: Skipping stream density measurement due to short run.")
                        else:
                            average_fps = int(average_fps / stream_count + 0.5)
                            print("Test finished: {}/{} streams pass, average fps = {}".format(stream_density, stream_count, average_fps))
                    prev_state = state

        except ValueError as e:
            # print(e)
            pass
