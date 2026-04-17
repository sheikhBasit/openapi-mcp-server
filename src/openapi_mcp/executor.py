import os
from typing import Any

import httpx

from openapi_mcp.parser import Endpoint


def _build_auth_headers() -> dict[str, str]:
    name = os.getenv("AUTH_HEADER_NAME")
    value = os.getenv("AUTH_HEADER_VALUE")
    if name and value:
        return {name: value}
    # Bearer token shorthand
    token = os.getenv("API_BEARER_TOKEN")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


async def call_endpoint(
    base_url: str,
    endpoint: Endpoint,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """Execute an API call for the given endpoint with provided arguments."""
    path = endpoint.path
    query_params: dict[str, Any] = {}
    body_params: dict[str, Any] = {}
    headers = _build_auth_headers()

    for param in endpoint.params:
        value = arguments.get(param.name)
        if value is None:
            continue
        if param.location == "path":
            path = path.replace(f"{{{param.name}}}", str(value))
        elif param.location == "query":
            query_params[param.name] = value
        elif param.location == "header":
            headers[param.name] = str(value)
        elif param.location == "body":
            body_params[param.name] = value

    url = base_url.rstrip("/") + path

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.request(
                method=endpoint.method,
                url=url,
                params=query_params or None,
                json=body_params or None,
                headers=headers,
            )
            try:
                data = resp.json()
            except Exception:
                data = resp.text

            return {
                "status_code": resp.status_code,
                "data": data,
                "error": None if resp.is_success else f"HTTP {resp.status_code}",
            }
    except httpx.TimeoutException:
        return {"status_code": None, "data": None, "error": "Request timed out"}
    except Exception as e:
        return {"status_code": None, "data": None, "error": str(e)}
