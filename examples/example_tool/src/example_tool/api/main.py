import json
from typing import Any
from xml.etree.ElementTree import ParseError, fromstring

from fastapi import FastAPI, HTTPException, Request, Response

from example_tool.description.formats import to_xml
from example_tool.description.schema import SCHEMA

app = FastAPI(title="Example LLM Tool")


@app.get("/description")
def description(format: str = "json") -> Any:
    if format == "json":
        return SCHEMA
    if format == "xml":
        return Response(to_xml(SCHEMA), media_type="application/xml")
    raise HTTPException(400, "format must be json or xml")


@app.post("/execute")
async def execute(request: Request, format: str = "json") -> Any:
    raw = (await request.body()).decode()
    try:
        text = json.loads(raw)["text"] if format == "json" else xml_text(raw)
    except (KeyError, ParseError, TypeError, ValueError) as error:
        raise HTTPException(422, f"Invalid payload: {error}") from error
    if not isinstance(text, str):
        raise HTTPException(422, "text must be a string")
    result = {"result": text.upper()}
    if format == "json":
        return result
    return Response(to_xml(result), media_type="application/xml")


def xml_text(raw: str) -> str:
    text = fromstring(raw).findtext("text")
    if text is None:
        raise ValueError("XML payload requires a text element")
    return text
