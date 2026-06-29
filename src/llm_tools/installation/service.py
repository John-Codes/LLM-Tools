import importlib.metadata
import re
import shutil
import sys

from llm_tools.models.errors import InvalidToolSpecError, ToolCommandError
from llm_tools.models.result import ExecutionResult
from llm_tools.models.tool import ToolRecord
from llm_tools.process.runner import run_command
from llm_tools.registry.store import Registry

NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


class InstallationService:
    def __init__(self, registry: Registry):
        self.registry = registry

    def install(
        self, package: str, source: str | None = None, timeout: float = 300
    ) -> ToolRecord:
        self._validate(package)
        if source and source.startswith("-"):
            raise InvalidToolSpecError("A pip source cannot start with '-'")
        result = run_command(
            [sys.executable, "-m", "pip", "install", source or package],
            timeout=timeout,
        )
        if not result.ok:
            raise ToolCommandError(f"Could not install {package}", result)
        return self.register(package)

    def register(self, package: str) -> ToolRecord:
        self._validate(package)
        try:
            version = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError as error:
            message = f"Package is not installed: {package}"
            raise InvalidToolSpecError(message) from error
        if shutil.which(package) is None:
            result = ExecutionResult(
                ok=False, error_type="command_not_found",
                error_message=f"Package did not install the required '{package}' CLI",
            )
            raise ToolCommandError(f"Invalid tool package: {package}", result)
        record = ToolRecord(package, version)
        self.registry.add(record)
        return record

    @staticmethod
    def _validate(package: str) -> None:
        if not NAME_PATTERN.fullmatch(package):
            raise InvalidToolSpecError(f"Invalid package name: {package}")
