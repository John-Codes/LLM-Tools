import json
from typing import Any

from llm_tools.execution.formats import parse_output, serialize
from llm_tools.models.result import ExecutionResult
from llm_tools.process.runner import run_command
from llm_tools.registry.store import Registry


class ExecutionService:
    def __init__(self, registry: Registry):
        self.registry = registry

    def execute(
        self, package: str, payload: Any, format: str = "json", timeout: float = 30
    ) -> ExecutionResult:
        tool = self.registry.get(package)
        encoded = serialize(payload, format)
        result = run_command(
            [tool.command, "execute", "--format", format], encoded, timeout
        )
        if not result.ok:
            return result
        try:
            output = parse_output(result.stdout, format)
        except json.JSONDecodeError as error:
            return ExecutionResult(
                ok=False, stdout=result.stdout, stderr=result.stderr,
                exit_code=result.exit_code, error_type="invalid_json",
                error_message=str(error),
            )
        return ExecutionResult(
            ok=True, output=output, stdout=result.stdout,
            stderr=result.stderr, exit_code=result.exit_code,
        )

