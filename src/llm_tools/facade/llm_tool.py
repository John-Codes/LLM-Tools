from pathlib import Path
from typing import Any

from llm_tools.description.service import DescriptionService
from llm_tools.discovery.service import DiscoveryService
from llm_tools.execution.service import ExecutionService
from llm_tools.installation.service import InstallationService
from llm_tools.models.result import ExecutionResult
from llm_tools.models.tool import ToolRecord
from llm_tools.registry.store import Registry
from llm_tools.removal.service import RemovalService


class LLMTool:
    def __init__(self, registry_path: str | Path | None = None):
        self.registry = Registry(registry_path)
        self.discovery = DiscoveryService(self.registry)
        self.descriptions = DescriptionService(self.registry)
        self.executions = ExecutionService(self.registry)
        self.installations = InstallationService(self.registry)
        self.removals = RemovalService(self.registry)

    def get_tools(self) -> list[ToolRecord]:
        return self.discovery.get_tools()

    def status(self) -> list[dict[str, object]]:
        return self.discovery.status()

    def install(
        self, package: str, source: str | None = None, timeout: float = 300
    ) -> ToolRecord:
        return self.installations.install(package, source, timeout)

    def register(self, package: str) -> ToolRecord:
        return self.installations.register(package)

    def describe(
        self, package: str, format: str = "json", timeout: float = 30
    ) -> dict[str, Any] | str:
        return self.descriptions.describe(package, format, timeout)

    def execute(
        self, package: str, payload: Any, format: str = "json", timeout: float = 30
    ) -> ExecutionResult:
        return self.executions.execute(package, payload, format, timeout)

    def remove(
        self, package: str, uninstall: bool = False, timeout: float = 300
    ) -> ToolRecord:
        return self.removals.remove(package, uninstall, timeout)

