# LLM Tools

`llm-tools` is a small Python registry for discovering, describing, executing,
and removing tools used by an LLM. Each tool is an independent Python package
with a standard CLI. The CLI can call FastAPI, another API, or local code.

The stable contract is:

```bash
my-tool describe --format json
printf '{"input":"value"}' | my-tool execute --format json
```

## 1. Install the registry

Python 3.11 or newer is required.

```bash
git clone <repository-url> LLM-Tools
cd LLM-Tools
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
llm-tools --help
```

Commands use `./LLM-tools.txt` by default. Set `LLM_TOOLS_FILE` or pass
`--registry PATH` to use another registry.

## 2. Run the working example

Terminal one starts the example FastAPI service:

```bash
source .venv/bin/activate
python -m pip install -e ./examples/example_tool
uvicorn example_tool.api.main:app --port 8000
```

Terminal two installs and registers the tool through the manager:

```bash
source .venv/bin/activate
llm-tools install example-tool --source ./examples/example_tool
llm-tools list
llm-tools describe example-tool --format json
llm-tools execute example-tool --payload '{"text":"hello LLM"}'
```

The final command returns:

```json
{
  "ok": true,
  "output": {"result": "HELLO LLM"},
  "stdout": "{\"result\":\"HELLO LLM\"}\n",
  "stderr": "",
  "exit_code": 0,
  "error_type": null,
  "error_message": null,
  "timed_out": false
}
```

## 3. Use it from Python

```python
from llm_tools import LLMTool

tools = LLMTool("LLM-tools.txt")
print([tool.to_dict() for tool in tools.get_tools()])
schema = tools.describe("example-tool")
result = tools.execute("example-tool", {"text": "hello"})

if not result.ok:
    print(result.to_dict())
else:
    print(result.output)
```

`execute()` does not hide tool failures. A failed call returns `ok=False` plus
stdout, stderr, exit code, timeout state, error type, and error message. Missing
registrations and invalid configuration raise explicit exceptions. Description,
installation, and removal failures raise `ToolCommandError`; its `.result`
contains the same diagnostics.

## 4. Build a compatible tool

Create a normal Python package. Its distribution name and CLI command must be
the same. For `weather-tool`, add this to its `pyproject.toml`:

```toml
[project]
name = "weather-tool"
version = "0.1.0"

[project.scripts]
weather-tool = "weather_tool.cli:main"
```

Implement these commands:

```bash
weather-tool describe --format json
weather-tool describe --format xml
printf '{"city":"Chicago"}' | weather-tool execute --format json
```

Rules for `describe`:

1. Write only the description document to stdout.
2. Include name, version, purpose, input schema, and output schema.
3. Write diagnostics to stderr and exit nonzero on failure.
4. Support JSON; XML support is recommended.

Minimal JSON description:

```json
{
  "name": "weather-tool",
  "version": "0.1.0",
  "description": "Returns current weather for a city.",
  "input_schema": {
    "type": "object",
    "properties": {"city": {"type": "string"}},
    "required": ["city"]
  },
  "output_schema": {"type": "object"}
}
```

Rules for `execute`:

1. Read the complete payload from stdin.
2. Send it to the tool API without changing its meaning.
3. Write only the successful result to stdout.
4. Write API error details to stderr and exit nonzero.
5. Never print credentials, tokens, or secret headers.

The complete reference implementation is in `examples/example_tool`.

## 5. Registry operations

```bash
llm-tools register weather-tool
llm-tools remove weather-tool
llm-tools remove weather-tool --uninstall
```

`register` adds an already installed compatible package. `remove` edits only
the registry unless `--uninstall` is supplied. Registry writes are atomic.

`LLM-tools.txt` deliberately follows a minimal requirements-style format:

```text
example-tool==0.1.0
weather-tool==1.2.0
```

Do not store endpoints or secrets there. A tool package should read its API URL
and credentials from environment variables.

## 6. Agentic installation sequence

An agent can safely follow this deterministic flow:

1. Run `llm-tools install PACKAGE`.
2. Check the process exit code.
3. Run `llm-tools describe PACKAGE --format json`.
4. Validate the LLM-generated arguments against `input_schema`.
5. Run `llm-tools execute PACKAGE --payload JSON`.
6. Treat `ok: false` as a tool failure and inspect all diagnostic fields.

Package installation uses `python -m pip` with an argument array, never a
shell command. Tool payloads go through stdin, so JSON/XML cannot become shell
syntax.

## Development

```bash
pytest
ruff check .
```

Every Python file is kept below 100 lines. Each operation lives in its own
feature folder and the `LLMTool` facade contains no subprocess logic.
