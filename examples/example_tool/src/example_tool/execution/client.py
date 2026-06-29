import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class APIError(Exception):
    pass


def execute(payload: str, format: str, timeout: float = 30) -> str:
    base_url = os.getenv("EXAMPLE_TOOL_URL", "http://127.0.0.1:8000")
    request = Request(
        f"{base_url}/execute?format={format}", data=payload.encode(),
        headers={"Content-Type": content_type(format)}, method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read().decode()
    except HTTPError as error:
        body = error.read().decode(errors="replace")
        raise APIError(f"HTTP {error.code}: {body}") from error
    except URLError as error:
        raise APIError(f"API connection failed: {error.reason}") from error


def describe(format: str, timeout: float = 30) -> str:
    base_url = os.getenv("EXAMPLE_TOOL_URL", "http://127.0.0.1:8000")
    url = f"{base_url}/description?format={format}"
    try:
        with urlopen(url, timeout=timeout) as response:
            return response.read().decode()
    except HTTPError as error:
        body = error.read().decode(errors="replace")
        raise APIError(f"HTTP {error.code}: {body}") from error
    except URLError as error:
        raise APIError(f"API connection failed: {error.reason}") from error


def content_type(format: str) -> str:
    return "application/json" if format == "json" else "application/xml"
