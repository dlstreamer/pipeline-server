'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''
#pylint: disable=R0801

tags = {
    "type": "object",
    "filter": {
        "name": "metaconvert",
        "type": "video",
        "property": "tags",
        "format": "json"
    },
    "element": {
        "name": "metaconvert",
        "property": "tags",
        "format": "json"
    }
}

source = {
    "application":{
        "type": "object",
        "properties": {
            "type": {
                "type":"string",
                "enum":["application"]
            },
            "class":{
                "type":"string"
            }
        },
        "required":["type", "class"]
    },
    "uri": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["uri"]
            },
            "uri": {
                "type": "string",
                "format": "uri",
                "filter": [{"name": "metaconvert", "property": "source", "type": "video"},
                           {"name": "i", "property": "_INPUT_ARG_", "type": "input"}],
                "element": [{"name": "source",
                             "property": "uri"},
                            {"name": "source",
                             "property": "location"},
                            {"name": "metaconvert", "property": "source"}]}
        },
        "required": ["type", "uri"]
    },
    "device": {
        "type": "object",
        "properties": {
            "type": {"type": "string", "enum": ["device"]},
            "path": {"type": "string",
                     "format": "path", "element": [{"name": "source", "property": "device"},
                                                   {"name": "metaconvert", "property": "source"}]}
        },
        "required": ["type", "path"]
    },
    "oneOf": [
        {
            "$ref": "#/uri"
        },
        {
            "$ref": "#/device"
        },
        {
            "$ref": "#/application"
        }
    ]
}

destination = {
    "application": {
        "type":"object",
        "properties": {
            "type": {
                "type":"string",
                "enum":["application"]
            },
            "class": {
                "type":"string"
            }
        },
        "required":["type", "class"]
    },
    "file": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["file"],
                "element": {
                    "name": "destination",
                    "property": "method"
                },
                "filter": {
                    "name": "metapublish",
                    "type": "output",
                    "property": "method",
                    "values": [0]
                }
            },
            "path": {
                "type": "string",
                "format": "path",
                "filter": {
                    "name": "metapublish",
                    "type": "output",
                    "property": "_METAPUBLISH_ARG_"
                },
                "element": {
                    "name": "destination",
                    "property": "file-path"
                }
            },
            "format": {
                "type": "string",
                "enum": [
                    "json-lines",
                    "json"
                ],
                "filter": {
                    "name": "metapublish",
                    "type": "output",
                    "property": "output_format",
                    "values": ["stream", "batch"]
                },
                "element": {
                    "name": "destination",
                    "property": "file-format"
                }
            }
        },
        "required": ["type", "path"]
    },
    "mqtt": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["mqtt"],
                "element": {"name": "destination", "property": "method"}
            },
            "host": {
                "type": "string",
                "element": {
                    "name": "destination",
                    "property": "address"
                }
            },
            "topic": {
                "type": "string",
                "element": "destination"
            },
            "clientId": {
                "type": "string",
                "element": "destination"
            },
            "timeout": {
                "type": "integer",
                "element": "destination"
            }
        },
        "required": [
            "host",
            "type",
            "topic"
        ]
    },
    "kafka": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["kafka"],
                "element": {"name": "destination", "property": "method"},
                "filter": {"name": "metapublish",
                           "property": "method",
                           "values": [1],
                           "type": "output"}
            },
            "host": {
                "type": "string",
                "description": "host:port to use as bootstrap server.",
                "filter": {
                    "name": "metapublish",
                    "type": "output",
                    "property": "_METAPUBLISH_KAFKA_HOST_"
                },
                "element": {
                    "name": "destination",
                    "property": "address"
                }
            },
            "topic": {
                "type": "string",
                "element": "destination",
                "filter": {
                    "name": "metapublish",
                    "type": "output",
                    "property": "_METAPUBLISH_KAFKA_TOPIC_"
                }
            }
        },
        "required": [
            "type",
            "host",
            "topic"
        ]
    },
    "oneOf": [
        {
            "$ref": "#/kafka"
        },
        {
            "$ref": "#/mqtt"
        },
        {
            "$ref": "#/file"
        },
        {
            "$ref": "#/application"
        }
    ]
}
