'''
* Copyright (C) 2019 Intel Corporation.
* 
* SPDX-License-Identifier: BSD-3-Clause
'''

import os
import json
import common.settings  # pylint: disable=import-error
from common.utils import logging  # pylint: disable=import-error

logger = logging.get_logger('ModelManager', is_static=True)

class ModelManager:
    models = None
 
    @staticmethod
    def load_config(model_dir):
        logger.info("Loading Models from Config Path {path}".format(path=os.path.abspath(model_dir)))
        if os.path.islink(model_dir):
            logger.warning("Models directory is symbolic link")
        if os.path.ismount(model_dir):
            logger.warning("Models directory is mount point")
        models = {}
        for path in os.listdir(model_dir):
            try:
                full_path = os.path.join(model_dir, path)
                if os.path.isdir(full_path):
                    model = path
                    for version_dir in os.listdir(full_path):
                        version_path = os.path.join(full_path, version_dir)
                        if os.path.isdir(version_path):
                            version = int(version_dir)
                            config_path = os.path.join(version_path, "model.json")
                            with open(config_path, 'r') as jsonfile:
                                config = json.load(jsonfile)
                                if 'network' in config:
                                    config['network'] = os.path.abspath(os.path.join(version_path, config['network']))
                                if 'weights' in config:
                                    config['weights'] = os.path.abspath(os.path.join(version_path, config['weights']))
                                if 'proc' in config:
                                    config['proc'] = os.path.abspath(os.path.join(version_path, config['proc']))
                                if 'gallery' in config:
                                    config['gallery'] = os.path.abspath(os.path.join(version_path, config['gallery']))
                                if 'labels' in config:
                                    config['labels'] = os.path.abspath(os.path.join(version_path, config['labels']))
                                if 'features' in config:
                                    config['features'] = os.path.abspath(os.path.join(version_path, config['features']))
                                if 'outputs' in config:
                                    for key in config['outputs']:
                                        if 'labels' in config['outputs'][key]:
                                            config['outputs'][key]['labels'] = os.path.abspath(
                                                os.path.join(version_path, config['outputs'][key]['labels']))
            except Exception as error:
                logger.error("Error in Model Loading: {err}".format(err=error))
                model = None
            if model:
                models[model] = {}
                models[model][version] = config
        ModelManager.models = models
        logger.info("Completed Loading Models")

    @staticmethod
    def get_model_parameters(name, version):
        if name not in ModelManager.models or version not in ModelManager.models[name] :
            return None
        params_obj = {
            "name": name,
            "version": version
        }
        if "type" in ModelManager.models[name][version]:
            params_obj["type"] = ModelManager.models[name][version]["type"]

        if "description" in ModelManager.models[name][version]:
            params_obj["description"] = ModelManager.models[name][version]["description"]
        return params_obj

    @staticmethod
    def get_loaded_models():
        results = []
        if ModelManager.models is not None:
            for model in ModelManager.models:
                for version in ModelManager.models[model].keys():
                    result = ModelManager.get_model_parameters(model, version)
                    if result :
                        results.append(result)
        return results

