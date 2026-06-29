# LLM Tools: Install and Manage Python Tools for AI Agents

## The LLM tool-management problem

Giving an LLM one tool is easy. Keeping many tools installed, documented,
versioned, and working across several AI agents is not.

A typical Python agent project starts with a few copied tool files. Soon it has
large nested folders, duplicated API clients, hard-coded endpoints, stale Git
clones, and different versions of the same tool. Every agent framework expects
a different schema. Moving the agent to another computer means finding and
installing everything again. An LLM cannot reliably install these tools by
itself because there is no standard client-side package contract.

This creates practical problems:

- Where is each tool installed?
- Which version does this agent use?
- How does the LLM learn the correct arguments?
- Does the tool expect JSON, XML, or a provider-specific schema?
- How is the API called without copying its client into every project?
- What error information reaches the agent when a call fails?

`LLM Tools` solves this with a lightweight Python LLM tool manager. Each tool
is a normal pip package. The manager installs it on the agent's machine,
records its exact version, asks it for usage instructions, and executes it
through one predictable contract.

The tool's real work can remain on a FastAPI server, commercial API, local
model, or local Python service. Only a small client package is installed beside
the agent. This clean separation keeps server logic on the server and gives the
LLM a reliable client-side interface.

## Before and after LLM Tools

Without a tool manager, setup often looks like this:

```text
agent/
├── tools/
│   ├── copied_weather_client/
│   ├── old_search_tool/
│   ├── search_tool_new/
│   └── random_helpers/
├── tool_schemas/
└── undocumented_setup_steps.txt
```

Nobody knows which folder is current, which Git commit is required, or which
schema the LLM should use.

With LLM Tools, the same agent has one readable registry:

```text
# LLM-tools.txt
weather-tool==1.2.0
search-tool==2.1.3
```

Installing and using a published tool becomes three beginner-friendly commands.
Here, `weather-tool` is an example package name; a fully runnable package is
provided later in this README.

```bash
# 1. Install the tool package and save its version.
llm-tools install weather-tool

# 2. Ask the package how the LLM should use it.
llm-tools describe weather-tool --format json

# 3. Execute the tool with ordinary JSON data.
llm-tools execute weather-tool --payload '{"city":"Chicago"}'
```

That is the main benefit: an agent can install an LLM tool with pip, discover
its schema, and call it without cloning repositories, copying source files, or
writing a new integration for every model provider.

## Why client-side LLM tool installation is better

Client-side installation makes tools behave like normal Python dependencies.
Each agent chooses and pins the versions it needs. Another developer can read
`LLM-tools.txt`, recreate the same setup, and understand exactly what the LLM
can call.

The manager provides:

- one requirements-style `LLM-tools.txt` registry;
- automatic pip installation and exact version tracking;
- one Python class for discovery, description, execution, and removal;
- one CLI contract shared by every independent tool package;
- JSON and XML for open-source and vendor-locked LLMs;
- structured failures with stderr, exit code, timeout, and error type;
- no copied API clients, giant tool folders, or hidden Git-version guesses;
- no secrets in the registry.

This makes LLM tool discovery and installation simple enough for a person,
Python application, or AI agent to perform safely and repeatably.

## Install with pip

Python 3.11 or newer is required. Start in the folder containing your agent.
A virtual environment keeps its tools separate from other Python projects:

```bash
# Create a private Python environment inside the current project.
python -m venv .venv

# Activate it on Linux or macOS.
source .venv/bin/activate

# Windows users run this activation command instead:
# .venv\Scripts\activate
```

Now install LLM Tools directly from GitHub with one pip command:

```bash
python -m pip install "git+https://github.com/John-Codes/LLM-Tools.git"
```

Confirm that it is ready:

```bash
llm-tools --help
```

That installs the `llm-tools` command and the `LLMTool` Python class. You do not
need to copy this repository into every agent project.

After a release is published to PyPI, installation becomes:

```bash
python -m pip install llm-tools
```

## Install an LLM tool

Installing a compatible, published tool is one command. Replace
`YOUR_TOOL_PACKAGE` with its pip package name:

```bash
llm-tools install YOUR_TOOL_PACKAGE
```

