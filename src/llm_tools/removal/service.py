import sys

from llm_tools.models.errors import ToolCommandError
from llm_tools.models.tool import ToolRecord
from llm_tools.process.runner import run_command
from llm_tools.registry.store import Registry


class RemovalService:
    def __init__(self, registry: Registry):
        self.registry = registry

    def remove(
        self, package: str, uninstall: bool = False, timeout: float = 300
    ) -> ToolRecord:
        record = self.registry.get(package)
        if uninstall:
            result = run_command(
                [sys.executable, "-m", "pip", "uninstall", "-y", package],
                timeout=timeout,
            )
            if not result.ok:
                raise ToolCommandError(f"Could not uninstall {package}", result)
        return self.registry.remove(package)

