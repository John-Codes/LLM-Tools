import json
from argparse import Namespace
from typing import Any

from llm_tools.cli.parser import build_parser
from llm_tools.facade.llm_tool import LLMTool
from llm_tools.models.errors import LLMToolsError, ToolCommandError


def main() -> None:
    args = build_parser().parse_args()
    try:
        output, failed = dispatch(args), False
    except ToolCommandError as error:
        output, failed = error.result.to_dict(), True
    except LLMToolsError as error:
        output = {"ok": False, "error_type": type(error).__name__,
                  "error_message": str(error)}
        failed = True
    print(render(output))
    if failed or getattr(output, "ok", True) is False:
        raise SystemExit(1)


def dispatch(args: Namespace) -> Any:
    tools = LLMTool(args.registry)
    if args.action == "list":
        return tools.status()
    if args.action == "install":
        return tools.install(args.package, args.source).to_dict()
    if args.action == "register":
        return tools.register(args.package).to_dict()
    if args.action == "describe":
        return tools.describe(args.package, args.format, args.timeout)
    if args.action == "execute":
        payload = json.loads(args.payload) if args.format == "json" else args.payload
        return tools.execute(args.package, payload, args.format, args.timeout)
    return tools.remove(args.package, args.uninstall).to_dict()


def render(value: Any) -> str:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    if isinstance(value, str):
        return value
    return json.dumps(value, indent=2)


if __name__ == "__main__":
    main()

