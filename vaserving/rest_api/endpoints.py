'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''
from http import HTTPStatus
import connexion
from vaserving.common.utils import logging
from vaserving.vaserving import VAServing


logger = logging.get_logger('Default Controller', is_static=True)


bad_request_response = 'Invalid pipeline, version or instance'


def models_get():  # noqa: E501
    """models_get

    Return supported models # noqa: E501


    :rtype: List[ModelVersion]
    """
    try:
        logger.debug("GET on /models")
        return VAServing.model_manager.get_loaded_models()
    except Exception as error:
        logger.error('pipelines_name_version_get %s', error)
        return ('Unexpected error', HTTPStatus.INTERNAL_SERVER_ERROR)


def pipelines_get():  # noqa: E501
    """pipelines_get

    Return supported pipelines # noqa: E501


    :rtype: List[Pipeline]
    """
    try:
        logger.debug("GET on /pipelines")
        return VAServing.pipeline_manager.get_loaded_pipelines()
    except Exception as error:
        logger.error('pipelines_name_version_get %s', error)
        return ('Unexpected error', HTTPStatus.INTERNAL_SERVER_ERROR)


def pipelines_name_version_get(name, version):  # noqa: E501
    """pipelines_name_version_get

    Return pipeline description and parameters # noqa: E501

    :param name:
    :type name: str
    :param version:
    :type version: str

    :rtype: None
    """
    try:
        logger.debug(
            "GET on /pipelines/{name}/{version}".format(name=name, version=version))
        result = VAServing.pipeline_manager.get_pipeline_parameters(
            name, version)
        if result:
            return result
        return ('Invalid Pipeline or Version', HTTPStatus.BAD_REQUEST)
    except Exception as error:
        logger.error('pipelines_name_version_get %s', error)
        return ('Unexpected error', HTTPStatus.INTERNAL_SERVER_ERROR)


def pipelines_name_version_instance_id_delete(name, version, instance_id):  # noqa: E501
    """pipelines_name_version_instance_id_delete

    Stop and remove an instance of the customized pipeline # noqa: E501

    :param name:
    :type name: str
    :param version:
    :type version: str
    :param instance_id:
    :type instance_id: int

    :rtype: None
    """
    try:
        logger.debug("DELETE on /pipelines/{name}/{version}/{id}".format(
            name=name, version=str(version), id=instance_id))
        result = VAServing.pipeline_manager.stop_instance(
            name, version, instance_id)
        if result:
            result['state'] = result['state'].name
            return result
        return (bad_request_response, HTTPStatus.BAD_REQUEST)
    except Exception as error:
        logger.error('pipelines_name_version_instance_id_delete %s', error)
        return ('Unexpected error', HTTPStatus.INTERNAL_SERVER_ERROR)


def pipelines_name_version_instance_id_get(name, version, instance_id):  # noqa: E501
    """pipelines_name_version_instance_id_get

    Return instance summary # noqa: E501

    :param name:
    :type name: str
    :param version:
    :type version: str
    :param instance_id:
    :type instance_id: int

    :rtype: object
    """
    try:
        logger.debug("GET on /pipelines/{name}/{version}/{id}".format(
            name=name, version=version, id=instance_id))
        result = VAServing.pipeline_manager.get_instance_parameters(
            name, version, instance_id)
        if result:
            return result
        return (bad_request_response, HTTPStatus.BAD_REQUEST)
    except Exception as error:
        logger.error('pipelines_name_version_instance_id_get %s', error)
        return ('Unexpected error', HTTPStatus.INTERNAL_SERVER_ERROR)


def pipelines_name_version_instance_id_status_get(name, version, instance_id):  # noqa: E501
    """pipelines_name_version_instance_id_status_get

    Return instance status summary # noqa: E501

    :param name:
    :type name: str
    :param version:
    :type version: str
    :param instance_id:
    :type instance_id: int

    :rtype: object
    """
    try:
        logger.debug("GET on /pipelines/{name}/{version}/{id}/status".format(name=name,
                                                                             version=version,
                                                                             id=instance_id))
        result = VAServing.pipeline_manager.get_instance_status(
            name, version, instance_id)
        if result:
            result['state'] = result['state'].name
            return result
        return ('Invalid pipeline, version or instance', HTTPStatus.BAD_REQUEST)
    except Exception as error:
        logger.error('pipelines_name_version_instance_id_status_get %s', error)
        return ('Unexpected error', HTTPStatus.INTERNAL_SERVER_ERROR)


def pipelines_name_version_post(name, version):  # noqa: E501
    """pipelines_name_version_post

    Start new instance of pipeline.
    Specify the source and destination parameters as URIs # noqa: E501

    :param name:
    :type name: str
    :param version:
    :type version: str
    :param pipeline_request:
    :type pipeline_request: dict | bytes

    :rtype: None
    """

    logger.debug(
        "POST on /pipelines/{name}/{version}".format(name=name, version=str(version)))
    if connexion.request.is_json:
        try:
            pipeline_id, err = VAServing.pipeline_instance(
                name, version, connexion.request.get_json())
            if pipeline_id is not None:
                return pipeline_id
            return (err, HTTPStatus.BAD_REQUEST)
        except Exception as error:
            logger.error('Exception in pipelines_name_version_post %s', error)
            return ('Unexpected error', HTTPStatus.INTERNAL_SERVER_ERROR)

    return('Invalid Request, Body must be valid JSON', HTTPStatus.BAD_REQUEST)
