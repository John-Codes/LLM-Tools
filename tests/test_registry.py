import pytest

from llm_tools.models.errors import InvalidToolSpecError, ToolNotRegisteredError
from llm_tools.models.tool import ToolRecord
from llm_tools.registry.store import Registry


def test_registry_add_read_and_remove(tmp_path):
    registry = Registry(tmp_path / "LLM-tools.txt")
    registry.add(ToolRecord("weather-tool", "1.2.3"))

    assert registry.read() == [ToolRecord("weather-tool", "1.2.3")]
    assert registry.remove("weather-tool").package == "weather-tool"
    assert registry.read() == []


def test_registry_rejects_invalid_lines(tmp_path):
    path = tmp_path / "LLM-tools.txt"
    path.write_text("valid-tool==1.0\nnot a requirement\n")

    with pytest.raises(InvalidToolSpecError, match="line|entry"):
        Registry(path).read()


def test_missing_tool_is_explicit(tmp_path):
    registry = Registry(tmp_path / "LLM-tools.txt")

    with pytest.raises(ToolNotRegisteredError, match="missing"):
        registry.get("missing")


def test_duplicate_tool_is_rejected(tmp_path):
    path = tmp_path / "LLM-tools.txt"
    path.write_text("same-tool==1.0\nsame-tool==2.0\n")

    with pytest.raises(InvalidToolSpecError, match="Duplicate"):
        Registry(path).read()
