#!/usr/bin/env python3
"""Sync public static assets derived from the Mintlify docs source."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DOCS_JSON = ROOT / "docs.json"
OPENAPI_SOURCE = ROOT / "api-reference" / "openapi.json"
OPENAPI_ROOT = ROOT / "openapi.json"
OPENAPI_BACKUP = ROOT / "api-reference-backup" / "openapi.json"
API_REFERENCE_BACKUP = ROOT / "api-reference-backup"
API_CATALOG = ROOT / "api-catalog.json"
LLMS_INDEX = ROOT / "llms.txt"
LLMS_FULL = ROOT / "llms-full.txt"
DOCS_BASE_URL = "https://api.lensmor.com"
API_BASE_URL = "https://platform.lensmor.com"
HTTP_METHODS = {"get", "post", "put", "patch", "delete"}
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
TITLE_RE = re.compile(r"^title:\s*(.+?)\s*$", re.MULTILINE)
OPENAPI_FRONTMATTER_RE = re.compile(
    r'^openapi:\s*["\']openapi\.json\s+'
    r"(GET|POST|PUT|PATCH|DELETE)\s+([^\"\']+)[\"\']\s*$",
    re.MULTILINE,
)
OPERATION_PAGE_RE = re.compile(r"^(GET|POST|PUT|PATCH|DELETE)\s+(/\S+)$")


@dataclass(frozen=True)
class OperationPage:
    public_path: str
    source_path: Path


def iter_pages(node: Any) -> Iterable[str]:
    if isinstance(node, str):
        yield node
        return
    if isinstance(node, dict):
        for page in node.get("pages", []):
            yield from iter_pages(page)


def navigation_pages(config: dict[str, Any]) -> list[str]:
    indexed_groups: list[tuple[int, dict[str, Any]]] = []
    index = 0
    for tab in config.get("navigation", {}).get("tabs", []):
        for group in tab.get("groups", []):
            indexed_groups.append((index, group))
            index += 1

    def llms_group_order(item: tuple[int, dict[str, Any]]) -> tuple[int, int]:
        original_index, group = item
        name = group.get("group")
        if name == "Introduction":
            return 0, original_index
        if name == "Guides":
            return 1, original_index
        if name == "Concepts":
            return 3, original_index
        return 2, original_index

    pages: list[str] = []
    for _, group in sorted(indexed_groups, key=llms_group_order):
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


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError(f"Unable to create a route slug from {value!r}")
    return slug


def openapi_operation_routes() -> dict[str, str]:
    spec = json.loads(OPENAPI_SOURCE.read_text(encoding="utf-8"))
    operations: dict[str, str] = {}

    for path, path_item in spec.get("paths", {}).items():
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS:
                continue
            summary = operation.get("summary")
            tags = operation.get("tags") or []
            if not summary or not tags:
                raise ValueError(
                    f"{method.upper()} {path} needs a summary and tag for its Mintlify route"
                )
            key = f"{method.upper()} {path}"
            public_path = f"/api-reference/{slugify(tags[0])}/{slugify(summary)}"
            operations[key] = public_path

    return operations


def operation_doc_paths() -> dict[str, Path]:
    docs: dict[str, Path] = {}
    for path in sorted(API_REFERENCE_BACKUP.rglob("*.mdx")):
        raw = path.read_text(encoding="utf-8")
        frontmatter_match = FRONTMATTER_RE.match(raw)
        if not frontmatter_match:
            continue
        openapi_match = OPENAPI_FRONTMATTER_RE.search(frontmatter_match.group(1))
        if not openapi_match:
            continue
        key = f"{openapi_match.group(1)} {openapi_match.group(2).strip()}"
        if key in docs:
            raise ValueError(f"Duplicate OpenAPI documentation page for {key}")
        docs[key] = path
    return docs


def operation_pages() -> dict[str, OperationPage]:
    routes = openapi_operation_routes()
    docs = operation_doc_paths()

    missing_docs = sorted(routes.keys() - docs.keys())
    if missing_docs:
        raise ValueError(
            "OpenAPI operations have no backup MDX page: " + ", ".join(missing_docs)
        )

    unknown_docs = sorted(docs.keys() - routes.keys())
    if unknown_docs:
        raise ValueError(
            "Backup MDX pages reference unknown OpenAPI operations: "
            + ", ".join(unknown_docs)
        )

    return {
        key: OperationPage(public_path=routes[key], source_path=docs[key])
        for key in routes
    }


def resolve_page(
    page: str,
    operations: dict[str, OperationPage],
) -> tuple[Path, str]:
    if OPERATION_PAGE_RE.match(page):
        if page not in operations:
            raise ValueError(f"Navigation references an unknown OpenAPI operation: {page}")
        operation = operations[page]
        return operation.source_path, operation.public_path

    path = ROOT / f"{page}.mdx"
    if not path.exists():
        raise FileNotFoundError(f"Navigation page does not exist: {path}")
    return path, f"/{page}"


def page_to_markdown(
    page: str,
    operations: dict[str, OperationPage],
) -> str:
    path, public_path = resolve_page(page, operations)
    raw = path.read_text(encoding="utf-8")
    title, body = parse_frontmatter(raw)
    if title is None:
        title = page.replace("-", " ").replace("/", " / ").title()
    body = body.strip()
    return f"## {title}\n\nSource: {public_path}\n\n{body}\n"


def expected_legacy_redirects() -> list[dict[str, Any]]:
    operations = operation_pages()
    redirects: list[dict[str, Any]] = []

    for operation in operations.values():
        relative = (
            operation.source_path.relative_to(API_REFERENCE_BACKUP)
            .with_suffix("")
            .as_posix()
        )
        source = f"/api-reference/{relative}"
        destination = operation.public_path
        if source != destination:
            redirects.append(
                {"source": source, "destination": destination, "permanent": True}
            )

    return sorted(redirects, key=lambda redirect: redirect["source"])


def missing_legacy_redirects() -> list[dict[str, Any]]:
    config = json.loads(DOCS_JSON.read_text(encoding="utf-8"))
    configured = {
        (
            redirect.get("source"),
            redirect.get("destination"),
            redirect.get("permanent", False),
        )
        for redirect in config.get("redirects", [])
    }
    return [
        redirect
        for redirect in expected_legacy_redirects()
        if (
            redirect["source"],
            redirect["destination"],
            redirect["permanent"],
        )
        not in configured
    ]


def render_api_catalog() -> str:
    catalog = {
        "apis": [
            {
                "name": "Lensmor API",
                "description": "Lensmor Event Intelligence API.",
                "baseUrl": API_BASE_URL,
                "openapi": f"{DOCS_BASE_URL}/openapi.json",
            }
        ]
    }
    return json.dumps(catalog, indent=2) + "\n"


def render_llms_index() -> str:
    return f"""# Lensmor API Documentation

