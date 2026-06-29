import json
from typing import Any
from xml.etree.ElementTree import Element, tostring


def serialize(payload: Any, format: str) -> str:
    if format == "json":
        return json.dumps(payload)
    if format == "xml":
        if isinstance(payload, str):
            return payload
        root = Element("payload")
        _append(root, payload)
        return tostring(root, encoding="unicode")
    raise ValueError(f"Unsupported format: {format}")


def parse_output(value: str, format: str) -> Any:
    if format == "json":
        return json.loads(value)
    return value


def _append(parent: Element, value: Any) -> None:
    if isinstance(value, dict):
        for key, child_value in value.items():
            child = Element(str(key))
            parent.append(child)
            _append(child, child_value)
    elif isinstance(value, list):
        for child_value in value:
            child = Element("item")
            parent.append(child)
            _append(child, child_value)
    elif value is not None:
        parent.text = str(value)
