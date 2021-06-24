'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import os
import json
from collections import namedtuple
from vaserving.common.utils import logging

Point = namedtuple('Point', ['x', 'y'])
BoundingBox = namedtuple('BoundingBox', ['left', 'top', 'width', 'height'])

'''
Line Crossing tracker for detecting if tracked objects cross defined lines.
Reference for line segment intersection calculation:
https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
'''

logger = logging.get_logger('line_events', is_static=True)

class Tracker: # pylint: disable=too-few-public-methods

    def __init__(self, lines, enable_watermark=False, log_level="INFO"):
        self._tracked = {}
        self._lines = []
        self._enable_watermark = enable_watermark
        logger.log_level = log_level
        if self._enable_watermark and os.getenv("ENABLE_RTSP") != "true":
            logger.warning("RTSP output is not enabled by environment variable.")

        for line in lines:
            try:
                self._lines.append(SpatialAnalysisCrossingLine(line))
            except Exception as error:
                logger.error(error)
                logger.error("Exception creating SpatialAnalysisCrossingLine: {}".format(line))

    def _create_events(self, frame):
        events = []
        for index, region in enumerate(frame.regions()):
            track_id = region.object_id()
            bounding_box = BoundingBox(*region.normalized_rect())
            if track_id in self._tracked:
                for line in self._lines:
                    orientation = line.intersect(self._tracked[track_id], bounding_box)
                    if orientation is not None:
                        if orientation == Segment.CLOCKWISE:
                            direction = "clockwise"
                            line.clockwise_total += 1
                        elif orientation == Segment.COUNTERCLOCKWISE:
                            direction = "counterclockwise"
                            line.counterclockwise_total += 1
                        else:
                            direction = "Parallel"
                        logger.debug('ID {} {} {}'.format(track_id, direction, line.name))
                        total = line.clockwise_total + line.counterclockwise_total
                        events.append(
                            {
                                'type': line.event_type,
                                'name': line.name,
                                'related_regions': [index],
                                'properties': {
                                    'direction': direction,
                                    'clockwiseTotal': str(line.clockwise_total),
                                    'counterclockwiseTotal': str(line.counterclockwise_total),
                                    'total': str(total)
                                }
                            }
                        )
            self._tracked[track_id] = bounding_box
        return events

    def _add_point(self, frame, point, label):
        region = frame.add_region(point.x, point.y, 0, 0, label=label, normalized=True)
        for tensor in region.tensors():
            tensor.set_name("line_crossing")

    def _add_watermark(self, frame):
        for index in range(0, len(self._lines)):
            self._add_point(frame, self._lines[index].line_segment.start_point, "{}_Start".format(index))
            self._add_point(frame, self._lines[index].line_segment.end_point, "{}_End".format(index))
            self._add_point(frame, self._lines[index].get_segment_midpoint(),
                            "{}_Count".format(self._lines[index].cross_count))

    def process_frame(self, frame):
        try:
            events = self._create_events(frame)
            if events:
                event_tensor = frame.add_tensor()
                event_tensor['events'] = json.dumps(events)
            if self._enable_watermark:
                self._add_watermark(frame)

        except Exception as error:
            logger.error(error)
        return True

