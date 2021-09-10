{
    "$schema": "https://json-schema.org/draft/2019-09/schema",
    "type": "array",
    "items": {
        "properties": {
            "event-type": {
                "description": "Event type, known by caller",
                "type": "string"
            },
            "related-objects": {
                "description": "Array of related detections, each entry refers to index of associated detected object",
                "type": "array",
                "items": {
                    "type": "integer"
                }
            },
        },
        "required": [
            "event-type"
        ],
        "additionalProperties": True
    }
}
