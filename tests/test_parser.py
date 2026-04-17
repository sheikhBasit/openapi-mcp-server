from openapi_mcp.parser import parse_spec

SAMPLE_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "Test API", "version": "1.0"},
    "servers": [{"url": "https://api.example.com/v1"}],
    "paths": {
        "/users": {
            "get": {
                "operationId": "listUsers",
                "summary": "List all users",
                "parameters": [
                    {
                        "name": "limit",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "integer"},
                        "description": "Max results",
                    }
                ],
            },
            "post": {
                "operationId": "createUser",
                "summary": "Create a user",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["name"],
                                "properties": {
                                    "name": {"type": "string", "description": "User name"},
                                    "email": {"type": "string", "description": "Email"},
                                },
                            }
                        }
                    }
                },
            },
        },
        "/users/{id}": {
            "get": {
                "operationId": "getUser",
                "summary": "Get a user by ID",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
            }
        },
    },
}


def test_parse_base_url():
    base_url, _ = parse_spec(SAMPLE_SPEC)
    assert base_url == "https://api.example.com/v1"


def test_parse_endpoint_count():
    _, endpoints = parse_spec(SAMPLE_SPEC)
    assert len(endpoints) == 3


def test_parse_get_endpoint():
    _, endpoints = parse_spec(SAMPLE_SPEC)
    ep = next(e for e in endpoints if e.operation_id == "listUsers")
    assert ep.method == "GET"
    assert ep.path == "/users"
    assert len(ep.params) == 1
    assert ep.params[0].name == "limit"
    assert ep.params[0].location == "query"


def test_parse_post_with_body():
    _, endpoints = parse_spec(SAMPLE_SPEC)
    ep = next(e for e in endpoints if e.operation_id == "createUser")
    assert ep.method == "POST"
    body_params = [p for p in ep.params if p.location == "body"]
    assert len(body_params) == 2
    required = [p.name for p in body_params if p.required]
    assert "name" in required


def test_parse_path_param():
    _, endpoints = parse_spec(SAMPLE_SPEC)
    ep = next(e for e in endpoints if e.operation_id == "getUser")
    assert ep.params[0].location == "path"
    assert ep.params[0].required is True


def test_safe_operation_id():
    spec = {
        "servers": [{"url": "https://api.example.com"}],
        "paths": {
            "/foo": {
                "get": {
                    "operationId": "my-operation.v2",
                    "summary": "Test",
                }
            }
        },
    }
    _, endpoints = parse_spec(spec)
    assert endpoints[0].operation_id == "my_operation_v2"
