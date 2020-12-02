'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''
import os
import time
from collections import defaultdict
from collections import namedtuple
from vaserving.arguments import parse_options
from vaserving.pipeline_manager import PipelineManager
from vaserving.model_manager import ModelManager
from vaserving.common.utils import logging
from vaserving.common import settings

#pylint: disable=C0103


class __VAServing:

    class ModelProxy:
        def __init__(self, vaserving, model, logger):
            self._model = model
            self._vaserving = vaserving
            self._logger = logger

        def name(self):
            return self._model["name"]

        def version(self):
            return self._model["version"]

        def networks(self):
            return self._model["networks"]

    class PipelineProxy:

        def __init__(self, vaserving, pipeline, logger, instance=None):
            self._pipeline = pipeline
            self._vaserving = vaserving
            self._instance = instance
            self._logger = logger
            self._status_named_tuple = None

        def name(self):
            return self._pipeline["name"]

        def version(self):
            return self._pipeline["version"]

        def stop(self):
            return self._vaserving.pipeline_manager.stop_instance(self.name(),
                                                                  self.version(),
                                                                  self._instance)

        def wait(self):
            status = self.status()
            while (status) and (not status.state.stopped()):
                time.sleep(1)
                status = self.status()
            return status

        def status(self):

            if (self._instance):
                result = self._vaserving.pipeline_manager.get_instance_status(self.name(),
                                                                              self.version(),
                                                                              self._instance)

                if 'avg_pipeline_latency' not in result:
                    result['avg_pipeline_latency'] = None

                if (not self._status_named_tuple):
                    self._status_named_tuple = namedtuple(
                        "PipelineStatus", sorted(result))

                return self._status_named_tuple(**result)

            return None

        def _set_or_update(self, request, section_name, section=None):
            if (section is None):
                section = {}
            if section_name in request:
                request[section_name].update(section)
            else:
                request[section_name] = section

        def start(self, request=None, source=None, destination=None, parameters=None, tags=None):
            if (self._instance):
                return self._instance

            if (not request):
                request = defaultdict(dict)

            self._set_or_update(request, "source", source)
            self._set_or_update(request, "destination", destination)
            self._set_or_update(request, "parameters", parameters)
            self._set_or_update(request, "tags", tags)
            self._instance, err = self._vaserving.pipeline_instance(
                self.name(), self.version(), request)

            if (not self._instance):
                self._logger.error("Error Starting Pipeline: {}".format(err))
            return self._instance

    def __init__(self):
        self._logger = logging.get_logger("VAServing", is_static=True)
        self.options = None
        self.model_manager = None
        self.pipeline_manager = None
        self._stopped = True

    def _log_options(self):
        heading = "Options for {}".format(os.path.basename(__file__))
        banner = "="*len(heading)
        self._logger.info(banner)
        self._logger.info(heading)
        self._logger.info(banner)
        for arg in vars(self.options):
            self._logger.info("{} == {}".format(arg, getattr(self.options, arg)))
        self._logger.info(banner)

    def start(self, _options=None):
        #pylint: disable=C0330
        if (self._stopped):
            self.options = parse_options(_options)
            settings.set_log_level(self.options.log_level)
            self._log_options()
            self.model_manager = ModelManager(
                os.path.abspath(
                    os.path.join(self.options.config_path,
                                 self.options.model_dir)),
                self.options.network_preference,
                self.options.ignore_init_errors)

            self.pipeline_manager = PipelineManager(
                self.model_manager,
                os.path.abspath(os.path.join(self.options.config_path,
                                             self.options.pipeline_dir)),
                ignore_init_errors=self.options.ignore_init_errors)
            self._stopped = False

    def __del__(self):
        try:
            self.stop()
        except Exception:
            pass

    def wait(self):
        for instance in self.pipeline_instances():
            status = instance.status()
            while (not status.state.stopped()):
                time.sleep(1)
                status = instance.status()

    def stop(self):

        for instance in self.pipeline_instances():
            if (not instance.status().state.stopped()):
                instance.stop()
                while (not instance.status().state.stopped()):
                    time.sleep(1)

        if (self.options) and (self.options.framework == "gstreamer") and (not self._stopped):
            try:
                from vaserving.gstreamer_pipeline import GStreamerPipeline
                GStreamerPipeline.mainloop_quit()
            except Exception as exception:
                self._logger.warning("Failed in quitting GStreamer main loop: %s",
                                     exception)

        self._stopped = True

    def pipeline_instances(self):
        if (self.pipeline_manager):
            return [self.PipelineProxy(self,
                                       pipeline.config,
                                       self._logger,
                                       instance_id)
                    for instance_id, pipeline in self.pipeline_manager.pipeline_instances.items()]

        return []

    def pipelines(self):
        return [self.PipelineProxy(self, pipeline, self._logger)
                for pipeline in self.pipeline_manager.get_loaded_pipelines()]

    def pipeline(self, name, version):
        if (isinstance(version, int)):
            version = str(version)
        pipeline = self.pipeline_manager.get_pipeline_parameters(name, version)
        if (pipeline):
            pipeline = self.PipelineProxy(self,
                                          pipeline,
                                          self._logger)
        return pipeline

    def models(self):
        return [self.ModelProxy(self, x, self._logger)
                for x in self.model_manager.get_loaded_models()]

    def pipeline_instance(self, name, version, request):
        if (not self._stopped):
            return self.pipeline_manager.create_instance(name, version, request)

        return None, "VA Serving Stopped"


VAServing = __VAServing()
