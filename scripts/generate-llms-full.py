#!/usr/bin/env python3
"""Generate a custom llms-full.txt from Mintlify MDX sources.

Mintlify's automatic llms-full.txt can emit framework-specific code fence
metadata. A custom root llms-full.txt overrides that output while preserving
normal Markdown code fences for LLM and agent consumers.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
DOCS_JSON = ROOT / "docs.json"
OUTPUT = ROOT / "llms-full.txt"
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


def main() -> None:
    config = json.loads(DOCS_JSON.read_text(encoding="utf-8"))
    sections = [page_to_markdown(page) for page in navigation_pages(config)]
    content = "# Lensmor API Documentation\n\n"
    content += "This file is generated from the public Mintlify MDX sources for LLM and agent consumption.\n"
    content += "It intentionally uses plain Markdown code fences without Mintlify-generated theme metadata.\n\n"
    content += "\n---\n\n".join(sections).rstrip() + "\n"
    OUTPUT.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
