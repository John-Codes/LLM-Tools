from typing import Any
from xml.etree.ElementTree import Element, tostring


def to_xml(value: dict[str, Any]) -> str:
    root = Element("tool")
    _append(root, value)
    return tostring(root, encoding="unicode")


def _append(parent: Element, value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            child = Element(str(key))
            parent.append(child)
            _append(child, item)
    elif isinstance(value, list):
        for item in value:
            child = Element("item")
            parent.append(child)
            _append(child, item)
    elif isinstance(value, bool):
        parent.text = str(value).lower()
    elif value is not None:
        parent.text = str(value)

