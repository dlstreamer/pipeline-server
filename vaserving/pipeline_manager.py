'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import os
import json
import traceback
from threading import Lock
from collections import deque
from collections import defaultdict
import jsonschema
from vaserving.common.utils import logging
from vaserving.pipeline import Pipeline
import vaserving.schema as schema


class PipelineManager:

    def __init__(self, model_manager, pipeline_dir, max_running_pipelines=-1,
                 ignore_init_errors=False):
        self.max_running_pipelines = max_running_pipelines
        self.model_manager = model_manager
        self.running_pipelines = 0
        self.pipeline_types = {}
        self.pipeline_instances = {}
        self.pipeline_state = {}
        self.pipeline_id = 0
        self.pipelines = {}
        self.pipeline_queue = deque()
        self.pipeline_dir = pipeline_dir
        self.logger = logging.get_logger('PipelineManager', is_static=True)
        self._create_lock = Lock()
        self._run_counter_lock = Lock()
        success = self._load_pipelines()
        if (not ignore_init_errors) and (not success):
            raise Exception("Error Initializing Pipelines")


    def _import_pipeline_types(self):
        pipeline_types = {}
        try:
            from vaserving.gstreamer_pipeline import GStreamerPipeline  # pylint: disable=import-error
            pipeline_types['GStreamer'] = GStreamerPipeline
        except Exception as error:
            pipeline_types['GStreamer'] = None
            self.logger.info(
                "GStreamer Pipelines Not Enabled: %s\n", error)
        try:
            from vaserving.ffmpeg_pipeline import FFmpegPipeline  # pylint: disable=import-error
            pipeline_types['FFmpeg'] = FFmpegPipeline
        except Exception as error:
            pipeline_types['FFmpeg'] = None
            self.logger.info(
                "FFmpeg Pipelines Not Enabled: %s\n", error)

        pipeline_types = {key: value for key,
                          value in pipeline_types.items() if value}

        return pipeline_types

    def _load_pipelines(self):
        # TODO: refactor
        # pylint: disable=R0912,R1702

        heading = "Loading Pipelines"
        banner = "="*len(heading)
        self.logger.info(banner)
        self.logger.info(heading)
        self.logger.info(banner)

        error_occurred = False
        self.pipeline_types = self._import_pipeline_types()
        self.logger.info("Loading Pipelines from Config Path {path}".format(
            path=self.pipeline_dir))
        if os.path.islink(self.pipeline_dir):
            self.logger.warning(
                "Pipelines directory is symbolic link")
        if os.path.ismount(self.pipeline_dir):
            self.logger.warning(
                "Pipelines directory is mount point")
        pipelines = defaultdict(dict)
        for root, subdirs, files in os.walk(self.pipeline_dir):
            if os.path.abspath(root) == os.path.abspath(self.pipeline_dir):
                for subdir in subdirs:
                    pipelines[subdir] = {}
            else:
                if len(files) == 0:
                    pipeline = os.path.basename(root)
                    pipelines[pipeline] = {}
                    for subdir in subdirs:
                        pipelines[pipeline][subdir] = {}
                else:
                    pipeline = os.path.basename(os.path.dirname(root))
                    version = os.path.basename(root)
                    for file in files:
                        path = os.path.join(root, file)
                        if path.endswith(".json"):
                            try:
                                with open(path, 'r') as jsonfile:
                                    config = json.load(jsonfile)
                                    if ('type' not in config) or ('description' not in config):
                                        del pipelines[pipeline][version]
                                        self.logger.error(
                                            "Pipeline %s"
                                            " is missing type or description", pipeline)
                                        error_occurred = True
                                        continue
                                    if "template" in config:
                                        if isinstance(config["template"], list):
                                            config["template"] = "".join(
                                                config["template"])
                                    if config['type'] in self.pipeline_types:
                                        pipelines[pipeline][version] = config
                                        config['name'] = pipeline
                                        config['version'] = version
                                        # validate_config will throw warning of
                                        # missing elements but continue execution
                                        self.pipeline_types[config['type']].validate_config(
                                            config)
                                        self.logger.info("Loading Pipeline: {} version: "
                                                         "{} type: {} from {}".format(
                                                             pipeline,
                                                             version,
                                                             config['type'],
                                                             path))
                                    else:
                                        del pipelines[pipeline][version]
                                        self.logger.error("Pipeline %s with type %s not supported",
                                                          pipeline, config['type'])
                                        error_occurred = True

                            except Exception as error:
                                if (pipeline in pipelines) and (version in pipelines[pipeline]):
                                    del pipelines[pipeline][version]
                                self.logger.error(
                                    "Failed to Load Pipeline from: {}".format(path))
                                self.logger.error(
                                    "Exception: {}".format(error))
                                self.logger.error(traceback.format_exc())
                                error_occurred = True

        # Remove pipelines with no valid versions
        pipelines = {pipeline: versions for pipeline,
                     versions in pipelines.items() if len(versions) > 0}
        self.pipelines = pipelines

        heading = "Completed Loading Pipelines"
        banner = "="*len(heading)
        self.logger.info(banner)
        self.logger.info(heading)
        self.logger.info(banner)
        return not error_occurred

    def get_loaded_pipelines(self):
        results = []
        for pipeline in self.pipelines:
            for version in self.pipelines[pipeline]:
                result = self.get_pipeline_parameters(
                    pipeline, version)
                if result:
                    results.append(result)
        return results

    def get_pipeline_parameters(self, name, version):
        if not self.pipeline_exists(name, version):
            return None
        params_obj = {
            "name": name,
            "version": version
        }
        if "type" in self.pipelines[name][version]:
            params_obj["type"] = self.pipelines[name][version]["type"]
        if "description" in self.pipelines[name][version]:
            params_obj["description"] = self.pipelines[name][version]["description"]
        if "parameters" in self.pipelines[name][version]:
            params_obj["parameters"] = self.pipelines[name][version]["parameters"]
        return params_obj

    def is_input_valid(self, request, pipeline_config, section):
        config = pipeline_config.get(section, {})
        try:
            if (section in request):
                input_validator = jsonschema.Draft4Validator(
                    schema=config, format_checker=jsonschema.draft4_format_checker)
                input_validator.validate(request.get(section, {}))
                self.logger.debug(
                    "{} Validation successful".format(section))
            return True
        except Exception as error:
            self.logger.debug(
                "Validation error in request section {}, error: {}".format(section, error))
            return False

    def set_section_defaults(self, request, config, request_section, config_section):
        section, config = Pipeline.get_section_and_config(
            request, config, request_section, config_section)
        for key in config:
            if (key not in section) and ("default" in config[key]):
                section[key] = config[key]["default"]

        if (len(section) != 0):
            result = request
            for key in request_section[0:-1]:
                result = result.setdefault(key, {})
            result[request_section[-1]] = section

    def set_defaults(self, request, config):

        if ("destination" not in config):
            config["destination"] = schema.destination
        if ("source" not in config):
            config["source"] = schema.source
        if ("tags" not in config):
            config["tags"] = schema.tags

        self.set_section_defaults(request, config, ["parameters"],
                                  ["parameters", "properties"])
        if "destination" in request:
            if "type" in request["destination"]:
                metadata = {"metadata": request["destination"]}
                request["destination"] = metadata

            for dest_type in request["destination"]:
                if "type" in request["destination"][dest_type]:
                    self.set_section_defaults(request, config, ["destination", dest_type],
                                              ["destination", dest_type,
                                               request["destination"][dest_type]["type"],
                                               "properties"])

        if ("source" in request) and ("type" in request["source"]):
            self.set_section_defaults(request, config, ["source"],
                                      ["source",
                                       request["source"]["type"],
                                       "properties"])

        self.set_section_defaults(request, config, ["tags"],
                                  ["tags", "properties"])

    def create_instance(self, name, version, request_original, options):
        self.logger.info(
            "Creating Instance of Pipeline {name}/{v}".format(name=name, v=version))
        if not self.pipeline_exists(name, version):
            return None, "Invalid Pipeline or Version"

        pipeline_type = self.pipelines[name][str(version)]['type']
        pipeline_config = self.pipelines[name][str(version)]

        request = request_original.copy()

        self.set_defaults(request, pipeline_config)

        if not self.is_input_valid(request, pipeline_config, "parameters"):
            return None, "Invalid Parameters"
        if not self.is_input_valid(request, pipeline_config, "destination"):
            return None, "Invalid Destination"
        if not self.is_input_valid(request, pipeline_config, "source"):
            return None, "Invalid Source"
        if not self.is_input_valid(request, pipeline_config, "tags"):
            return None, "Invalid Tags"

        with self._create_lock:
            self.pipeline_id += 1
            instance_id = self.pipeline_id
        self.pipeline_instances[instance_id] = self.pipeline_types[pipeline_type](
            instance_id,
            pipeline_config,
            self.model_manager,
            request,
            self._pipeline_finished,
            options)
        self.pipeline_queue.append(instance_id)
        self._start()
        return instance_id, None

    def _get_next_pipeline_identifier(self):
        if (self.max_running_pipelines > 0):
            if (self.running_pipelines >= self.max_running_pipelines):
                return None

        try:
            if (self.pipeline_queue):
                return self.pipeline_queue.popleft()
        except Exception:
            pass

        return None

    def _start(self):
        pipeline_identifier = self._get_next_pipeline_identifier()
        if (pipeline_identifier):
            pipeline_to_start = self.pipeline_instances[pipeline_identifier]
            with self._run_counter_lock:
                self.running_pipelines += 1
            pipeline_to_start.start()

    def _pipeline_finished(self):
        with self._run_counter_lock:
            self.running_pipelines -= 1
        self._start()

    def get_instance_parameters(self, name, version, instance_id):
        if self.instance_exists(name, version, instance_id):
            return self.pipeline_instances[instance_id].params()
        return None

    def get_all_instance_status(self):
        results = []
        for key in self.pipeline_instances:
            tmp = self.pipeline_instances[key].status()
            tmp['state'] = self.pipeline_instances[key].status()['state'].name
            results.append(tmp)
        return json.dumps(results)

    def get_instance_status(self, name, version, instance_id):
        if self.instance_exists(name, version, instance_id):
            return self.pipeline_instances[instance_id].status()
        return None

    def stop_instance(self, name, version, instance_id):
        if self.instance_exists(name, version, instance_id):
            try:
                self.pipeline_queue.remove(instance_id)
            except Exception:
                pass
            return self.pipeline_instances[instance_id].stop()
        return None

    def instance_exists(self, name, version, instance_id):
        if (self.pipeline_exists(name, version) and
                instance_id in self.pipeline_instances):
            return True
        self.logger.warning("Invalid Instance ID")
        return False

    def pipeline_exists(self, name, version):
        if name in self.pipelines and str(version) in self.pipelines[name]:
            return True
        self.logger.warning("Invalid pipeline or version")
        return False
