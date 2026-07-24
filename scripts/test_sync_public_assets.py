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
EXPECTED_PUBLIC_OPERATIONS = {
    ("GET", "/external/credits/balance"),
    ("POST", "/external/actions/precheck"),
    ("GET", "/external/events/list"),
    ("GET", "/external/events/{id}"),
    ("GET", "/external/events/brief"),
    ("POST", "/external/events/fit-score"),
    ("POST", "/external/events/rank"),
    ("POST", "/external/events/{id}/unlock"),
    ("POST", "/external/events/{id}/visitors/unlock"),
    ("POST", "/external/events/{id}/full-access/unlock"),
    ("GET", "/external/exhibitors/list"),
    ("POST", "/external/exhibitors/search"),
    ("POST", "/external/exhibitors/search-by-company-name"),
    ("POST", "/external/exhibitors/search-events"),
    ("GET", "/external/exhibitors/profile"),
    ("GET", "/external/exhibitors/events"),
    ("GET", "/external/personnel/list"),
    ("GET", "/external/personnel/profile"),
    ("GET", "/external/personnel/events"),
    ("GET", "/external/personnel/events/by-linkedin"),
    ("POST", "/external/personnel/unlock-linkedin-activity"),
    ("POST", "/external/personnel/generate-outreach-message"),
    ("GET", "/external/personnel/outreach"),
    ("GET", "/external/contacts/search"),
    ("POST", "/external/contacts/unlock"),
    ("GET", "/external/contacts/unlock-tasks/{taskId}"),
    ("POST", "/external/contacts/unlock-phone"),
    ("GET", "/external/contacts/unlock-phone-tasks/{taskId}"),
    ("POST", "/external/profile-matching/actions/apply-recommended-events/paged"),
    ("GET", "/external/profile-matching/recommendations/exhibitors"),
}


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

        self.assertEqual(
            {(method, path) for method, path, _ in operations},
            EXPECTED_PUBLIC_OPERATIONS,
        )
        self.assertFalse(
            any(path.startswith("/external/integrations/") for _, path, _ in operations)
        )
        self.assertFalse(
            any(path.startswith("/external/agent-files/") for _, path, _ in operations)
        )
        self.assertFalse(
            any(path.startswith("/external/debug/") for _, path, _ in operations)
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

    def test_company_search_contract_matches_current_credit_rule(self) -> None:
        spec = json.loads(self.sync.OPENAPI_SOURCE.read_text(encoding="utf-8"))
        self.assertEqual(spec["info"]["version"], "0.24.1")

        company_search = spec["paths"]["/external/exhibitors/search-by-company-name"]["post"]
        self.assertIn("non-empty", company_search["description"])
        self.assertIn("402", company_search["responses"])

    def test_event_search_and_event_item_contracts(self) -> None:
        spec = json.loads(self.sync.OPENAPI_SOURCE.read_text(encoding="utf-8"))
        schemas = spec["components"]["schemas"]
        request_bodies = spec["components"]["requestBodies"]

        event_search = spec["paths"]["/external/exhibitors/search-events"]["post"]
        self.assertEqual(
            event_search["requestBody"]["$ref"],
            "#/components/requestBodies/SearchEventsByCompanyNameBody",
        )
        self.assertEqual(
            event_search["responses"]["201"]["content"]["application/json"]["schema"]["$ref"],
            "#/components/schemas/EventReverseSearchPage",
        )
        event_search_fields = request_bodies["SearchEventsByCompanyNameBody"]["content"][
            "application/json"
        ]["schema"]["properties"]
        self.assertEqual(event_search_fields["sponsor_match_starred"]["enum"], [0, 1])

        event_fields = schemas["EventItem"]["properties"]
        self.assertEqual(event_fields["dataSource"]["const"], "Lensmor")
        self.assertEqual(event_fields["sponsorMatchStarred"]["enum"], [0, 1])

        event_examples = [
            spec["paths"]["/external/events/list"]["get"]["responses"]["200"]["content"]
            ["application/json"]["example"]["items"][0],
            spec["paths"]["/external/events/{id}"]["get"]["responses"]["200"]["content"]
            ["application/json"]["example"]["event"],
            spec["paths"]["/external/events/brief"]["get"]["responses"]["200"]["content"]
            ["application/json"]["example"]["event"],
            spec["paths"]["/external/events/fit-score"]["post"]["responses"]["201"]
            ["content"]["application/json"]["example"]["event"],
        ]
        for example in event_examples:
            with self.subTest(event=example["eventId"]):
                self.assertIn(example["sponsorMatchStarred"], [0, 1])
                self.assertEqual(example["dataSource"], "Lensmor")

    def test_contact_unlock_and_outreach_contracts(self) -> None:
        spec = json.loads(self.sync.OPENAPI_SOURCE.read_text(encoding="utf-8"))
        schemas = spec["components"]["schemas"]

        contact_fields = schemas["ContactItem"]["properties"]
        self.assertTrue(
            {
                "phone",
                "phoneUnlockStatus",
                "eventCount",
                "outreachMessageStatus",
                "outreachMessageChannels",
            }.issubset(contact_fields)
        )

        unlock_submission = schemas["ContactUnlockSubmission"]
        self.assertEqual(unlock_submission["properties"]["status"]["enum"], ["accepted", "success"])
        self.assertIn("skipped_personnel_ids", unlock_submission["properties"])
        self.assertIn("skipped_detail", unlock_submission["properties"])

        outreach_request_fields = schemas["OutreachMessageRequest"]["properties"]
        self.assertEqual(
            outreach_request_fields["linkedin_message_types"]["items"]["enum"],
            ["inmail", "connection_note", "connected_message"],
        )
        outreach_message_fields = schemas["OutreachDetail"]["properties"]["messages"][
            "properties"
        ]
        self.assertIn("linkedin", outreach_message_fields)

    def test_v024_access_and_balance_contracts(self) -> None:
        spec = json.loads(self.sync.OPENAPI_SOURCE.read_text(encoding="utf-8"))
        schemas = spec["components"]["schemas"]

        action_types = set(
            schemas["ActionPrecheckRequest"]["properties"]["action_type"]["enum"]
        )
        self.assertTrue(
            {
                "unlock_event_visitors",
                "unlock_event_full_access",
                "unlock_contact_phones",
            }.issubset(action_types)
        )

        visitor_unlock = spec["paths"]["/external/events/{id}/visitors/unlock"]["post"]
        full_access = spec["paths"]["/external/events/{id}/full-access/unlock"]["post"]
        self.assertIn("3,000", visitor_unlock["description"])
        for expected_cost in ("2,000", "3,000", "5,000"):
            self.assertIn(expected_cost, full_access["description"])
        self.assertTrue(
            {"400", "401", "402", "404", "409", "429"}.issubset(
                visitor_unlock["responses"]
            )
        )
        self.assertTrue(
            {"400", "401", "402", "404", "409", "429"}.issubset(
                full_access["responses"]
            )
        )

        self.assertEqual(
            set(schemas["EventFullAccessUnlockResult"]["required"]),
            {
                "success",
                "alreadyUnlocked",
                "eventUnlocked",
                "visitorUnlocked",
                "visitorSkipped",
                "totalCreditsUsed",
                "balanceAfter",
                "event",
            },
        )

        credit_fields = schemas["CreditBalance"]["properties"]
        self.assertTrue(
            {"addonAmount", "addonBalance", "addonExpireAt"}.issubset(credit_fields)
        )

        source_type = schemas["ContactItem"]["properties"]["sourceType"]
        self.assertEqual(source_type["type"], "array")
        self.assertEqual(
            source_type["items"]["enum"],
            ["exhibitor", "social", "visitors"],
        )
        self.assertIn("not mutually exclusive", source_type["description"])

        source_examples = [
            spec["paths"]["/external/personnel/list"]["get"]["responses"]["200"]
            ["content"]["application/json"]["example"]["items"][0]["sourceType"],
            spec["paths"]["/external/personnel/profile"]["get"]["responses"]["200"]
            ["content"]["application/json"]["example"]["sourceType"],
            spec["paths"]["/external/contacts/search"]["get"]["responses"]["200"]
            ["content"]["application/json"]["example"]["items"][0]["sourceType"],
        ]
        for example in source_examples:
            with self.subTest(example=example):
                self.assertTrue(example)
                self.assertTrue(set(example).issubset({"exhibitor", "social", "visitors"}))

        for page_name in (
            "unlock-event-visitor-access.mdx",
            "unlock-full-event-access.mdx",
        ):
            page = (
                ROOT / "api-reference-backup" / "events" / page_name
            ).read_text(encoding="utf-8")
            self.assertIn("Actions precheck", page)
            self.assertIn("idempotency", page.lower())

    def test_event_prose_uses_the_public_event_shape(self) -> None:
        event_pages = [
            ROOT / "api-reference-backup" / "events" / "list.mdx",
            ROOT / "api-reference-backup" / "events" / "detail.mdx",
            ROOT / "api-reference-backup" / "exhibitors" / "events.mdx",
            ROOT
            / "api-reference-backup"
            / "profile-matching"
            / "actions-apply-recommended-events-paged.mdx",
            ROOT / "api-reference-backup" / "personnel" / "events.mdx",
            ROOT / "api-reference-backup" / "personnel" / "events-by-linkedin.mdx",
        ]

        for path in event_pages:
            with self.subTest(path=path.relative_to(ROOT)):
                page = path.read_text(encoding="utf-8")
                self.assertIn("sponsorMatchStarred", page)
                self.assertIn("Always `Lensmor`", page)
                self.assertNotIn('"dataSource": "database"', page)
                self.assertNotIn('"local_import"', page)

    def test_personnel_prose_matches_endpoint_specific_shapes(self) -> None:
        profile_page = (
            ROOT / "api-reference-backup" / "personnel" / "profile.mdx"
        ).read_text(encoding="utf-8")
        linkedin_events_page = (
            ROOT / "api-reference-backup" / "personnel" / "events-by-linkedin.mdx"
        ).read_text(encoding="utf-8")

        self.assertNotIn("outreachMessageStatus", profile_page)
        self.assertNotIn("outreachMessageChannels", profile_page)
        for field in ("phone", "phoneUnlockStatus", "eventCount"):
            with self.subTest(field=field):
                self.assertIn(field, linkedin_events_page)

    def test_phone_unlock_prose_handles_accepted_and_no_work_success(self) -> None:
        page = (
            ROOT / "api-reference-backup" / "contacts" / "unlock-phone.mdx"
        ).read_text(encoding="utf-8")

        self.assertIn('status: "accepted"', page)
        self.assertIn('status: "success"', page)
        self.assertIn("there is nothing to poll", page)
        self.assertIn("Only poll", page)
        self.assertNotIn("A `201 Created` response means the task was accepted", page)

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
            line[len("Source: "):]
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

    def test_multilingual_navigation_has_unique_existing_pages(self) -> None:
        config = json.loads(self.sync.DOCS_JSON.read_text(encoding="utf-8"))
        languages = config["navigation"]["languages"]

        self.assertEqual(languages[0]["language"], "en")
        self.assertTrue(languages[0]["default"])
        self.assertEqual(languages[1]["language"], "zh-Hans")

        all_pages: list[str] = []
        for language in languages:
            for tab in language.get("tabs", []):
                for group in tab.get("groups", []):
                    for page in group.get("pages", []):
                        if self.sync.OPERATION_PAGE_RE.match(page):
                            continue
                        all_pages.extend(self.sync.iter_pages(page))

        self.assertEqual(len(all_pages), len(set(all_pages)))
        for page in all_pages:
            with self.subTest(page=page):
                self.assertTrue((ROOT / f"{page}.mdx").exists())

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
            *sorted((ROOT / "zh-Hans").rglob("*.mdx")),
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
