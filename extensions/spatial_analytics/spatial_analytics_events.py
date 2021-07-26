'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import json
from vaserving.common.utils import logging

logger = logging.get_logger('spatial_analytics_events', is_static=True)

def add_event(frame, event_type, attributes):
    event = {'event-type': event_type}
    for key, value in attributes.items():
        event[key] = value
    existing_events = _get_events(frame)
    existing_events.append(event)
    clear_events(frame)
    events_message = {"events": existing_events}
    frame.add_message(json.dumps(events_message))

def remove_event(frame, event):
    events = _get_events(frame)
    if events:
        events.remove(event)
        clear_events(frame)
        events_message = {"events": events}
        frame.add_message(json.dumps(events_message))

def events(frame):
    return _get_events(frame)

def _get_events(frame):
    events = []
    for message in frame.messages():
        try:
            message_obj = json.loads(message)
            if "events" in message_obj.keys():
                events = message_obj["events"]
                break
        except Exception as error:
            logger.error(error)
    return events

def clear_events(frame):
    messages = frame.messages()
    for message in messages:
        try:
            message_obj = json.loads(message)
            if "events" in message_obj.keys():
                frame.remove_message(message)
                return
        except Exception as error:
            logger.error(error)
