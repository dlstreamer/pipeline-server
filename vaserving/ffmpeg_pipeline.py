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
from threading import Thread
import shutil
import re
from collections import OrderedDict
import json
from vaserving.pipeline import Pipeline
from vaserving.common.utils import logging
from datetime import datetime, timedelta

if shutil.which('ffmpeg') is None:
    raise Exception("ffmpeg not installed")


class FFmpegPipeline(Pipeline):

    GVA_INFERENCE_FILTER_TYPES = ["detect",
                                  "classify"]

    def __init__(self, identifier, config, model_manager, request, finished_callback):
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
        self._fps_regular_expression = re.compile(
            r"\s*frame=\s*(?P<frame_count>\d+)\s*fps=\s*(?P<fps>\d+\.?\d*).*time=(?P<duration>\d+:\d+:\d+\.\d+).*speed=\s*(?P<speed>\d+\.\d+)x")

    def stop(self):
        self.state = Pipeline.State.ABORTED
        return self.status()

    def params(self):
        # TODO: refactor common code
        request = copy.deepcopy(self.request)
        if "models" in request:
            del request["models"]

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
    def validate_config(config):
        pass

    def get_fps(self, next_line):
        matched = self._fps_regular_expression.match(next_line)
        if (matched):
            fps = float(matched.group('fps'))
            if (fps > 0):
                return fps
            speed = float(matched.group("speed"))
            frame_count = int(matched.group("frame_count"))
            time_value = datetime.strptime(
                matched.group("duration"), "%H:%M:%S.%f")
            duration = timedelta(
                hours=time_value.hour,
                minutes=time_value.minute,
                seconds=time_value.second,
                microseconds=time_value.microsecond)
            calculated_fps = (frame_count / (duration.total_seconds())) * speed
            return calculated_fps
        return None

    def _spawn(self, args):
        self.start_time = time.time()
        self._process = subprocess.Popen(args,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         bufsize=1,
                                         universal_newlines=True)
        self.state = Pipeline.State.RUNNING
        self._process.poll()
        while self._process.returncode is None and not self.state is Pipeline.State.ABORTED:
            next_line = self._process.stderr.readline()
            self._logger.debug(next_line)
            fps = self.get_fps(next_line)
            if (fps):
                self.fps = fps
            self._process.poll()
        self.stop_time = time.time()
        if self.state is Pipeline.State.ABORTED:
            self._process.kill()
        else:
            if self._process.returncode == 0:
                self.state = Pipeline.State.COMPLETED
            else:
                self.state = Pipeline.State.ERROR
        self._finished_callback()
        self._process = None

    def _get_filter_params(self, _filter):
        result = {}
        params = re.split("=|:", _filter)
        result['_TYPE_'] = params[0]
        result['_ORIG_'] = _filter
        for x in range(1, len(params[0:]), 2):
            result[params[x]] = params[x + 1]
        return result

    def _get_finalized_filters(self, filters):
        gva_filter_types = ["metapublish", "metaconvert"] + \
            FFmpegPipeline.GVA_INFERENCE_FILTER_TYPES
        finalized_filters = []
        for _filter, params in filters.items():
            if _filter in gva_filter_types:
                params.pop("_ORIG_")
                finalized_filters.append(
                    self._join_filter_params(_filter, params))
            else:
                finalized_filters.append(params["_ORIG_"])

        return ','.join(finalized_filters)

    def _join_filter_params(self, filter_type, filter_params):
        parameters = ["%s=%s" % (x, y) for (x, y) in filter_params.items()]
        return "{filter_type}={params}".format(filter_type=filter_type, params=':'.join(parameters))

    def _get_filters(self, args):
        result = OrderedDict()
        vf_index = args.index('-vf') if ('-vf' in args) else None
        if vf_index is None:
            return result
        filters = args[vf_index + 1].split(',')
        for _filter in filters:
            params = self._get_filter_params(_filter)
            filter_type = params.pop('_TYPE_')
            result[filter_type] = params
        return result

    def _set_default_models(self, filters):
        for _filter, params in filters.items():
            if ((_filter in FFmpegPipeline.GVA_INFERENCE_FILTER_TYPES)
                    and ("VA_DEVICE_DEFAULT" in params['model'])):

                if "device" not in params:
                    params["device"] = "CPU"

                params["model"] = self.model_manager.get_default_network_for_device(
                    params["device"], params["model"])

    def _replace_filters(self, args, finalized_filters):
        vf_index = args.index('-vf') if ('-vf' in args) else None
        if (vf_index):
            args[vf_index + 1] = finalized_filters

    def _unescape_args(self, args):
        for i, arg in enumerate(args):
            args[i] = arg.replace('_COLON_', ':')

    def _escape_source(self):
        if "source" in self.request and "uri" in self.request["source"]:
            self.request["source"]["uri"] = self.request["source"]["uri"].replace(
                ':', '_COLON_')

    def _unescape_source(self):
        if "source" in self.request and "uri" in self.request["source"]:
            self.request["source"]["uri"] = self.request["source"]["uri"].replace(
                '_COLON_', ':')

    def _set_metaconvert_properties(self, request, filters):
        if ('metaconvert') in filters:
            properties = filters["metaconvert"]

            if "converter" not in properties:
                properties["converter"] = "json"
            if "method" not in properties:
                properties["method"] = "all"
            if "source" not in properties:
                if "source" in request and "uri" in request["source"]:
                    properties["source"] = "\'{}\'".format(
                        request["source"]["uri"].replace('_COLON_', r'\:'))
            if "tags" not in properties:
                if "tags" in request and request["tags"]:
                    properties["tags"] = "\'{}\'".format(json.dumps(
                        request['tags']).replace(':', r'\:'))

    def _get_metapublish_properties(self, args):
        metapublish_index = None
        for output, fmt in zip(args, args[1:]):
            if output == '-f' and fmt == 'metapublish':
                metapublish_index = args.index('metapublish')
                break

        properties = dict(
            zip(args[metapublish_index + 1:], args[metapublish_index + 2:]))

        properties["_INDEX_"] = metapublish_index

        return {'metapublish': properties}

    def _replace_metapublish(self, args, metapublish_args):

        index = metapublish_args['metapublish'].pop("_INDEX_")
        values = []
        for key, value in metapublish_args["metapublish"].items():
            if (key == "_OUTPUT_"):
                values.extend(value)
            else:
                values.extend([key, str(value)])

        args[index + 1:] = values

    def _set_metapublish_properties(self, _properties):
        if "metapublish" in _properties:
            properties = _properties["metapublish"]

            if '-output_format' not in properties:
                properties["-output_format"] = "stream"

            if '-method' not in properties:
                if 'destination' in self.request:
                    if self.request['destination']['type'] == "kafka":
                        properties['-method'] = 1
                        properties["_OUTPUT_"] = []
                        for item in self.request['destination']['host'].split(','):
                            properties["_OUTPUT_"].append(
                                "kafka://" + item + "/" + self.request["destination"]["topic"])
                    elif self.request['destination']['type'] == "file":
                        properties['-method'] = 0
                        properties["_OUTPUT_"] = [
                            self.request['destination']['path']]
                else:
                    properties["-method"] = 0
                    self._logger.warning("No destination in pipeline request {id}."
                                         " Results will be discarded.".format(id=self.identifier))
                    properties["_OUTPUT_"] = ["/dev/null"]

    def start(self):
        self._logger.debug("Starting Pipeline %s", self.identifier)
        self.request["models"] = self.models
        self._escape_source()
        self._ffmpeg_launch_string = string.Formatter().vformat(
            self.template, [], self.request)
        args = ['ffmpeg']
        args.extend(shlex.split(self._ffmpeg_launch_string))
        filters = self._get_filters(args)
        self._set_metaconvert_properties(self.request, filters)
        metapublish_properties = self._get_metapublish_properties(args)
        self._set_metapublish_properties(metapublish_properties)
        self._set_default_models(filters)
        final_filters = self._get_finalized_filters(filters)
        self._replace_filters(args, final_filters)
        self._replace_metapublish(args, metapublish_properties)
        self._unescape_args(args)
        self._unescape_source()
        self._logger.debug(args)
        thread = Thread(target=self._spawn, args=[args])
        thread.start()
