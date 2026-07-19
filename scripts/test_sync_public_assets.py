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
