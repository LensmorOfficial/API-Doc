#!/usr/bin/env python3
"""Sync public static assets derived from the Mintlify docs source."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
DOCS_JSON = ROOT / "docs.json"
OPENAPI_SOURCE = ROOT / "api-reference" / "openapi.json"
OPENAPI_ROOT = ROOT / "openapi.json"
API_CATALOG = ROOT / "api-catalog.json"
LLMS_INDEX = ROOT / "llms.txt"
LLMS_FULL = ROOT / "llms-full.txt"
DOCS_BASE_URL = "https://api.lensmor.com"
API_BASE_URL = "https://platform.lensmor.com"
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
TITLE_RE = re.compile(r"^title:\s*(.+?)\s*$", re.MULTILINE)


def iter_pages(node: Any) -> Iterable[str]:
    if isinstance(node, str):
        yield node
        return
    if isinstance(node, dict):
        for page in node.get("pages", []):
            yield from iter_pages(page)


def navigation_pages(config: dict[str, Any]) -> list[str]:
    pages: list[str] = []
    for tab in config.get("navigation", {}).get("tabs", []):
        for group in tab.get("groups", []):
            for page in group.get("pages", []):
                pages.extend(iter_pages(page))
    return pages


def parse_frontmatter(raw: str) -> tuple[str | None, str]:
    match = FRONTMATTER_RE.match(raw)
    if not match:
        return None, raw
    frontmatter = match.group(1)
    body = raw[match.end():]
    title_match = TITLE_RE.search(frontmatter)
    if not title_match:
        return None, body
    title = title_match.group(1).strip().strip('"').strip("'")
    return title, body


def page_to_markdown(page: str) -> str:
    path = ROOT / f"{page}.mdx"
    raw = path.read_text(encoding="utf-8")
    title, body = parse_frontmatter(raw)
    if title is None:
        title = page.replace("-", " ").replace("/", " / ").title()
    body = body.strip()
    return f"## {title}\n\nSource: /{page}\n\n{body}\n"


def sync_openapi_root() -> None:
    shutil.copyfile(OPENAPI_SOURCE, OPENAPI_ROOT)


def sync_api_catalog() -> None:
    API_CATALOG.parent.mkdir(parents=True, exist_ok=True)
    catalog = {
        "apis": [
            {
                "name": "Lensmor API",
                "description": "Customer-facing Lensmor Event Intelligence API.",
                "baseUrl": API_BASE_URL,
                "openapi": f"{DOCS_BASE_URL}/openapi.json",
            }
        ]
    }
    API_CATALOG.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")


def sync_llms_index() -> None:
    content = f"""# Lensmor API Documentation

> Customer-facing Lensmor Event Intelligence API documentation for event discovery, exhibitor research, personnel lookup, credits, and profile matching.

## Primary Resources

- [Full documentation export]({DOCS_BASE_URL}/llms-full.txt)
- [OpenAPI specification]({DOCS_BASE_URL}/openapi.json)
- [API catalog]({DOCS_BASE_URL}/api-catalog.json)

## API Base URL

`{API_BASE_URL}`

All public API paths are under `/external/*` and require `Authorization: Bearer uak_your_api_key`.
"""
    LLMS_INDEX.write_text(content, encoding="utf-8")


def sync_llms_full() -> None:
    config = json.loads(DOCS_JSON.read_text(encoding="utf-8"))
    sections = [page_to_markdown(page) for page in navigation_pages(config)]
    content = "# Lensmor API Documentation\n\n"
    content += "This file is generated from the public Mintlify MDX sources for LLM and agent consumption.\n"
    content += "It intentionally uses plain Markdown code fences without Mintlify-specific metadata.\n\n"
    content += "\n---\n\n".join(sections).rstrip() + "\n"
    LLMS_FULL.write_text(content, encoding="utf-8")


def main() -> None:
    sync_openapi_root()
    sync_api_catalog()
    sync_llms_index()
    sync_llms_full()


if __name__ == "__main__":
    main()
