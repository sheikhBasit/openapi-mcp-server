import json
import pytest
from openapi_mcp.loader import load_spec


def test_load_from_json_file(tmp_path):
    spec = {"openapi": "3.0.0", "info": {"title": "Test", "version": "1"}, "paths": {}}
    f = tmp_path / "spec.json"
    f.write_text(json.dumps(spec))
    result = load_spec(str(f))
    assert result["openapi"] == "3.0.0"


def test_load_from_yaml_file(tmp_path):
    f = tmp_path / "spec.yaml"
    f.write_text("openapi: '3.0.0'\ninfo:\n  title: Test\n  version: '1'\npaths: {}\n")
    result = load_spec(str(f))
    assert result["openapi"] == "3.0.0"


def test_load_missing_file():
    with pytest.raises(FileNotFoundError):
        load_spec("/nonexistent/spec.json")


@pytest.mark.asyncio
async def test_load_from_url():
    import respx
    import httpx

    spec = {"openapi": "3.0.0", "info": {"title": "Remote", "version": "1"}, "paths": {}}
    with respx.mock:
        respx.get("https://api.example.com/openapi.json").mock(
            return_value=httpx.Response(200, json=spec)
        )
        result = load_spec("https://api.example.com/openapi.json")
    assert result["info"]["title"] == "Remote"
