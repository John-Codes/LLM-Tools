import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="llm-tools")
    parser.add_argument("--registry", help="Path to LLM-tools.txt")
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("list", help="List registered tools")
    install = commands.add_parser("install", help="Install and register a tool")
    install.add_argument("package")
    install.add_argument("--source", help="pip source, such as a local directory")
    register = commands.add_parser("register", help="Register an installed tool")
    register.add_argument("package")
    describe = commands.add_parser("describe", help="Get a tool schema")
    describe.add_argument("package")
    describe.add_argument("--format", choices=["json", "xml"], default="json")
    describe.add_argument("--timeout", type=float, default=30)
    execute = commands.add_parser("execute", help="Execute a registered tool")
    execute.add_argument("package")
    execute.add_argument("--payload", required=True)
    execute.add_argument("--format", choices=["json", "xml"], default="json")
    execute.add_argument("--timeout", type=float, default=30)
    remove = commands.add_parser("remove", help="Remove a registered tool")
    remove.add_argument("package")
    remove.add_argument("--uninstall", action="store_true")
    return parser

