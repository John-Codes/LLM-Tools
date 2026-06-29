import os
import re
import tempfile
from pathlib import Path

from llm_tools.models.errors import InvalidToolSpecError, ToolNotRegisteredError
from llm_tools.models.tool import ToolRecord

LINE_PATTERN = re.compile(r"^([A-Za-z0-9][A-Za-z0-9_.-]*)(?:==([^\s]+))?$")
HEADER = "# One registered Python distribution per line.\n"


class Registry:
    def __init__(self, path: str | Path | None = None):
        configured = path or os.getenv("LLM_TOOLS_FILE", "LLM-tools.txt")
        self.path = Path(configured).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def read(self) -> list[ToolRecord]:
        records: list[ToolRecord] = []
        seen: set[str] = set()
        for number, raw in enumerate(self.path.read_text().splitlines(), 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            match = LINE_PATTERN.fullmatch(line)
            if not match:
                raise InvalidToolSpecError(
                    f"Invalid registry entry at {self.path}:{number}: {line}"
                )
            if match.group(1) in seen:
                raise InvalidToolSpecError(
                    f"Duplicate tool at {self.path}:{number}: {match.group(1)}"
                )
            seen.add(match.group(1))
            records.append(ToolRecord(match.group(1), match.group(2)))
        return records

    def get(self, package: str) -> ToolRecord:
        for record in self.read():
            if record.package == package:
                return record
        raise ToolNotRegisteredError(f"Tool is not registered: {package}")

    def add(self, record: ToolRecord) -> None:
        records = [item for item in self.read() if item.package != record.package]
        self._write([*records, record])

    def remove(self, package: str) -> ToolRecord:
        removed = self.get(package)
        self._write([item for item in self.read() if item.package != package])
        return removed

    def _write(self, records: list[ToolRecord]) -> None:
        content = HEADER + "".join(f"{item.requirement}\n" for item in records)
        with tempfile.NamedTemporaryFile(
            "w", dir=self.path.parent, delete=False, encoding="utf-8"
        ) as temporary:
            temporary.write(content)
            temporary_path = Path(temporary.name)
        temporary_path.replace(self.path)
