'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''
#pylint: disable=R0801

extension_config = {
    "$schema":"https://json-schema.org/draft/2019-09/schema",
    "type":"object",
    "properties":{
        "pipeline":{
            "type":"object",
            "properties":{
                "name":{
                    "type":"string"
                },
                "version":{
                    "type":"string"
                },
                "parameters":{
                    "type":"object"
                }
            },
            "required":[
                "name",
                "version"
            ],
            "additionalProperties":False
        }
    },
    "additionalProperties":False
}
