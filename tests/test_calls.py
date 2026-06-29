import os

import pytest

from llm_tools import LLMTool, ToolCommandError
from llm_tools.models.tool import ToolRecord


@pytest.fixture
def fake_tool(tmp_path, monkeypatch):
    command = tmp_path / "fake-tool"
    command.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        "action = sys.argv[1]\n"
        "payload = json.loads(sys.stdin.read()) if action == 'execute' else {}\n"
        "if payload.get('fail'):\n"
        " print('remote exploded', file=sys.stderr); raise SystemExit(7)\n"
        "print(json.dumps({'name':'fake-tool'} if action == 'describe' "
        "else {'echo':payload}))\n"
    )
    command.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.getenv('PATH', '')}")
    return command


def configured(tmp_path):
    tools = LLMTool(tmp_path / "LLM-tools.txt")
    tools.registry.add(ToolRecord("fake-tool", "1.0"))
    return tools


def test_describe_and_execute(tmp_path, fake_tool):
    tools = configured(tmp_path)

    assert tools.describe("fake-tool")["name"] == "fake-tool"
    result = tools.execute("fake-tool", {"text": "hello"})

    assert result.ok is True
    assert result.output == {"echo": {"text": "hello"}}


def test_execute_returns_all_failure_information(tmp_path, fake_tool):
    result = configured(tmp_path).execute("fake-tool", {"fail": True})

    assert result.ok is False
    assert result.exit_code == 7
    assert result.error_type == "nonzero_exit"
    assert "remote exploded" in result.stderr
    assert "remote exploded" in result.error_message


def test_describe_raises_diagnostic_error(tmp_path, fake_tool):
    fake_tool.unlink()
    with pytest.raises(ToolCommandError) as captured:
        configured(tmp_path).describe("fake-tool")

    assert captured.value.result.error_type == "command_not_found"

