from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    ok: bool
    output: Any = None
    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    error_type: str | None = None
    error_message: str | None = None
    timed_out: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

