'''
* Copyright (C) 2022 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

model_index_schema = {
                    "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "properties": {
                                "labels": {
                                        "type": ["string", "null"]
                                },
                                "model-proc": {
                                        "type": ["string", "null"]
                                }
                            }
                        }
                    }