LLM Tools runs pip safely, confirms that the tool command exists, detects the
installed version, and records it in `LLM-tools.txt`. The resulting file is as
simple as a Python requirements file:

```text
YOUR_TOOL_PACKAGE==1.2.0
```

Now an agent can discover, understand, and call the package:

```bash
llm-tools list
llm-tools describe YOUR_TOOL_PACKAGE --format json
llm-tools execute YOUR_TOOL_PACKAGE --payload '{"input":"value"}'
```

The default registry is `LLM-tools.txt` in the current directory. Override it
with `LLM_TOOLS_FILE` or `LLMTool("path/to/LLM-tools.txt")`.

## Five-minute working example

This repository includes `example-tool`, a real pip package backed by FastAPI.
It accepts text and returns the uppercase version. Install both the manager and
the example without cloning the repository:

Install it:

```bash
python -m pip install "git+https://github.com/John-Codes/LLM-Tools.git"
llm-tools install example-tool \
  --source "git+https://github.com/John-Codes/LLM-Tools.git#subdirectory=examples/example_tool"
```

Start its API in terminal one:

```bash
source .venv/bin/activate
uvicorn example_tool.api.main:app --port 8000
```

Use it in terminal two:

```bash
source .venv/bin/activate
llm-tools list
llm-tools describe example-tool --format json
llm-tools execute example-tool --payload '{"text":"hello LLM"}'
```

The execution result includes both the tool output and call diagnostics:

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

## Simple Python example

This is the complete client-side flow an agent needs:

```python
from llm_tools import LLMTool

# Creates LLM-tools.txt automatically if it does not exist.
tools = LLMTool("LLM-tools.txt")

# Install from PyPI and pin the installed version in LLM-tools.txt.
# tools.install("weather-tool")

# See which tools the agent can use.
for tool in tools.get_tools():
    print(tool.package, tool.version)

# Ask the package how the LLM should call it.
schema = tools.describe("example-tool", format="json")
print(schema["description"])
print(schema["input_schema"])

# Call the tool using ordinary Python data.
result = tools.execute(
    "example-tool",
    payload={"text": "hello from Python"},
    format="json",
)

if result.ok:
    print(result.output)  # {'result': 'HELLO FROM PYTHON'}
else:
    print(result.to_dict())
```

There are only three concepts: read registered tools, describe one tool, then
execute it with a payload. Installation and removal maintain the same registry.

## Agentic installation

An agent can install a published tool without cloning its Git repository:

```python
from llm_tools import LLMTool

tools = LLMTool()
installed = tools.install("weather-tool")
schema = tools.describe(installed.package)
result = tools.execute(installed.package, {"city": "Chicago"})
```

For a local package or Git checkout, identify its required command name and
pass its directory as the pip source:

```python
tools.install("example-tool", source="./examples/example_tool")
```

Equivalent agent-friendly CLI commands are:

```bash
llm-tools install weather-tool
llm-tools install example-tool --source ./examples/example_tool
llm-tools describe example-tool --format json
llm-tools execute example-tool --payload '{"text":"hello"}'
llm-tools remove example-tool
llm-tools remove weather-tool --uninstall
```

This makes tool installation reproducible: pip handles the package while
`LLM-tools.txt` records the exact installed version for the agent project.

## JSON and XML

Use JSON for most Python agents:

```python
schema = tools.describe("example-tool", format="json")
result = tools.execute("example-tool", {"text": "hello"}, format="json")
```

Use XML when a model or provider performs better with XML contracts:

```python
xml_schema = tools.describe("example-tool", format="xml")
xml_payload = "<payload><text>hello</text></payload>"
result = tools.execute("example-tool", xml_payload, format="xml")
```

The manager does not depend on a specific model SDK. The same registry can sit
behind Ollama, llama.cpp, vLLM, OpenAI-compatible clients, or vendor SDKs.

## Failures are never hidden

`execute()` returns structured failure information instead of an empty value:

```python
result = tools.execute("example-tool", {"text": "hello"}, timeout=10)

if not result.ok:
    print(result.error_type)
    print(result.error_message)
    print(result.stderr)
    print(result.exit_code)
    print(result.timed_out)
```

