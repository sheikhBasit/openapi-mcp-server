import pytest
import respx
import httpx
from openapi_mcp.executor import call_endpoint
from openapi_mcp.parser import Endpoint, EndpointParam

GET_ENDPOINT = Endpoint(
    operation_id="listUsers",
    method="GET",
    path="/users",
    summary="List users",
    description="List users",
    params=[
        EndpointParam(name="limit", location="query", required=False, description="Max", type="integer")
    ],
)

POST_ENDPOINT = Endpoint(
    operation_id="createUser",
    method="POST",
    path="/users",
    summary="Create user",
    description="Create user",
    params=[
        EndpointParam(name="name", location="body", required=True, description="Name", type="string")
    ],
)

PATH_ENDPOINT = Endpoint(
    operation_id="getUser",
    method="GET",
    path="/users/{id}",
    summary="Get user",
    description="Get user",
    params=[
        EndpointParam(name="id", location="path", required=True, description="User ID", type="string")
    ],
)


@pytest.mark.asyncio
async def test_get_with_query_param():
    with respx.mock:
        respx.get("https://api.example.com/v1/users").mock(
            return_value=httpx.Response(200, json=[{"id": 1, "name": "Alice"}])
        )
        result = await call_endpoint("https://api.example.com/v1", GET_ENDPOINT, {"limit": 10})
    assert result["status_code"] == 200
    assert result["error"] is None
    assert result["data"][0]["name"] == "Alice"


@pytest.mark.asyncio
async def test_post_with_body():
    with respx.mock:
        respx.post("https://api.example.com/v1/users").mock(
            return_value=httpx.Response(201, json={"id": 2, "name": "Bob"})
        )
        result = await call_endpoint("https://api.example.com/v1", POST_ENDPOINT, {"name": "Bob"})
    assert result["status_code"] == 201
    assert result["error"] is None


@pytest.mark.asyncio
async def test_path_param_substitution():
    with respx.mock:
        respx.get("https://api.example.com/v1/users/42").mock(
            return_value=httpx.Response(200, json={"id": 42})
        )
        result = await call_endpoint("https://api.example.com/v1", PATH_ENDPOINT, {"id": "42"})
    assert result["status_code"] == 200


@pytest.mark.asyncio
async def test_http_error_returned_gracefully():
    with respx.mock:
        respx.get("https://api.example.com/v1/users").mock(
            return_value=httpx.Response(404, json={"detail": "not found"})
        )
        result = await call_endpoint("https://api.example.com/v1", GET_ENDPOINT, {})
    assert result["status_code"] == 404
    assert result["error"] is not None
