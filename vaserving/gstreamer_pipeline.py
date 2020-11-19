'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''
import copy
import json
import os
import string
import time
from threading import Lock, Thread

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstApp', '1.0')
# pylint: disable=wrong-import-position
from gi.repository import GLib, Gst, GstApp  # pylint: disable=unused-import
from gstgva.util import GVAJSONMeta
from vaserving.app_destination import AppDestination
from vaserving.app_source import AppSource
from vaserving.common.utils import logging
from vaserving.pipeline import Pipeline
# pylint: enable=wrong-import-position

logger = logging.get_logger('GSTPipeline', is_static=True)

class GStreamerPipeline(Pipeline):
    Gst.init(None)
    GVA_INFERENCE_ELEMENT_TYPES = ["GstGvaDetect",
                                   "GstGvaClassify",
                                   "GstGvaInference",
                                   "GvaAudioDetect"]

    _inference_element_cache = {}
    _mainloop = None
    _mainloop_thread = None

    @staticmethod
    def gobject_mainloop():
        gi.require_version('Gst', '1.0')
        from gi.repository import GLib
        GStreamerPipeline._mainloop = GLib.MainLoop.new(None, False)
        try:
            GStreamerPipeline._mainloop.run()
        except (KeyboardInterrupt, SystemExit):
            pass

    def __init__(self, identifier, config, model_manager, request, finished_callback):
        # TODO: refactor as abstract interface
        # pylint: disable=super-init-not-called
        self.config = config
        self.identifier = identifier
        self.pipeline = None
        self.template = config['template']
        self.models = model_manager.models
        self.model_manager = model_manager
        self.request = request
        self.state = Pipeline.State.QUEUED
        self.frame_count = 0
        self.start_time = None
        self.stop_time = None
        self.avg_fps = 0
        self._gst_launch_string = None
        self.latency_times = dict()
        self.sum_pipeline_latency = 0
        self.count_pipeline_latency = 0
        self._real_base = None
        self._stream_base = None
        self._year_base = None
        self._month_base = None
        self._day_base = None
        self._dir_name = None
        self._bus_connection_id = None
        self._create_delete_lock = Lock()
        self._finished_callback = finished_callback
        self._bus_messages = False
        self.appsrc_element = None
        self._app_source = None
        self.appsink_element = None
        self._app_destination = None
        if (not GStreamerPipeline._mainloop):
            GStreamerPipeline._mainloop_thread = Thread(
                target=GStreamerPipeline.gobject_mainloop)
            GStreamerPipeline._mainloop_thread.daemon = True
            GStreamerPipeline._mainloop_thread.start()

    @staticmethod
    def mainloop_quit():
        if (GStreamerPipeline._mainloop):
            GStreamerPipeline._mainloop.quit()
            GStreamerPipeline._mainloop = None
        if (GStreamerPipeline._mainloop_thread):
            GStreamerPipeline._mainloop_thread = None

    def _delete_pipeline(self, new_state):
        self.state = new_state
        self.stop_time = time.time()
        logger.debug("Setting Pipeline {id}"
                     " State to {next_state}".format(id=self.identifier,
                                                     next_state=new_state.name))
        if self.pipeline:
            bus = self.pipeline.get_bus()
            if self._bus_connection_id:
                bus.remove_signal_watch()
                bus.disconnect(self._bus_connection_id)
                self._bus_connection_id = None
            self.pipeline.set_state(Gst.State.NULL)
            del self.pipeline
            self.pipeline = None
        if self._app_source:
            self._app_source.finish()
        if self._app_destination:
            self._app_destination.finish()
        self._finished_callback()

    def _delete_pipeline_with_lock(self, new_state):
        with(self._create_delete_lock):
            self._delete_pipeline(new_state)

    def stop(self):
        with(self._create_delete_lock):
            if not self.state.stopped():
                if (self.pipeline):
                    structure = Gst.Structure.new_empty(self.state.name)
                    message = Gst.Message.new_custom(
                        Gst.MessageType.APPLICATION, None, structure)
                    self.pipeline.get_bus().post(message)
                else:
                    self.state = Pipeline.State.ABORTED
        return self.status()

    def params(self):
        # TODO: refactor
        # pylint: disable=R0801

        request = copy.deepcopy(self.request)
        if "models" in request:
            del request["models"]

        params_obj = {
            "id": self.identifier,
            "request": request,
            "type": self.config["type"],
            "launch_command": self._gst_launch_string
        }

        return params_obj

    def status(self):
        logger.debug("Called Status")
        if self.start_time is not None:
            if self.stop_time is not None:
                elapsed_time = max(0, self.stop_time - self.start_time)
            else:
                elapsed_time = max(0, time.time() - self.start_time)
        else:
            elapsed_time = None

        status_obj = {
            "id": self.identifier,
            "state": self.state,
            "avg_fps": self.avg_fps,
            "start_time": self.start_time,
            "elapsed_time": elapsed_time
        }
        if self.count_pipeline_latency != 0:
            status_obj["avg_pipeline_latency"] = self.sum_pipeline_latency / \
                self.count_pipeline_latency

        return status_obj

    def get_avg_fps(self):
        return self.avg_fps

    def _get_element_property(self, element, key):
        if isinstance(element, str):
            return (element, key, None)
        if isinstance(element, dict):
            return (element["name"], element["property"], element.get("format", None))
        return None

    def _set_bus_messages_flag(self):
        request_parameters, config_parameters = Pipeline.get_section_and_config(
            self.request, self.config, ["parameters"],
            ["parameters", "properties"])
        bus_msgs = "bus-messages"
        if bus_msgs in config_parameters and bus_msgs in request_parameters and \
           isinstance(request_parameters[bus_msgs], bool):
            self._bus_messages = request_parameters[bus_msgs]

    def _set_section_properties(self, request_section, config_section):
        # TODO: refactor
        # pylint: disable=R1702
        request, config = Pipeline.get_section_and_config(
            self.request, self.config, request_section, config_section)

        for key in config:
            if isinstance(config[key], dict) and "element" in config[key]:
                if key in request:
                    if isinstance(config[key]["element"], list):
                        element_properties = [self._get_element_property(
                            x, key) for x in config[key]["element"]]
                    else:
                        element_properties = [self._get_element_property(
                            config[key]["element"], key)]

                    for element_name, property_name, format_type in element_properties:
                        element = self.pipeline.get_by_name(element_name)
                        if element:
                            if (property_name in [x.name for x in element.list_properties()]):
                                if (format_type == "json"):
                                    element.set_property(
                                        property_name, json.dumps(request[key]))
                                else:
                                    element.set_property(
                                        property_name, request[key])
                                logger.debug("Setting element: {}, property: {}, value: {}".format(
                                    element_name,
                                    property_name,
                                    element.get_property(property_name)))
                            else:
                                logger.debug("Parameter {} given for element {}"
                                             " but no property found".format(
                                                 property_name, element_name))
                        else:
                            logger.debug(
                                "Parameter {} given for element {}"
                                " but no element found".format(property_name, element_name))

    def _cache_inference_elements(self):
        model_instance_id = "model-instance-id"
        gva_elements = [(element, element.__gtype__.name + '_'
                         + element.get_property(model_instance_id))
                        for element in self.pipeline.iterate_elements()
                        if (element.__gtype__.name in self.GVA_INFERENCE_ELEMENT_TYPES
                            and model_instance_id in [x.name for x in element.list_properties()]
                            and element.get_property(model_instance_id))]
        for element, key in gva_elements:
            if key not in GStreamerPipeline._inference_element_cache:
                GStreamerPipeline._inference_element_cache[key] = element

    def _set_default_models(self):
        gva_elements = [element for element in self.pipeline.iterate_elements() if (
            element.__gtype__.name in self.GVA_INFERENCE_ELEMENT_TYPES and
            "VA_DEVICE_DEFAULT" in element.get_property("model"))]
        for element in gva_elements:
            network = self.model_manager.get_default_network_for_device(
                element.get_property("device"), element.get_property("model"))
            logger.debug("Setting model to {} for element {}".format(
                network, element.get_name()))
            element.set_property("model", network)

    @staticmethod
    def _get_elements_by_type(pipeline, type_strings):
        return [element for element in pipeline.iterate_elements()
                if element.__gtype__.name in type_strings]


    @staticmethod
    def validate_config(config):
        template = config["template"]
        pipeline = Gst.parse_launch(template)
        appsink_elements = GStreamerPipeline._get_elements_by_type(pipeline, ["GstAppSink"])
        metaconvert = pipeline.get_by_name("metaconvert")
        metapublish = pipeline.get_by_name("destination")
        appsrc_elements = GStreamerPipeline._get_elements_by_type(pipeline, ["GstAppSrc"])
        if (len(appsrc_elements) > 1):
            logger.warning("Multiple appsrc elements found")
        if len(appsink_elements) != 1:
            logger.warning("Missing or multiple appsink elements")
        if metaconvert is None:
            logger.warning("Missing metaconvert element")
        if metapublish is None:
            logger.warning("Missing metapublish element")

    def calculate_times(self, sample):
        buffer = sample.get_buffer()
        segment = sample.get_segment()
        times = {}
        times['segment.time'] = segment.time
        times['stream_time'] = segment.to_stream_time(
            Gst.Format.TIME, buffer.pts)
        return times

    def format_location_callback(self,
                                 unused_element,
                                 unused_fragement_id,
                                 sample,
                                 unused_data=None):

        times = self.calculate_times(sample)

        if (self._real_base is None):
            clock = Gst.SystemClock(clock_type=Gst.ClockType.REALTIME)
            self._real_base = clock.get_time()
            self._stream_base = times["segment.time"]
            metaconvert = self.pipeline.get_by_name("metaconvert")

            if metaconvert:
                if ("tags" not in self.request):
                    self.request["tags"] = {}
                self.request["tags"]["real_base"] = self._real_base
                metaconvert.set_property(
                    "tags", json.dumps(self.request["tags"]))

        adjusted_time = self._real_base + \
            (times["stream_time"] - self._stream_base)
        self._year_base = time.strftime(
            "%Y", time.localtime(adjusted_time / 1000000000))
        self._month_base = time.strftime(
            "%m", time.localtime(adjusted_time / 1000000000))
        self._day_base = time.strftime(
            "%d", time.localtime(adjusted_time / 1000000000))
        template = "{prefix}/{yearbase}/{monthbase}/{daybase}"
        self._dir_name = template.format(prefix=self.request["parameters"]["recording_prefix"],
                                         yearbase=self._year_base,
                                         monthbase=self._month_base, daybase=self._day_base)

        try:
            os.makedirs(self._dir_name)
        except FileExistsError:
            logger.debug("Directory already exists")

        template = "{dirname}/{adjustedtime}_{time}.mp4"
        return template.format(dirname=self._dir_name,
                               adjustedtime=adjusted_time,
                               time=times["stream_time"] - self._stream_base)

    def _set_properties(self):
        self._set_section_properties(["parameters"],
                                     ["parameters", "properties"])
        self._set_section_properties(["destination"],
                                     ["destination", "properties"])
        if "destination" in self.request and "type" in self.request["destination"]:
            self._set_section_properties(["destination"],
                                         ["destination",
                                          self.request["destination"]["type"], "properties"])
        self._set_section_properties(["source"],
                                     ["source", "properties"])

        if "source" in self.request and "type" in self.request["source"]:
            self._set_section_properties(["source"],
                                         ["source", self.request["source"]["type"], "properties"])
        self._set_section_properties([], [])


    def _get_any_source(self):
        src = self.pipeline.get_by_name("source")
        if (not src):
            for src in self.pipeline.iterate_sources():
                break
        return src

    def start(self):

        self.request["models"] = self.models
        self._gst_launch_string = string.Formatter().vformat(
            self.template, [], self.request)

        with(self._create_delete_lock):
            if (self.start_time is not None):
                return

            logger.debug("Starting Pipeline {id}".format(id=self.identifier))
            logger.debug(self._gst_launch_string)

            try:
                self.pipeline = Gst.parse_launch(self._gst_launch_string)
                self._set_properties()
                self._set_bus_messages_flag()
                self._set_default_models()
                self._cache_inference_elements()

                src = self._get_any_source()

                sink = self.pipeline.get_by_name("appsink")
                if (not sink):
                    sink = self.pipeline.get_by_name("sink")
                if src and sink:
                    src_pad = src.get_static_pad("src")
                    if (src_pad):
                        src_pad.add_probe(Gst.PadProbeType.BUFFER,
                                          GStreamerPipeline.source_probe_callback, self)
                    else:
                        src.connect(
                            "pad-added", GStreamerPipeline.source_pad_added_callback, self)
                    sink_pad = sink.get_static_pad("sink")
                    sink_pad.add_probe(Gst.PadProbeType.BUFFER,
                                       GStreamerPipeline.appsink_probe_callback, self)

                bus = self.pipeline.get_bus()
                bus.add_signal_watch()
                self._bus_connection_id = bus.connect("message", self.bus_call)
                splitmuxsink = self.pipeline.get_by_name("splitmuxsink")
                self._real_base = None

                if (not splitmuxsink is None):
                    splitmuxsink.connect("format-location-full",
                                         self.format_location_callback,
                                         None)

                self._set_application_source()
                self._set_application_destination()
                self.pipeline.set_state(Gst.State.PLAYING)
                self.start_time = time.time()
            except Exception as error:
                logger.error("Error on Pipeline {id}: {err}".format(
                    id=self.identifier, err=error))
                # Context is already within _create_delete_lock
                self._delete_pipeline(Pipeline.State.ERROR)


    def _set_application_destination(self):
        self._app_destination = None
        self.appsink_element = None

        app_sink_elements = GStreamerPipeline._get_elements_by_type(self.pipeline, ["GstAppSink"])
        if (app_sink_elements):
            self.appsink_element = app_sink_elements[0]

        if "destination" in self.request and self.request["destination"]["type"] == "application":

            self._app_destination = AppDestination.create_app_destination(self.request, self)

            if ((not self._app_destination) or (not self.appsink_element)
                    or (not self.appsink_element.name == "destination")):
                raise Exception("Unsupported Application Destination: {}".format(
                    self.request["destination"]["class"]))

        if self.appsink_element is not None:
            self.appsink_element.set_property("emit-signals", True)
            self.appsink_element.set_property('sync', False)
            self.avg_fps = 0

            if (self._app_destination):
                self.appsink_element.connect("new-sample", self.on_sample_app_destination)
            else:
                self.appsink_element.connect("new-sample", self.on_sample)

    def on_need_data_app_source(self, src, _):
        try:
            self._app_source.start_frames()
        except Exception as error:
            logger.error("Error on Pipeline {id}: Error in App Source: {err}".format(
                id=self.identifier, err=error))
            src.post_message(Gst.Message.new_error(src, GLib.GError(),
                                                   "AppSource: {}".format(str(error))))

    def on_enough_data_app_source(self, src):
        try:
            self._app_source.pause_frames()
        except Exception as error:
            logger.error("Error on Pipeline {id}: Error in App Source: {err}".format(
                id=self.identifier, err=error))
            src.post_message(Gst.Message.new_error(src, GLib.GError(),
                                                   "AppSource: {}".format(str(error))))

    def _set_application_source(self):
        self._app_source = None
        self.appsrc_element = None

        if self.request["source"]["type"] == "application":

            appsrc_element = self.pipeline.get_by_name("source")

            if (appsrc_element) and (appsrc_element.__gtype__.name == "GstAppSrc"):
                self.appsrc_element = appsrc_element

            self._app_source = AppSource.create_app_source(self.request, self)

            if (not self._app_source) or (not self.appsrc_element):
                raise Exception("Unsupported Application Source: {}".format(
                    self.request["source"]["class"]))

            self.appsrc_element.set_property("format", Gst.Format.TIME)
            self.appsrc_element.set_property("block", True)
            self.appsrc_element.set_property("do-timestamp", True)
            self.appsrc_element.set_property("is-live", True)
            self.appsrc_element.set_property("emit-signals", True)
            self.appsrc_element.connect('need-data', self.on_need_data_app_source)
            self.appsrc_element.connect('enough-data', self.on_enough_data_app_source)

    @staticmethod
    def source_pad_added_callback(unused_element, pad, self):
        pad.add_probe(Gst.PadProbeType.BUFFER,
                      GStreamerPipeline.source_probe_callback, self)
        return Gst.FlowReturn.OK

    @staticmethod
    def source_probe_callback(unused_pad, info, self):
        buffer = info.get_buffer()
        pts = buffer.pts
        self.latency_times[pts] = time.time()
        return Gst.PadProbeReturn.OK

    @staticmethod
    def appsink_probe_callback(unused_pad, info, self):
        buffer = info.get_buffer()
        pts = buffer.pts
        source_time = self.latency_times.pop(pts, -1)
        if source_time != -1:
            self.sum_pipeline_latency += time.time() - source_time
            self.count_pipeline_latency += 1
        return Gst.PadProbeReturn.OK

    def on_sample_app_destination(self, sink):
        logger.debug("Received Sample from Pipeline {id}".format(
            id=self.identifier))
        sample = sink.emit("pull-sample")
        result = Gst.FlowReturn.OK
        try:
            self._app_destination.process_frame(sample)
        except Exception as error:
            logger.error("Error on Pipeline {id}: Error in App Destination: {err}".format(
                id=self.identifier, err=error))
            result = Gst.FlowReturn.ERROR
        self.frame_count += 1
        self.avg_fps = self.frame_count / (time.time() - self.start_time)
        return result

    def on_sample(self, sink):

        logger.debug("Received Sample from Pipeline {id}".format(
            id=self.identifier))
        sample = sink.emit("pull-sample")
        try:

            buf = sample.get_buffer()

            for meta in GVAJSONMeta.iterate(buf):
                json_object = json.loads(meta.get_message())
                logger.debug(json.dumps(json_object))

        except Exception as error:
            logger.error("Error on Pipeline {id}: {err}".format(
                id=self.identifier, err=error))

        self.frame_count += 1
        self.avg_fps = self.frame_count / (time.time() - self.start_time)
        return Gst.FlowReturn.OK

    def bus_call(self, unused_bus, message, unused_data=None):
        message_type = message.type
        if message_type == Gst.MessageType.APPLICATION:
            logger.info("Pipeline {id} Aborted".format(id=self.identifier))
            self._delete_pipeline_with_lock(Pipeline.State.ABORTED)
        if message_type == Gst.MessageType.EOS:
            logger.info("Pipeline {id} Ended".format(id=self.identifier))
            self._delete_pipeline_with_lock(Pipeline.State.COMPLETED)
        elif message_type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            logger.error(
                "Error on Pipeline {id}: {err}: {debug}".format(id=self.identifier,
                                                                err=err,
                                                                debug=debug))
            self._delete_pipeline_with_lock(Pipeline.State.ERROR)
        elif message_type == Gst.MessageType.STATE_CHANGED:
            old_state, new_state, unused_pending_state = message.parse_state_changed()
            if message.src == self.pipeline:
                if old_state == Gst.State.PAUSED and new_state == Gst.State.PLAYING:
                    if self.state is Pipeline.State.ABORTED:
                        self._delete_pipeline_with_lock(Pipeline.State.ABORTED)
                    if self.state is Pipeline.State.QUEUED:
                        logger.info(
                            "Setting Pipeline {id} State to RUNNING".format(id=self.identifier))
                        self.state = Pipeline.State.RUNNING
        else:
            if self._bus_messages:
                structure = Gst.Message.get_structure(message)
                if structure:
                    logger.info("Message header: {name} , Message: {message}".format(
                        name=Gst.Structure.get_name(structure),
                        message=Gst.Structure.to_string(structure)))
        return True
