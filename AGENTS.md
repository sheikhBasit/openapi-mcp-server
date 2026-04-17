# AGENTS.md

This file provides guidance to AI coding agents (Claude Code, Cursor, GitHub Copilot, etc.)
working in this repository.

## Project
MCP server that dynamically registers any OpenAPI spec as callable AI tools at runtime. Point it at a spec URL or file and every endpoint becomes an MCP tool. Built with FastMCP.

## Code Style
- Python 3.11+
- Follow existing patterns — parser, loader, executor are separate modules
- Use type hints on all public functions

## Architecture
- `loader.py` — fetches and parses YAML/JSON specs (URL or file)
- `parser.py` — extracts endpoints, resolves relative server URLs
- `executor.py` — makes HTTP calls using parsed endpoint metadata
- `server.py` — registers FastMCP tools dynamically using `make_handler` closure pattern

## Key Invariant
- Tools use a single `arguments: str = "{}"` JSON parameter — NOT `**kwargs`
- FastMCP does not support `**kwargs` handlers; this pattern must be preserved

## Testing
- Run tests before committing: `pytest`
- Integration tests use the Petstore demo API — ensure relative URL resolution works

## Commits
- Use conventional commits: `feat:`, `fix:`, `chore:`, `docs:`
- No WIP commits to main

## What NOT to do
- Do not switch to `**kwargs` in tool handlers — this breaks FastMCP
- Do not hardcode base URLs — always resolve from the spec
