from dataclasses import dataclass, field
from typing import Any


@dataclass
class EndpointParam:
    name: str
    location: str  # path, query, header, body
    required: bool
    description: str
    type: str  # string, integer, boolean, object


@dataclass
class Endpoint:
    operation_id: str
    method: str
    path: str
    summary: str
    description: str
    params: list[EndpointParam] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


def _safe_id(operation_id: str) -> str:
    """Make operation_id safe for use as a Python function name."""
    import re
    return re.sub(r"[^a-zA-Z0-9_]", "_", operation_id)[:64]


def parse_spec(spec: dict[str, Any]) -> tuple[str, list[Endpoint]]:
    """Extract base URL and all endpoints from an OpenAPI 3.x spec."""
    # Base URL
    servers = spec.get("servers", [])
    base_url = servers[0].get("url", "") if servers else ""

    endpoints = []
    paths = spec.get("paths", {})

    for path, path_item in paths.items():
        for method in ("get", "post", "put", "patch", "delete"):
            op = path_item.get(method)
            if not op:
                continue

            operation_id = op.get("operationId") or f"{method}_{path.replace('/', '_').strip('_')}"
            safe_id = _safe_id(operation_id)
            summary = op.get("summary") or ""
            description = op.get("description") or summary

            params: list[EndpointParam] = []

            # Path + query + header params
            for p in op.get("parameters", []):
                schema = p.get("schema", {})
                params.append(EndpointParam(
                    name=p.get("name", ""),
                    location=p.get("in", "query"),
                    required=p.get("required", False),
                    description=p.get("description") or "",
                    type=schema.get("type", "string"),
                ))

            # Request body
            body = op.get("requestBody", {})
            if body:
                content = body.get("content", {})
                for media_type in ("application/json", "application/x-www-form-urlencoded"):
                    if media_type in content:
                        schema = content[media_type].get("schema", {})
                        props = schema.get("properties", {})
                        required_body = schema.get("required", [])
                        for prop_name, prop_schema in props.items():
                            params.append(EndpointParam(
                                name=prop_name,
                                location="body",
                                required=prop_name in required_body,
                                description=prop_schema.get("description") or "",
                                type=prop_schema.get("type", "string"),
                            ))
                        break

            endpoints.append(Endpoint(
                operation_id=safe_id,
                method=method.upper(),
                path=path,
                summary=summary,
                description=description,
                params=params,
                tags=op.get("tags", []),
            ))

    return base_url, endpoints