Missing registrations and invalid configuration raise explicit exceptions.
Describe, install, and removal failures raise `ToolCommandError`; inspect
`error.result.to_dict()` for the same diagnostics.

## Build a compatible tool

A tool is just a small pip package that exposes `describe` and `execute`. The
CLI forwards those calls to the tool's FastAPI service. Start with this layout:

```text
weather-tool/
├── pyproject.toml
└── src/
    └── weather_tool/
        ├── __init__.py
        └── cli.py
```

### Step 1: define the pip package

Create `weather-tool/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "weather-tool"
version = "0.1.0"
requires-python = ">=3.11"

[project.scripts]
weather-tool = "weather_tool.cli:main"

[tool.setuptools.packages.find]
where = ["src"]
```

The distribution name and command name are both `weather-tool`. This is how the
registry finds the installed command without extra configuration.

### Step 2: create the tool CLI

Create an empty `weather-tool/src/weather_tool/__init__.py`, then create
`weather-tool/src/weather_tool/cli.py`:

```python
import argparse
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_URL = os.getenv("WEATHER_TOOL_URL", "http://127.0.0.1:8000")


def call_api(request: str | Request) -> None:
    try:
        with urlopen(request, timeout=30) as response:
            print(response.read().decode())
    except HTTPError as error:
        print(error.read().decode(), file=sys.stderr)
        raise SystemExit(1) from error
    except URLError as error:
        print(f"API connection failed: {error.reason}", file=sys.stderr)
        raise SystemExit(1) from error


def main() -> None:
    parser = argparse.ArgumentParser(prog="weather-tool")
    commands = parser.add_subparsers(dest="action", required=True)
    for name in ("describe", "execute"):
        command = commands.add_parser(name)
        command.add_argument("--format", choices=["json", "xml"], default="json")
    args = parser.parse_args()

    if args.action == "describe":
        call_api(f"{API_URL}/description?format={args.format}")
        return

    payload = sys.stdin.buffer.read()
    request = Request(
        f"{API_URL}/execute?format={args.format}",
        data=payload,
        headers={"Content-Type": f"application/{args.format}"},
        method="POST",
    )
    call_api(request)


if __name__ == "__main__":
    main()
```

The FastAPI service implements two endpoints:

- `GET /description?format=json` returns the tool instructions and schemas.
- `POST /execute?format=json` accepts the payload and returns the tool result.

Use XML instead by passing `format=xml`. The complete working API and CLI are
in [`examples/example_tool`](examples/example_tool).

### Step 3: install and test the tool locally

From the agent project directory:

```bash
llm-tools install weather-tool --source ./weather-tool
llm-tools describe weather-tool --format json
llm-tools execute weather-tool --payload '{"city":"Chicago"}'
```

The first command uses pip to install the local package and adds its exact
version to `LLM-tools.txt`. No manual registry editing is required.

### Step 4: publish it for agentic installation

Publish `weather-tool` to a Python package index using your normal build and
release process. Other agents can then install it without its Git folder:

```bash
llm-tools install weather-tool
```

`describe` must write the name, version, purpose, input schema, and output
schema to stdout. `execute` reads its payload from stdin. Failures must go to
stderr with a nonzero exit code. Keep API URLs and credentials in environment
variables, never in `LLM-tools.txt`.

## Clean project structure

Every Python code file in this repository is under 100 lines. A test enforces
that limit. Each feature has its own folder and one responsibility:

```text
src/llm_tools/
├── discovery/       # get registered tools
├── description/     # get schemas for an LLM
├── execution/       # send payloads and return results
├── installation/    # pip install and register
├── removal/         # unregister or uninstall
├── registry/        # read and atomically write LLM-tools.txt
├── process/         # safe subprocess calls
└── facade/          # the small LLMTool public API
```

This single-responsibility structure keeps the library simple to read, test,
replace, and extend without creating another large tool framework.

## Development

```bash
python -m pip install -e '.[dev]'
pytest
ruff check .
```

The test suite covers registry parsing, discovery, successful execution,
failure diagnostics, and the under-100-line code rule.
