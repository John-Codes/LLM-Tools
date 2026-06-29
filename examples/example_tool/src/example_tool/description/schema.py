SCHEMA = {
    "name": "example-tool",
    "version": "0.1.0",
    "description": "Converts supplied text to uppercase.",
    "input_schema": {
        "type": "object",
        "properties": {"text": {"type": "string"}},
        "required": ["text"],
        "additionalProperties": False,
    },
    "output_schema": {
        "type": "object",
        "properties": {"result": {"type": "string"}},
        "required": ["result"],
    },
}

