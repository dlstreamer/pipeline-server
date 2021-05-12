'''
* Copyright (C) 2021 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import json
import sys
import traceback
import gi

gi.require_version('Gst', '1.0')
# pylint: disable=wrong-import-position
from gi.repository import Gst
from gstgva import VideoFrame
from vaserving.common.utils import logging
# pylint: enable=wrong-import-position

def print_message(message):
    print("", flush=True)
    print(message, flush=True)

Gst.init(sys.argv)
logger = logging.get_logger('zone_events', is_static=True)

class ZoneEvents:
    DEFAULT_EVENT_TYPE = "zoneCrossing"
    DEFAULT_TRIGGER_ON_INTERSECT = True
    DEFAULT_DETECTION_CONFIDENCE_THRESHOLD = 0.0

    # Caller supplies one or more zones via request parameter
    def __init__(self, zones, enable_watermark=False, log_level="INFO"):
        self._logger = logger
        self._logger.log_level = log_level
        self._enable_watermark = enable_watermark
        self._assign_tensor_name = not self._enable_watermark
        self._zones = self._assign_defaults(zones)

    # Note that the pipeline already applies a pipeline-specific threshold value, but
    # this method serves as an example for handling optional zone-specific parameters.
    # If a field (e.g., 'threshold') exists in extension configuration, it overrides default value.
    def _assign_defaults(self, zones):
        for zone in zones:
            if not "threshold" in zone:
                zone["threshold"] = ZoneEvents.DEFAULT_DETECTION_CONFIDENCE_THRESHOLD
        return zones

    def process_frame(self, frame: VideoFrame) -> bool:
        try:
            if self._zones:
                self._process_regions(frame)
                if self._enable_watermark:
                    self._add_watermark_regions(frame)
        except Exception:
            print_message("Error processing frame: {}".format(traceback.format_exc()))
        return True

    def _add_watermark_regions(self, frame):
        for zone in self._zones:
            self._add_watermark_region(frame, zone, zone["name"], False)

    def _add_watermark_region(self, frame, zone, frame_label, draw_label):
        zone_poly = zone["polygon"]
        rv_x1, rv_y1 = None, None
        if self._enable_watermark:
            for zone_vertex in range(len(zone_poly)):
                draw_label_value = ""
                # We draw zone label on first vertex defined in configuration (zone index 0)
                if zone_vertex == 0:
                    draw_label_value = frame_label
                if rv_x1 is None and rv_x1 is None:
                    rv_x1, rv_y1 = zone_poly[0]
                else:
                    rv_x1, rv_y1 = zone_poly[zone_vertex % len(zone_poly)]
                dot_region = frame.add_region(rv_x1, rv_y1, 0.008, 0.008, label=draw_label_value, normalized=True)
                for tensor in dot_region.tensors():
                    # Rendering color is currently assigned using position of zone, within extension configuration
                    # list, for simplicity.
                    tensor['label_id'] = self._zones.index(zone)
                    if self._assign_tensor_name:
                        tensor.set_name(zone["name"])
                if draw_label:
                    break

    def _get_detection_poly(self, detected_object):
        detection_poly = [0, 0, 0, 0]
        x_min = detected_object.normalized_rect().x
        x_max = detected_object.normalized_rect().x + detected_object.normalized_rect().w
        y_min = detected_object.normalized_rect().y
        y_max = detected_object.normalized_rect().y + detected_object.normalized_rect().h
        detection_poly[0] = (x_min, y_min)
        detection_poly[1] = (x_min, y_max)
        detection_poly[2] = (x_max, y_max)
        detection_poly[3] = (x_max, y_min)
        return detection_poly

    def _process_regions(self, frame: VideoFrame):
        for detected_object in frame.regions():
            for zone in self._zones:
                if not detected_object.label().startswith(zone["name"]):
                    self._detect_zone_triggers(frame, detected_object, zone)

    def _detect_zone_triggers(self, frame, detected_object, zone):
        object_poly = self._get_detection_poly(detected_object)
        intersects_zone = False
        within_zone = False
        if (detected_object.confidence() >= zone["threshold"]):  # applying optional confidence filter
            within_zone = self.detection_within_zone(zone["polygon"], object_poly)
            if (not within_zone) and (ZoneEvents.DEFAULT_TRIGGER_ON_INTERSECT):
                intersects_zone = self.detection_intersects_zone(zone["polygon"], object_poly)
                if intersects_zone:
                    self._add_zone_event(frame, detected_object, zone, "intersects")
            if within_zone:
                self._add_zone_event(frame, detected_object, zone, "within")

    def _add_zone_event(self, frame, detected_object, zone, status):
        for tensor in detected_object.tensors():
            if tensor.is_detection():
                existing_events = []
                if 'events' in tensor.fields():
                    existing_events = json.loads(tensor['events'])
                zone_event = {}
                zone_event['type'] = ZoneEvents.DEFAULT_EVENT_TYPE
                zone_event['name'] = zone['name']
                zone_event['properties'] = {
                    "status": status
                }
                existing_events.append(zone_event)
                # We assign tensors with novel key "events" for aggregation in media_graph_extension.py
                tensor['events'] = json.dumps(existing_events)
        if self._enable_watermark:
            event_label = "{}-{}".format(zone["name"], status)
            self._add_watermark_region(frame, zone, event_label, True)

    def detection_intersects_zone(self, zone_poly, object_poly):
        intersects = not ((zone_poly[0][0] >= object_poly[2][0]) or (zone_poly[2][0] <= object_poly[0][0]) or \
                    (zone_poly[2][1] <= object_poly[3][1]) or (zone_poly[3][1] >= object_poly[2][1]))
        return intersects

    def detection_within_zone(self, zone_poly, object_poly):
        inside = (self.point_within_zone(object_poly[0], zone_poly) and \
            self.point_within_zone(object_poly[1], zone_poly) and \
            self.point_within_zone(object_poly[2], zone_poly) and \
            self.point_within_zone(object_poly[3], zone_poly))
        return inside

    def point_within_zone(self, vertex, zone_poly):
        within = False
        vert_x, vert_y = vertex
        rv_x1, rv_x2 = None, None
        for zone_vertex in range(len(zone_poly)):
            if rv_x1 is None and rv_x2 is None:
                rv_x1, rv_y1 = zone_poly[0]
            rv_x2, rv_y2 = zone_poly[zone_vertex % len(zone_poly)]
            if min(rv_y1, rv_y2) < vert_y <= max(rv_y1, rv_y2) and vert_x <= max(rv_x1, rv_x2):
                if rv_y1 != rv_y2:
                    intersection = (vert_y-rv_y1)*(rv_x2-rv_x1)/(rv_y2-rv_y1)+rv_x1
                if rv_x1 != rv_x2 or vert_x <= intersection:
                    within = not within
            rv_x1, rv_y1 = rv_x2, rv_y2
        return within
