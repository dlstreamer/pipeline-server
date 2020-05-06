'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''
import string
import json
import time
import os
import copy
from threading import Lock
from threading import Thread
import gi

from gstgva.util import GVAJSONMeta
from vaserving.pipeline import Pipeline
from vaserving.common.utils import logging


# pylint: disable=wrong-import-order, wrong-import-position
from gi.repository import Gst
gi.require_version('Gst', '1.0')
# pylint: enable=wrong-import-order, wrong-import-position


logger = logging.get_logger('GSTPipeline', is_static=True)


class GStreamerPipeline(Pipeline):
    Gst.init(None)
    GVA_INFERENCE_ELEMENT_TYPES = ["GstGvaDetect",
                                   "GstGvaClassify",
                                   "GstGvaInference"]

    _inference_element_cache = {}
    _mainloop = None
    _mainloop_thread = None

    @staticmethod
    def gobject_mainloop():
        gi.require_version('Gst', '1.0')
        from gi.repository import GLib
        GStreamerPipeline._mainloop = GLib.MainLoop()
        try:
            GStreamerPipeline._mainloop.run()
        except KeyboardInterrupt:
            pass
        print("exiting")

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
        if (not GStreamerPipeline._mainloop):
            GStreamerPipeline._mainloop_thread = Thread(
                target=GStreamerPipeline.gobject_mainloop)
            GStreamerPipeline._mainloop_thread.start()

    @staticmethod
    def mainloop_quit():
        if (GStreamerPipeline._mainloop):
            GStreamerPipeline._mainloop.quit()
            GStreamerPipeline._mainloop = None
        if (GStreamerPipeline._mainloop_thread):
            GStreamerPipeline._mainloop_thread = None

    def _shutdown_and_delete_pipeline(self, new_state):
        with(self._create_delete_lock):
            self.state = new_state
            self.stop_time = time.time()
            logger.debug("Setting Pipeline {id}"
                         " State to {next_state}".format(id=self.identifier,
                                                         next_state=new_state.name))
            bus = self.pipeline.get_bus()
            bus.remove_signal_watch()
            bus.disconnect(self._bus_connection_id)
            self.pipeline.set_state(Gst.State.NULL)
            del self.pipeline
            self.pipeline = None
        self._finished_callback()

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
        gva_elements = [(element, element.__gtype__.name + '_'
                         + element.get_property('model-instance-id'))
                        for element in self.pipeline.iterate_elements()
                        if (element.__gtype__.name in self.GVA_INFERENCE_ELEMENT_TYPES
                            and element.get_property("model-instance-id"))]
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
    def validate_config(config):
        template = config["template"]
        pipeline = Gst.parse_launch(template)
        appsink = pipeline.get_by_name("appsink")
        metaconvert = pipeline.get_by_name("metaconvert")
        metapublish = pipeline.get_by_name("destination")
        if appsink is None:
            logger.warning("Missing appsink element")
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

    def start(self):

        self.request["models"] = self.models
        self._gst_launch_string = string.Formatter().vformat(
            self.template, [], self.request)

        with(self._create_delete_lock):
            if (self.start_time is not None):
                return

            logger.debug("Starting Pipeline {id}".format(id=self.identifier))
            logger.debug(self._gst_launch_string)

            self.pipeline = Gst.parse_launch(self._gst_launch_string)
            self._set_properties()
            self._set_default_models()
            self._cache_inference_elements()
            sink = self.pipeline.get_by_name("appsink")

            if sink is not None:
                sink.set_property("emit-signals", True)
                sink.set_property('sync', False)
                sink.connect("new-sample", GStreamerPipeline.on_sample, self)
                self.avg_fps = 0

            src = self.pipeline.get_by_name("source")

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

            self.pipeline.set_state(Gst.State.PLAYING)
            self.start_time = time.time()

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

    @staticmethod
    def on_sample(sink, self):

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
            self._shutdown_and_delete_pipeline(Pipeline.State.ABORTED)
        if message_type == Gst.MessageType.EOS:
            logger.info("Pipeline {id} Ended".format(id=self.identifier))
            self._shutdown_and_delete_pipeline(Pipeline.State.COMPLETED)
        elif message_type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            logger.error(
                "Error on Pipeline {id}: {err}: {debug}".format(id=self.identifier,
                                                                err=err,
                                                                debug=debug))
            self._shutdown_and_delete_pipeline(Pipeline.State.ERROR)
        elif message_type == Gst.MessageType.STATE_CHANGED:
            old_state, new_state, unused_pending_state = message.parse_state_changed()
            if message.src == self.pipeline:
                if old_state == Gst.State.PAUSED and new_state == Gst.State.PLAYING:
                    if self.state is Pipeline.State.ABORTED:
                        self._shutdown_and_delete_pipeline(Pipeline)
                    if self.state is Pipeline.State.QUEUED:
                        logger.info(
                            "Setting Pipeline {id} State to RUNNING".format(id=self.identifier))
                        self.state = Pipeline.State.RUNNING
        else:
            pass
        return True
