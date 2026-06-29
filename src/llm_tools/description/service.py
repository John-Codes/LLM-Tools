import json
from typing import Any

from llm_tools.models.errors import ToolCommandError
from llm_tools.process.runner import run_command
from llm_tools.registry.store import Registry


class DescriptionService:
    def __init__(self, registry: Registry):
        self.registry = registry

    def describe(
        self, package: str, format: str = "json", timeout: float = 30
    ) -> dict[str, Any] | str:
        tool = self.registry.get(package)
        result = run_command(
            [tool.command, "describe", "--format", format], timeout=timeout
        )
        if not result.ok:
            raise ToolCommandError(f"Could not describe {package}", result)
        if format == "xml":
            return result.stdout
        try:
            document = json.loads(result.stdout)
        except json.JSONDecodeError as error:
            failed = result.__class__(
                ok=False, stdout=result.stdout, stderr=result.stderr,
                exit_code=result.exit_code, error_type="invalid_json",
                error_message=str(error),
            )
            message = f"Invalid description from {package}"
            raise ToolCommandError(message, failed) from error
        if not isinstance(document, dict):
            raise ToolCommandError(
                f"Description from {package} is not an object",
                result.__class__(
                    ok=False, stdout=result.stdout, exit_code=0,
                    error_type="invalid_schema",
                    error_message="Description must be a JSON object",
                ),
            )
        return document
