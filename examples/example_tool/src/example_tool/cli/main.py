import json
import sys

from example_tool.cli.parser import parse_args
from example_tool.execution.client import APIError, describe, execute


def main() -> None:
    args = parse_args()
    try:
        output = (
            describe(args.format, args.timeout)
            if args.action == "describe"
            else execute(sys.stdin.read(), args.format, args.timeout)
        )
    except APIError as error:
        print(json.dumps({"error_type": "api_error", "message": str(error)}),
              file=sys.stderr)
        raise SystemExit(1) from error
    print(output)


if __name__ == "__main__":
    main()

