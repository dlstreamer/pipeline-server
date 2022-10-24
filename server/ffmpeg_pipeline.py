'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import string
import shlex
import subprocess
import time
import copy
from threading import Lock
from threading import Thread
import shutil
import re
from collections import OrderedDict
from collections import namedtuple
from collections import Counter
import json
import os
from datetime import datetime, timedelta

from server.pipeline import Pipeline
from server.common.utils import logging


if shutil.which('ffmpeg') is None:
    raise Exception("ffmpeg not installed")


class FFmpegPipeline(Pipeline):

    SECONDS_TO_NANOSECONDS = 10**9

    GVA_INFERENCE_FILTER_TYPES = ["detect",
                                  "classify"]

    FilterPropertyConfig = namedtuple("FilterPropertyConfig",
                                      ["name",
                                       "type",
                                       "property",
                                       "enum_values",
                                       "index",
                                       "format"])
    VideoFilters = namedtuple("VideoFilters", ["range", "token", "filters"])
    VideoFilter = namedtuple("VideoFilter", ["name", "index", "properties"])
    Input = namedtuple("Input", ["range", "token", "properties"])
    Output = namedtuple("Output", ["range", "token", "format", "properties"])

    def __init__(self, identifier, config, model_manager, request, finished_callback, options):
        # TODO: refactor as abstract interface
        # pylint: disable=super-init-not-called
        self.config = config
        self.models = model_manager.models
        self.model_manager = model_manager
        self.template = config['template']
        self.identifier = identifier
        self._process = None
        self.start_time = None
        self.stop_time = None
        self._ffmpeg_launch_string = None
        self.request = request
        self.state = Pipeline.State.QUEUED
        self.fps = 0
        self._finished_callback = finished_callback
        self._logger = logging.get_logger('FFmpegPipeline', is_static=True)
        self._fps_regex = re.compile(
            r"\s*frame=\s*(?P<frame_count>\d+)\s*fps=\s*(?P<fps>\d+\.?\d*).*"
            r"time=(?P<duration>\d+:\d+:\d+\.\d+).*speed=\s*(?P<speed>\d+\.\d+)x")
        self._recording_started_regex = re.compile(
            r"\[segment @ 0x.*?\] Opening '(.*?)' for writing")
        self._recording_prefix = None
        self._current_recording = None
        self._stream_base = None
        self._real_base = None
        self._temp_recording_dir = None
        self._recording_dir = None
        self._ffmpeg_args = None
        self._video_filters = None
        self._inputs = None
        self._outputs = None
        self._create_delete_lock = Lock()
        self._video_filter_index = Counter()
        self._video_filter_map = {}
        self._output_format_index = Counter()
        self._output_format_map = {}
        self.pipeline_type = "FFmpeg"
        self._options = options

    def stop(self):
        with self._create_delete_lock:
            if (not self.state.stopped()):
                self.state = Pipeline.State.ABORTED
        return self.status()

    def params(self):
        # TODO: refactor common code
        request = copy.deepcopy(self.request)
        if "models" in request:
            del request["models"]
        if not self._options.emit_source_and_destination:
            self._logger.debug("Not emitting source or destination."\
                "Launch server with --emit-source-and-destination if desired.")
            if "source" in request:
                del request["source"]
            if "destination" in request:
                del request["destination"]

        params_obj = {
            "id": self.identifier,
            "request": request,
            "type": self.config["type"],
            "launch_command": self._ffmpeg_launch_string
        }

        return params_obj

    def status(self):
        self._logger.debug("Called Status")
        if self.stop_time is not None:
            elapsed_time = self.stop_time - self.start_time
        elif self.start_time is not None:
            elapsed_time = time.time() - self.start_time
        else:
            elapsed_time = None
        status_obj = {
            "id": self.identifier,
            "state": self.state,
            "avg_fps": self.fps,
            "start_time": self.start_time,
            "elapsed_time": elapsed_time
        }

        return status_obj

    @staticmethod
    def validate_config(config, request):
        pass

    def _get_fps(self, next_line):

        # Note: ffmpeg doesn't immediately report fps
        #       which can cause issues for short clips
        #       We calculate it if fps is 0 otherwise we
        #       report what ffmpeg provides

        matched = self._fps_regex.match(next_line)
        if (matched):
            fps = float(matched.group('fps'))

            if (fps > 0):
                self.fps = fps
                return

            speed = float(matched.group("speed"))
            frame_count = int(matched.group("frame_count"))
            time_value = datetime.strptime(
                matched.group("duration"), "%H:%M:%S.%f")
            duration = timedelta(
                hours=time_value.hour,
                minutes=time_value.minute,
                seconds=time_value.second,
                microseconds=time_value.microsecond)
            self.fps = (frame_count / (duration.total_seconds())) * speed

    def _check_for_started_recording(self, next_line):

        # We check when a new segment is started to indicate
        # when the current segment is complete and can be moved

        if self._recording_prefix:
            matched = self._recording_started_regex.match(next_line)
            if (matched):
                self._move_current_recording()
                self._current_recording = matched.groups()[0]

    def _get_stream_time(self, recording):
        args = ["ffprobe", "-show_entries", "stream=start_time",
                "-print_format", "json", "-v", "quiet", "-hide_banner", recording]

        result = json.loads(subprocess.check_output(args))
        if (('streams' in result) and
                (len(result['streams']) > 0) and
                ('start_time' in result['streams'][0])):

            start_time = int(float(result['streams'][0]['start_time']) * 10**9)

        if (not self._stream_base):
            self._stream_base = start_time
        return start_time - self._stream_base

    def _move_current_recording(self):
        if (self._current_recording):
            stream_time = self._get_stream_time(self._current_recording)
            adjusted_time = self._real_base + stream_time
            local_time = time.localtime(
                adjusted_time / FFmpegPipeline.SECONDS_TO_NANOSECONDS)
            dir_name = time.strftime(
                "{}/%Y/%m/%d".format(self._recording_prefix), local_time)

            if (dir_name != self._recording_dir):
                os.makedirs(dir_name, exist_ok=True)
                self._recording_dir = dir_name

            filename = "{dirname}/{adjustedtime}_{time}.mp4".format(
                dirname=dir_name,
                adjustedtime=adjusted_time,
                time=stream_time)

            os.rename(self._current_recording, filename)

    def _spawn(self, args):
        self._logger.debug("Launching: %s ", ' '.join(args))
        with self._create_delete_lock:
            if not self.state is Pipeline.State.ABORTED:

                self._process = subprocess.Popen(args, #pylint: disable=consider-using-with
                                                 stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE,
                                                 bufsize=1,
                                                 universal_newlines=True)
                self.state = Pipeline.State.RUNNING
            else:
                self._finished_callback()
                return

        self._process.poll()
        while self._process.returncode is None and not self.state is Pipeline.State.ABORTED:
            next_line = self._process.stderr.readline()
            self._logger.debug(next_line)
            self._get_fps(next_line)
            self._check_for_started_recording(next_line)
            self._process.poll()
        self.stop_time = time.time()

        with self._create_delete_lock:
            if self.state is Pipeline.State.ABORTED:
                self._process.kill()
            else:
                if self._process.returncode == 0:
                    self.state = Pipeline.State.COMPLETED
                else:
                    self.state = Pipeline.State.ERROR
            self._process = None

        self._finished_callback()

    def _get_filter_properties(self, _filter):
        result = {}
        params = re.split("=|:", _filter)
        result['_TYPE_'] = params[0]
        result['_ORIG_'] = _filter
        for x in range(1, len(params[0:]), 2):
            result[params[x]] = params[x + 1]
        return result

    def _join_filter_params(self, filter_type, filter_params):
        parameters = ["%s=%s" % (x, y) for (x, y) in filter_params.items()]
        return "{filter_type}={params}".format(filter_type=filter_type, params=':'.join(parameters))

    def _set_default_models(self):
        for video_filters in self._video_filters:
            for _filter_key, _filter in video_filters.filters.items():
                if ((_filter_key[0] in FFmpegPipeline.GVA_INFERENCE_FILTER_TYPES)
                        and ("VA_DEVICE_DEFAULT" in _filter.properties['model'])):

                    if "device" not in _filter.properties:
                        _filter.properties["device"] = "CPU"

                    _filter.properties["model"] = self.model_manager.get_default_network_for_device(
                        _filter.properties["device"], _filter.properties["model"])

                    self._logger.debug("Setting model to {} for filter {}".format(
                        _filter.properties["model"], _filter_key))

    def _set_model_proc(self):
        for video_filters in self._video_filters:
            for _filter_key, _filter in video_filters.filters.items():
                if ((_filter_key[0] in FFmpegPipeline.GVA_INFERENCE_FILTER_TYPES)):
                    if "model_proc" not in _filter.properties:
                        model_proc = None
                        if _filter.properties["model"] in self.model_manager.model_procs:
                            model_proc = self.model_manager.model_procs[_filter.properties["model"]]
                        if model_proc is not None:
                            _filter.properties["model_proc"] = model_proc
                            self._logger.debug("Setting model proc to {} for filter {}".format(
                                model_proc, _filter_key))

    def _unescape_args(self, args):
        for i, arg in enumerate(args):
            args[i] = arg.replace(
                '_COLON_', ':') if isinstance(arg, str) else arg

    def _escape_source(self):
        if "source" in self.request and "uri" in self.request["source"]:
            self.request["source"]["uri"] = self.request["source"]["uri"].replace(
                ':', '_COLON_')

    def _unescape_source(self):
        if "source" in self.request and "uri" in self.request["source"]:
            self.request["source"]["uri"] = self.request["source"]["uri"].replace(
                '_COLON_', ':')

    def _get_filter_property_config(self, _filter, config):
        enum_values = None

        if (("enum" in config) and ("values" in _filter)):
            enum_values = dict(zip(config["enum"], _filter["values"]))

        return FFmpegPipeline.FilterPropertyConfig(_filter["name"],
                                                   _filter["type"],
                                                   _filter.get(
                                                       "property", None),
                                                   enum_values,
                                                   _filter.get("index", 0),
                                                   _filter.get("format", None))

    def _set_video_filter_property(self, _filter, _value):

        key = (_filter.name, _filter.index)
        if (key in self._video_filter_map):

            if (_filter.enum_values):
                _value = _filter.enum_values[_value]

            if _filter.name == "metaconvert" and _filter.property == "source":
                if not self._options.emit_source_and_destination:
                    self._logger.debug("Not emitting source or destination."\
                        "Launch server with --emit-source-and-destination if desired.")
                    return

            if (_filter.format == 'json'):
                _value = "\'{}\'".format(json.dumps(
                    _value).replace(':', r'\:'))
            self._logger.debug("Setting filter: {}, property: {}, value: {}".format(
                key,
                _filter.property,
                _value))

            self._video_filter_map[key].properties[_filter.property] = _value

    def _set_input_property(self, _filter, _value):
        if (_filter.index < len(self._inputs)):

            _input = self._inputs[_filter.index]

            if (_filter.enum_values):
                _value = _filter.enum_values[_value]

            if (_filter.format == 'json'):
                _value = "\'{}\'".format(json.dumps(
                    _value).replace(':', r'\:'))

            if (_filter.property.endswith("_ARG_")):
                _input.properties["_ARGS_"] = ([
                    _value
                    if arg == _filter.property else arg
                    for arg in _input.properties["_ARGS_"]
                ])

            self._logger.debug("Setting input: {}, property: {}, value: {}".format(
                (_filter.name, _filter.index),
                _filter.property,
                _value))

    def _set_output_property(self, _filter, _value):
        key = (_filter.name, _filter.index)
        if (key in self._output_format_map):

            _output = self._output_format_map[key]

            if (_filter.enum_values):
                _value = _filter.enum_values[_value]

            if (_filter.format == 'json'):
                _value = "\'{}\'".format(json.dumps(
                    _value).replace(':', r'\:'))

            if ((_filter.name == "metapublish" and _filter.property == "_METAPUBLISH_ARG_") and
                    (not _output.properties["_ARGS_"])):
                _output.properties["_ARGS_"].append("_METAPUBLISH_ARG_")

            if (_filter.property.endswith("_ARG_")):
                _output.properties["_ARGS_"] = ([
                    _value
                    if arg == _filter.property else arg
                    for arg in _output.properties["_ARGS_"]
                ])
            else:
                _output.properties[_filter.property] = _value

            self._logger.debug("Setting Output: {}, property: {}, value: {}".format(
                key,
                _filter.property,
                _value))

    def _set_filter_property(self, _filter, _value):

        if (_filter.type == "video"):
            self._set_video_filter_property(_filter, _value)
        elif(_filter.type == "input"):
            self._set_input_property(_filter, _value)
        elif(_filter.type == "output"):
            self._set_output_property(_filter, _value)

    def _set_section_properties(self, request_section, config_section):
        request, config = Pipeline.get_section_and_config(
            self.request, self.config, request_section, config_section)

        for key in config:
            if isinstance(config[key], dict) and "filter" in config[key]:
                if key in request:
                    if isinstance(config[key]["filter"], list):
                        filter_properties = [self._get_filter_property_config(x, config[key])
                                             for x in config[key]["filter"]]
                    else:
                        filter_properties = [self._get_filter_property_config(
                            config[key]["filter"], config[key])]

                    for _filter in filter_properties:
                        self._set_filter_property(_filter, request[key])

    def _set_properties(self):
        self._set_section_properties(["parameters"],
                                     ["parameters", "properties"])
        self._set_section_properties(["destination"],
                                     ["destination", "properties"])
        if "destination" in self.request and \
                "metadata" in self.request["destination"] and \
                    "type" in self.request["destination"]["metadata"]:
            self._set_section_properties(["destination", "metadata"],
                                         ["destination", "metadata",
                                          self.request["destination"]["metadata"]["type"],
                                          "properties"])
        self._set_section_properties(["source"],
                                     ["source", "properties"])
        if "source" in self.request and "type" in self.request["source"]:
            self._set_section_properties(["source"],
                                         ["source", self.request["source"]["type"], "properties"])
        self._set_section_properties([], [])

    def _get_outputs(self, args):
        # pylint: disable=unsupported-assignment-operation,unsubscriptable-object
        result = []
        args_remaining = len(args)
        indices = [args_remaining - (x + 1) for x in range(len(args))]
        current_output_properties = None
        current_output_list = None
        current_start = None
        while(args_remaining):
            index = indices[args_remaining - 1]
            if (current_output_properties is not None):
                if args[index].startswith('-'):
                    if (current_output_list is None):
                        current_output_properties[args[index]
                                                  ] = args[index + 1]
                        args_remaining -= 2
                        continue
                    output_index = self._output_format_index[args[current_start + 1]]
                    output = FFmpegPipeline.Output((current_start, index - 1), "-f",
                                                    args[current_start + 1],
                                                    current_output_properties)
                    result.append(output)
                    self._output_format_map[(
                        args[current_start + 1], output_index)] = output
                    self._output_format_index[args[current_start + 1]] += 1
                    current_output_list = None
                    current_output_properties = None
                    current_start = None
                else:
                    current_output_list = current_output_properties["_ARGS_"]
                    current_output_list.append(args[index])
                    args_remaining -= 1
                    continue

            if (args[index] == '-f'):
                current_start = index
                current_output_properties = {}
                current_output_properties["_ARGS_"] = []
                args_remaining -= 2
                index = index + 1
                continue

            args_remaining -= 1

        if (current_output_properties is not None):
            output_index = self._output_format_index[args[current_start + 1]]
            output = self.Output((current_start, index), "-f",
                                 args[current_start + 1], current_output_properties)
            result.append(output)
            self._output_format_map[(
                args[current_start + 1], output_index)] = output
            self._output_format_index[args[current_start + 1]] += 1

        return result

    def _get_video_filters(self, args):
        result = OrderedDict()
        vf_index = args.index('-vf') if ('-vf' in args) else None
        if vf_index is None:
            return result
        filters = args[vf_index + 1].split(',')
        for _filter in filters:
            properties = self._get_filter_properties(_filter)
            filter_type = properties.pop('_TYPE_')
            index = self._video_filter_index[filter_type]
            video_filter = FFmpegPipeline.VideoFilter(
                filter_type, index, properties)
            result[(filter_type, index)] = video_filter
            self._video_filter_map[(filter_type, index)] = video_filter
            self._video_filter_index[filter_type] += 1

        return [FFmpegPipeline.VideoFilters((vf_index, vf_index + 1), '-vf', result)]

    def _get_inputs(self, args):
        result = []
        for i, arg in enumerate(args):
            if arg == '-i':
                result.append(FFmpegPipeline.Input(
                    (i, i + 1), arg, {'_ARGS_': [args[i + 1]]}))

        return result

    def _parse_ffmpeg_launch_string(self, launch_string):
        # TODO: Fully parse ffmpeg syntax

        self._ffmpeg_args = ['ffmpeg']
        self._ffmpeg_args.extend(shlex.split(launch_string))
        self._video_filters = self._get_video_filters(self._ffmpeg_args)
        self._outputs = self._get_outputs(self._ffmpeg_args)
        self._inputs = self._get_inputs(self._ffmpeg_args)

    def _generate_input(self, _input):
        _input.properties["_ARGS_"].insert(0, '-i')
        return _input.properties["_ARGS_"]

    def _join_video_filter_properties(self, filter_type, filter_params):
        parameters = ["%s=%s" % (x, y) for (x, y) in filter_params.items()]
        return "{filter_type}={params}".format(filter_type=filter_type, params=':'.join(parameters))

    def _generate_video_filter(self, video_filter):
        result = [video_filter.token]
        gva_filter_types = FFmpegPipeline.GVA_INFERENCE_FILTER_TYPES + \
            ["metaconvert"]
        filter_components = []
        for (name, _index), _filter in video_filter.filters.items():
            if (name in gva_filter_types):
                _filter.properties.pop("_ORIG_")

                if (name == "metaconvert"):

                    if "converter" not in _filter.properties:
                        _filter.properties["converter"] = "json"
                    if "method" not in _filter.properties:
                        _filter.properties["method"] = "all"
                    if "source" in _filter.properties:
                        _filter.properties["source"] = "\'{}\'".format(
                            _filter.properties["source"]).replace('_COLON_', r'\:')

                filter_components.append(
                    self._join_video_filter_properties(name, _filter.properties))
            else:
                filter_components.append(_filter.properties["_ORIG_"])
        result.append(','.join(filter_components))
        return result

    def _generate_output(self, _output):
        result = [_output.token, _output.format]

        args = _output.properties.pop("_ARGS_")

        args = [arg for arg in args if not arg.endswith("_ARG_")]

        kafka_hosts = (_output.properties.pop("_METAPUBLISH_KAFKA_HOST_")
                       if "_METAPUBLISH_KAFKA_HOST_" in _output.properties else None)
        kafka_topic = (_output.properties.pop("_METAPUBLISH_KAFKA_TOPIC_")
                       if "_METAPUBLISH_KAFKA_TOPIC_" in _output.properties else None)

        if (kafka_hosts) and (kafka_topic):
            args.extend(["kafka://{}/{}".format(host, kafka_topic)
                         for host in kafka_hosts.split(',')])

        for option, value in _output.properties.items():
            result.append("-{}".format(option)
                          if not option.startswith('-') else option)
            result.append(value)
        result.extend(args)
        return result

    def _generate_ffmpeg_launch_args(self):
        args_remaining = len(self._ffmpeg_args)
        indices = [args_remaining - (x + 1)
                   for x in range(len(self._ffmpeg_args))]
        result = []

        generators = [(_input, self._generate_input)
                      for _input in self._inputs]
        generators.extend([(_output, self._generate_output)
                           for _output in self._outputs])
        generators.extend([(_video_filter, self._generate_video_filter)
                           for _video_filter in self._video_filters])
        while(args_remaining):
            index = indices[args_remaining - 1]
            consumed = False

            for token, generate in generators:
                if (index == token.range[0]):
                    result.extend(generate(token))
                    args_remaining -= token.range[1] - token.range[0] + 1
                    consumed = True
                    generators.remove((token, generate))
                    break

            if (not consumed):
                result.append(self._ffmpeg_args[index])
                args_remaining -= 1

        self._ffmpeg_args = result
        self._unescape_args(self._ffmpeg_args)
        self._ffmpeg_args = [str(x) for x in self._ffmpeg_args]

    def _set_real_base(self, metaconvert):
        self._real_base = int(
            time.clock_gettime(time.CLOCK_REALTIME) *
            FFmpegPipeline.SECONDS_TO_NANOSECONDS)

        if ("tags" not in self.request):
            self.request["tags"] = {}

        self.request["tags"]["real_base"] = self._real_base

        properties = self._video_filter_map[metaconvert].properties
        properties["tags"] = "\'{}\'".format(
            json.dumps(self.request["tags"]).replace(':', r'\:'))

    def _set_recording_prefix(self, segment):
        self._recording_prefix = os.path.abspath(
            self.request['parameters']['recording_prefix'])
        self._temp_recording_dir = os.path.join(os.path.dirname(
            self._recording_prefix), "tmp_recording/{}".format(self.identifier))

        try:
            shutil.rmtree(self._temp_recording_dir)
        except OSError as exception:
            self._logger.warning(str(exception))

        try:
            os.makedirs(self._temp_recording_dir)
        except Exception as exception:
            self._logger.warning(str(exception))

        properties = self._output_format_map[segment].properties

        properties['_ARGS_'] = [os.path.join(
            self._temp_recording_dir, "temp_recording_%d.mp4")]

    def _initialize_segment_recording(self):
        segment_key = ("segment", 0)

        if (segment_key in self._output_format_map):
            metaconvert_key = ("metaconvert", 0)
            if (metaconvert_key in self._video_filter_map):

                self._set_real_base(metaconvert_key)

            if (('parameters' in self.request)
                    and ('recording_prefix' in self.request['parameters'])):

                self._set_recording_prefix(segment_key)

    def start(self):
        with(self._create_delete_lock):
            if (self.start_time is not None):
                return
            self._logger.debug("Starting Pipeline %s", self.identifier)
            self.request["models"] = self.models
            self._escape_source()
            self._ffmpeg_launch_string = string.Formatter().vformat(
                self.template, [], self.request)
            self._parse_ffmpeg_launch_string(self._ffmpeg_launch_string)
            self._set_properties()
            self._set_default_models()
            self._set_model_proc()
            self._initialize_segment_recording()
            self._generate_ffmpeg_launch_args()
            self._unescape_source()
            thread = Thread(target=self._spawn, args=[self._ffmpeg_args])
            self.start_time = time.time()
            thread.start()