class SpatialAnalysisCrossingLine:

    def __init__(self, line):
        self.event_type = 'lineCrossing'
        self._focus_point = 'bottom_center'
        self.cross_count = 0
        self.clockwise_total = 0
        self.counterclockwise_total = 0

        if 'name' not in line:
            raise ValueError('Crossing Line \'name\' not defined')
        self.name = line['name']

        if 'line' not in line:
            raise ValueError('Line segment not defined')
        if len(line['line']) != 2 or \
           len(line['line'][0]) != 2 or \
           len(line['line'][1]) != 2:
            raise ValueError('Line segment incorrectly defined')

        start_x = line['line'][0][0]
        start_y = line['line'][0][1]
        end_x = line['line'][1][0]
        end_y = line['line'][1][1]
        if start_x < 0 or start_x > 1 or start_y < 0 or start_y > 1:
            raise ValueError('Start point not normalized values [0,1]')
        if end_x < 0 or end_x > 1 or end_y < 0 or end_y > 1:
            raise ValueError('End point not normalized values [0,1]')
        self.line_segment = Segment(Point(start_x, start_y), Point(end_x, end_y))

        if 'focus' in line:
            self._focus_point = line['focus']

        if self._focus_point not in ['bottom_center', 'center']:
            raise ValueError('Got invalid focus point: {}'.format(self._focus_point))

    def intersect(self, bounding_box_old, bounding_box_new):
        initial_position = self._get_focus_point(bounding_box_old)
        current_position = self._get_focus_point(bounding_box_new)
        object_segment = Segment(initial_position, current_position)
        if (Segment.intersect(self.line_segment, object_segment)):
            self.cross_count += 1
            return self.line_segment.get_orientation(current_position)
        return None

    def _get_focus_point(self, bounding_box):
        if self._focus_point == 'bottom_center':
            return Point(x=bounding_box.left + (bounding_box.width/2.0),
                         y=bounding_box.top + bounding_box.height)
        if self._focus_point == 'center':
            return Point(x=bounding_box.left + (bounding_box.width/2.0),
                         y=bounding_box.top + (bounding_box.height/2.0))
        return None

    def get_segment_midpoint(self):
        return self.line_segment.get_midpoint()

class Segment:
    CLOCKWISE = 1
    COUNTERCLOCKWISE = 2
    COLLINEAR = 3

    def __init__(self, start_point, end_point):
        self.start_point = start_point
        self.end_point = end_point

    # Checks if point is on this segment. All points are assumed collinear.
    def point_on_segment(self, point):
        if ((point.x <= max(self.start_point.x, self.end_point.x)) and
                (point.x >= min(self.start_point.x, self.end_point.x)) and
                (point.y <= max(self.start_point.y, self.end_point.y)) and
                (point.y >= min(self.start_point.y, self.end_point.y))):
            return True
        return False

    def get_orientation(self, point):
        cross_product = (float(self.end_point.y - self.start_point.y) * (point.x - self.end_point.x)) - \
                        (float(point.y - self.end_point.y) * (self.end_point.x - self.start_point.x))
        if (cross_product > 0):
            return self.COUNTERCLOCKWISE
        if (cross_product < 0):
            return self.CLOCKWISE
        return self.COLLINEAR

    @classmethod
    def intersect(cls, segment_1, segment_2):

        orientation1 = segment_1.get_orientation(segment_2.start_point)
        orientation2 = segment_1.get_orientation(segment_2.end_point)
        orientation3 = segment_2.get_orientation(segment_1.start_point)
        orientation4 = segment_2.get_orientation(segment_1.end_point)
        # Basic Case
        # (segment_1.start_point, segment_1.end_point, segment_2.start_point) and
        # (segment_1.start_point, segment_1.end_point, segment_2.end_point) have diferent orientations and
        # (segment_2.start_point, segment_2.end_point, segment_1.start_point) and
        # (segment_2.start_point, segment_2.end_point, segment_1.end_point) have different orientations
        if ((orientation1 != orientation2) and (orientation3 != orientation4)):
            return True

        # Special Cases
        # Check if COLLINEAR points are on the same segment
        if ((orientation1 == cls.COLLINEAR) and segment_1.point_on_segment(segment_2.start_point)):
            return True
        if ((orientation2 == cls.COLLINEAR) and segment_1.point_on_segment(segment_2.end_point)):
            return True
        if ((orientation3 == cls.COLLINEAR) and segment_2.point_on_segment(segment_1.start_point)):
            return True
        if ((orientation4 == cls.COLLINEAR) and segment_2.point_on_segment(segment_1.end_point)):
            return True

        return False

    def get_midpoint(self):
        return Point((self.start_point.x + self.end_point.x) / 2.0,
                     (self.start_point.y + self.end_point.y) / 2.0)
