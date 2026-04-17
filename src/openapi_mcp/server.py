import os
from typing import Any

from fastmcp import FastMCP

from openapi_mcp.executor import call_endpoint
from openapi_mcp.loader import load_spec
from openapi_mcp.parser import Endpoint, parse_spec

mcp = FastMCP("openapi-mcp-server")

_base_url: str = ""
_endpoints: dict[str, Endpoint] = {}


def _build_tool_description(endpoint: Endpoint) -> str:
    parts = []
    if endpoint.summary:
        parts.append(endpoint.summary)
    parts.append(f"{endpoint.method} {endpoint.path}")
    if endpoint.description and endpoint.description != endpoint.summary:
        parts.append(endpoint.description)
    required = [p.name for p in endpoint.params if p.required]
    if required:
        parts.append(f"Required params: {', '.join(required)}")
    return " | ".join(parts)


def register_tools(spec_source: str) -> int:
    """Load spec and register all endpoints as MCP tools. Returns count registered."""
    global _base_url, _endpoints

    spec = load_spec(spec_source)
    _base_url, endpoints = parse_spec(spec)

    for endpoint in endpoints:
        _endpoints[endpoint.operation_id] = endpoint

        # Build param schema for FastMCP
        props: dict[str, Any] = {}
        required_props: list[str] = []
        for p in endpoint.params:
            props[p.name] = {
                "type": p.type if p.type in ("string", "integer", "number", "boolean") else "string",
                "description": p.description or f"{p.location} parameter",
            }
            if p.required:
                required_props.append(p.name)

        description = _build_tool_description(endpoint)
        op_id = endpoint.operation_id

        # Dynamically register tool — closure captures op_id
        def make_handler(oid: str):
            async def handler(**kwargs: Any) -> dict:
                return await call_endpoint(_base_url, _endpoints[oid], kwargs)
            handler.__name__ = oid
            handler.__doc__ = description
            return handler

        mcp.tool(name=op_id, description=description)(make_handler(op_id))

    return len(endpoints)


def main() -> None:
    spec_source = (
        os.getenv("OPENAPI_SPEC_URL")
        or os.getenv("OPENAPI_SPEC_FILE")
    )
    if not spec_source:
        raise SystemExit(
            "Set OPENAPI_SPEC_URL (remote) or OPENAPI_SPEC_FILE (local path) before starting."
        )
    count = register_tools(spec_source)
    print(f"[openapi-mcp] Registered {count} tools from {spec_source}")
    mcp.run()


if __name__ == "__main__":
    main()
