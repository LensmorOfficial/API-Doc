#!/usr/bin/env python3
"""Regression tests for generated Lensmor API documentation assets."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "sync-public-assets.py"


def load_sync_module():
    spec = importlib.util.spec_from_file_location("sync_public_assets", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PublicAssetSyncTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sync = load_sync_module()

    def test_generated_openapi_artifacts_are_identical(self) -> None:
        outputs = self.sync.build_outputs()
        source = self.sync.OPENAPI_SOURCE.read_bytes()

        self.assertEqual(outputs[self.sync.OPENAPI_ROOT], source)
        self.assertEqual(outputs[self.sync.OPENAPI_BACKUP], source)

    def test_public_openapi_has_descriptions_and_examples(self) -> None:
        spec = json.loads(self.sync.OPENAPI_SOURCE.read_text(encoding="utf-8"))
        operations: list[tuple[str, str, dict]] = []
        for path, path_item in spec["paths"].items():
            for method, operation in path_item.items():
                if method.lower() in self.sync.HTTP_METHODS:
                    operations.append((method.upper(), path, operation))

        self.assertEqual(len(operations), 28)
        self.assertFalse(
            any(path.startswith("/external/integrations/") for _, path, _ in operations)
        )
        self.assertTrue(spec["info"]["license"]["name"].strip())
        self.assertEqual(
            [tag["name"] for tag in spec["tags"] if not tag.get("description", "").strip()],
            [],
        )

        missing_descriptions: list[str] = []
        missing_request_examples: list[str] = []
        missing_response_examples: list[str] = []

        for method, path, operation in operations:
            label = f"{method} {path}"
            if not operation.get("description", "").strip():
                missing_descriptions.append(label)

            request_body = operation.get("requestBody")
            if request_body:
                if "$ref" in request_body:
                    request_body = spec["components"]["requestBodies"][
                        request_body["$ref"].rsplit("/", 1)[-1]
                    ]
                media = request_body.get("content", {}).get("application/json", {})
                if "example" not in media and "examples" not in media:
                    missing_request_examples.append(label)

            success_responses = [
                response
                for status, response in operation["responses"].items()
                if status.startswith("2")
            ]
            has_example = False
            for response in success_responses:
                if "$ref" in response:
                    response = spec["components"]["responses"][response["$ref"].rsplit("/", 1)[-1]]
                media = response.get("content", {}).get("application/json", {})
                if "example" in media or "examples" in media:
                    has_example = True
            if not has_example:
                missing_response_examples.append(label)

        self.assertEqual(missing_descriptions, [])
        self.assertEqual(missing_request_examples, [])
        self.assertEqual(missing_response_examples, [])

    def test_agent_integrations_are_explicitly_excluded(self) -> None:
        inventory = (
            ROOT / "docs" / "endpoint-inventory" / "external-api-endpoints.md"
        ).read_text(encoding="utf-8")

        self.assertIn("/external/integrations/*", inventory)
        self.assertIn("Agent-only", inventory)

    def test_llms_full_covers_every_navigation_entry(self) -> None:
        outputs = self.sync.build_outputs()
        llms_full = outputs[self.sync.LLMS_FULL].decode("utf-8")
        sources = [
            line.removeprefix("Source: ")
            for line in llms_full.splitlines()
            if line.startswith("Source: ")
        ]
        config = json.loads(self.sync.DOCS_JSON.read_text(encoding="utf-8"))
        expected_pages = self.sync.navigation_pages(config)
        expected_api_pages = self.sync.openapi_operation_routes()

        self.assertEqual(len(sources), len(expected_pages))
        self.assertEqual(
            len([source for source in sources if source.startswith("/api-reference/")]),
            len(expected_api_pages),
        )
        self.assertEqual(len(sources), len(set(sources)))

    def test_legacy_api_routes_have_permanent_redirects(self) -> None:
        missing = self.sync.missing_legacy_redirects()
        self.assertEqual(missing, [])

    def test_llms_full_has_no_known_truncated_fragments(self) -> None:
        outputs = self.sync.build_outputs()
        llms_full = outputs[self.sync.LLMS_FULL].decode("utf-8")

        for fragment in ("guaubmitted", "taskot create", "completaskStatus"):
            with self.subTest(fragment=fragment):
                self.assertFalse(
                    fragment in llms_full,
                    f"Generated llms-full.txt contains truncated fragment: {fragment}",
                )

    def test_internal_api_reference_links_target_generated_routes(self) -> None:
        valid_routes = set(self.sync.openapi_operation_routes().values())

        public_sources = [
            ROOT / "index.mdx",
            *sorted((ROOT / "guides").rglob("*.mdx")),
            *sorted((ROOT / "concepts").rglob("*.mdx")),
            *sorted((ROOT / "api-reference-backup").rglob("*.mdx")),
        ]
        invalid: list[str] = []
        link_pattern = re.compile(r"/api-reference/[A-Za-z0-9/_-]+")
        for path in public_sources:
            for link in link_pattern.findall(path.read_text(encoding="utf-8")):
                if link not in valid_routes:
                    invalid.append(f"{path.relative_to(ROOT)}: {link}")

        self.assertEqual(invalid, [])

    def test_check_mode_is_clean_and_read_only(self) -> None:
        tracked_outputs = [
            self.sync.OPENAPI_ROOT,
            self.sync.OPENAPI_BACKUP,
            self.sync.API_CATALOG,
            self.sync.LLMS_INDEX,
            self.sync.LLMS_FULL,
        ]
        before = {path: path.read_bytes() for path in tracked_outputs}
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--check"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        after = {path: path.read_bytes() for path in tracked_outputs}

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
