import shutil

from llm_tools.models.tool import ToolRecord
from llm_tools.registry.store import Registry


class DiscoveryService:
    def __init__(self, registry: Registry):
        self.registry = registry

    def get_tools(self) -> list[ToolRecord]:
        return self.registry.read()

    def status(self) -> list[dict[str, object]]:
        return [
            {**tool.to_dict(), "available": shutil.which(tool.command) is not None}
            for tool in self.get_tools()
        ]

