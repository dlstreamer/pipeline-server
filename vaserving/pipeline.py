'''
* Copyright (C) 2019 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''
from enum import Enum, auto


class Pipeline:
    class State(Enum):
        QUEUED = auto()
        RUNNING = auto()
        COMPLETED = auto()
        ERROR = auto()
        ABORTED = auto()

        def stopped(self):
            return not (self is Pipeline.State.QUEUED or self is Pipeline.State.RUNNING)

    def __init__(self, identifier, config, model_manager, request, finished_callback):
        pass

    def start(self):
        pass

    def status(self):
        pass

    def params(self):
        pass

    @staticmethod
    def validate_config(config):
        pass

    @staticmethod
    def get_section_and_config(request, config, request_section, config_section):
        for key in request_section:
            request = request.get(key, {})

        for key in config_section:
            config = config.get(key, {})

        return request, config
