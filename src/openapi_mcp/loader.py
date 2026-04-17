from pathlib import Path
from typing import Any

import httpx
import yaml


def load_spec(source: str) -> dict[str, Any]:
    """Load an OpenAPI spec from a URL or file path. Returns parsed dict."""
    if source.startswith("http://") or source.startswith("https://"):
        resp = httpx.get(source, timeout=15, follow_redirects=True)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        if "yaml" in content_type or source.endswith((".yaml", ".yml")):
            return yaml.safe_load(resp.text)
        return resp.json()
    else:
        text = Path(source).read_text()
        if source.endswith((".yaml", ".yml")):
            return yaml.safe_load(text)
        import json
        return json.loads(text)
