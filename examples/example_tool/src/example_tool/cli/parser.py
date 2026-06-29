import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="example-tool")
    commands = parser.add_subparsers(dest="action", required=True)
    for name in ("describe", "execute"):
        command = commands.add_parser(name)
        command.add_argument("--format", choices=["json", "xml"], default="json")
        command.add_argument("--timeout", type=float, default=30)
    return parser.parse_args()

