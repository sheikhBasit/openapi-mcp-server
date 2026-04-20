# openapi-mcp-server

Runtime OpenAPI → MCP bridge. Point it at any OpenAPI spec and every endpoint becomes an MCP tool — no code generation, pure runtime.

## How It Works

1. Set `OPENAPI_SPEC_URL` or `OPENAPI_SPEC_FILE`
2. Start the server — it reads the spec and registers every `operationId` as an MCP tool
3. Your AI agent can now call any API endpoint by name

## Quick Start

```bash
git clone https://github.com/sheikhBasit/openapi-mcp-server
cd openapi-mcp-server
python -m venv .venv && .venv/bin/pip install -e .

# Point at any OpenAPI spec
OPENAPI_SPEC_URL=https://petstore3.swagger.io/api/v3/openapi.json openapi-mcp
```

## Claude Desktop Config

```json
{
  "mcpServers": {
    "myapi": {
      "command": "/path/to/.venv/bin/openapi-mcp",
      "env": {
        "OPENAPI_SPEC_URL": "https://your-api.com/openapi.json",
        "API_BEARER_TOKEN": "your-token-here"
      }
    }
  }
}
```

## Environment Variables

| Variable | Description |
|---|---|
| `OPENAPI_SPEC_URL` | URL to OpenAPI spec (JSON or YAML) |
| `OPENAPI_SPEC_FILE` | Local file path to OpenAPI spec |
| `API_BEARER_TOKEN` | Bearer token — added as `Authorization: Bearer <token>` |
| `AUTH_HEADER_NAME` | Custom auth header name (e.g. `X-API-Key`) |
| `AUTH_HEADER_VALUE` | Custom auth header value |

## Supports

- OpenAPI 3.x specs (JSON and YAML)
- Path, query, header, and body parameters
- GET, POST, PUT, PATCH, DELETE methods
- Bearer token and custom header auth
- Local files and remote URLs

## Usage Examples

```
list all users from the API
create a user with name "Alice" and email "alice@example.com"
get user with id 42
```

## Running Tests

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT


---

## Knowledge Graph

This repo is indexed by [Understand Anything](https://github.com/Lum1104/Understand-Anything) — a multi-agent pipeline that builds a knowledge graph of every file, function, class, and dependency.

The graph lives at `.understand-anything/knowledge-graph.json` and can be explored visually:

```bash
# In Claude Code, from this repo root:
/understand-dashboard
```

To rebuild the graph after major changes:

```bash
~/scripts/graphify-all.sh
```

> Graph covers: files · functions · classes · imports · architecture layers · plain-English summaries · guided tours.
