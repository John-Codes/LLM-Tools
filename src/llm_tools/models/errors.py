from llm_tools.models.result import ExecutionResult


class LLMToolsError(Exception):
    """Base error for registry and contract failures."""


class InvalidToolSpecError(LLMToolsError):
    pass


class ToolNotRegisteredError(LLMToolsError):
    pass


class ToolCommandError(LLMToolsError):
    def __init__(self, message: str, result: ExecutionResult):
        super().__init__(message)
        self.result = result