> Lensmor Event Intelligence API documentation for event discovery, exhibitor research, personnel lookup, credits, and profile matching.

## Primary Resources

- [Full documentation export]({DOCS_BASE_URL}/llms-full.txt)
- [OpenAPI specification]({DOCS_BASE_URL}/openapi.json)
- [API catalog]({DOCS_BASE_URL}/api-catalog.json)

## API Base URL

`{API_BASE_URL}`

Send requests to `{API_BASE_URL}` with `Authorization: Bearer sk_your_api_key`.
"""


def render_llms_full() -> str:
    config = json.loads(DOCS_JSON.read_text(encoding="utf-8"))
    operations = operation_pages()
    sections = [
        page_to_markdown(page, operations)
        for page in navigation_pages(config)
    ]
    content = "# Lensmor API Documentation\n\n"
    content += "This file is generated from the public Mintlify MDX sources for LLM and agent consumption.\n"
    content += "It intentionally uses plain Markdown code fences without Mintlify-specific metadata.\n\n"
    content += "\n---\n\n".join(sections).rstrip() + "\n"
    return content


def build_outputs() -> dict[Path, bytes]:
    openapi = OPENAPI_SOURCE.read_bytes()
    return {
        OPENAPI_ROOT: openapi,
        OPENAPI_BACKUP: openapi,
        API_CATALOG: render_api_catalog().encode("utf-8"),
        LLMS_INDEX: render_llms_index().encode("utf-8"),
        LLMS_FULL: render_llms_full().encode("utf-8"),
    }


def sync_public_assets(check: bool = False) -> int:
    missing_redirects = missing_legacy_redirects()
    if missing_redirects:
        print("Missing permanent redirects for legacy API reference routes:")
        for redirect in missing_redirects:
            print(f"- {redirect['source']} -> {redirect['destination']}")
        return 1

    stale: list[Path] = []
    for path, expected in build_outputs().items():
        actual = path.read_bytes() if path.exists() else None
        if actual == expected:
            continue
        stale.append(path)
        if not check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(expected)
            print(f"Updated {path.relative_to(ROOT)}")

    if check and stale:
        print("Generated public assets are stale:")
        for path in stale:
            print(f"- {path.relative_to(ROOT)}")
        return 1

    if check:
        print("Generated public assets are up to date.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero when generated assets or legacy redirects are stale.",
    )
    args = parser.parse_args()
    return sync_public_assets(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
