import subprocess
from collections.abc import Sequence

from llm_tools.models.result import ExecutionResult


def run_command(
    command: Sequence[str], payload: str | None = None, timeout: float = 30
) -> ExecutionResult:
    try:
        completed = subprocess.run(
            command,
            input=payload,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as error:
        return _failure("command_not_found", str(error))
    except subprocess.TimeoutExpired as error:
        return _failure(
            "timeout",
            f"Command exceeded {timeout} seconds",
            _text(error.stdout),
            _text(error.stderr),
            timed_out=True,
        )
    except OSError as error:
        return _failure(type(error).__name__, str(error))
    if completed.returncode:
        message = completed.stderr.strip() or "Tool command failed"
        return _failure(
            "nonzero_exit", message, completed.stdout, completed.stderr,
            completed.returncode,
        )
    return ExecutionResult(
        ok=True,
        stdout=completed.stdout,
        stderr=completed.stderr,
        exit_code=completed.returncode,
    )


def _failure(
    kind: str, message: str, stdout: str = "", stderr: str = "",
    code: int | None = None, timed_out: bool = False,
) -> ExecutionResult:
    return ExecutionResult(
        ok=False, stdout=stdout, stderr=stderr, exit_code=code,
        error_type=kind, error_message=message, timed_out=timed_out,
    )


def _text(value: str | bytes | None) -> str:
    return value.decode() if isinstance(value, bytes) else value or ""

