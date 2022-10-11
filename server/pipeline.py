'''
* Copyright (C) 2019-2020 Intel Corporation.
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

    def __init__(self, identifier, config, model_manager, request, finished_callback, options):
        pass

    def start(self):
        pass

    def status(self):
        pass

    def params(self):
        pass

    @staticmethod
    def validate_config(config, request):
        pass

    @staticmethod
    def get_config_section(config, config_section):
        for key in config_section:
            config = config.get(key, {})

        return config

    @staticmethod
    def get_section_and_config(request, config, request_section, config_section):
        for key in request_section:
            request = request.get(key, {})

        config = Pipeline.get_config_section(config, config_section)

        return request, config
