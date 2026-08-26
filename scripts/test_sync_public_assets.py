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
    ("GET", "/external/personnel/events/by-name"),
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

    def test_all_api_reference_pages_have_in_depth_field_documentation(self) -> None:
        spec = json.loads(self.sync.OPENAPI_SOURCE.read_text(encoding="utf-8"))

        def iter_schema_properties(schema: object):
            if isinstance(schema, list):
                for item in schema:
                    yield from iter_schema_properties(item)
                return
            if not isinstance(schema, dict):
                return
            for name, child in schema.get("properties", {}).items():
                yield name, child
                yield from iter_schema_properties(child)
            for keyword in ("items", "allOf", "oneOf", "anyOf"):
                if keyword in schema:
                    yield from iter_schema_properties(schema[keyword])

        unbalanced_operation_descriptions: list[str] = []
        undocumented_parameters: list[str] = []
        undocumented_request_fields: list[str] = []

        for path, path_item in spec["paths"].items():
            for method, operation in path_item.items():
                if method.lower() not in self.sync.HTTP_METHODS:
                    continue
                label = f"{method.upper()} {path}"
                description_length = len(operation.get("description", "").strip())
                if not 600 <= description_length <= 750:
                    unbalanced_operation_descriptions.append(
                        f"{label}: {description_length} characters"
                    )

                for parameter in operation.get("parameters", []):
                    if "$ref" in parameter:
                        parameter = spec["components"]["parameters"][
                            parameter["$ref"].rsplit("/", 1)[-1]
                        ]
                    if not parameter.get("description", "").strip() or "example" not in parameter:
                        undocumented_parameters.append(f"{label}: {parameter.get('name')}")

                request_body = operation.get("requestBody")
                if not request_body:
                    continue
                if "$ref" in request_body:
                    request_body = spec["components"]["requestBodies"][
                        request_body["$ref"].rsplit("/", 1)[-1]
                    ]
                schema = request_body["content"]["application/json"]["schema"]
                if "$ref" in schema:
                    schema = spec["components"]["schemas"][schema["$ref"].rsplit("/", 1)[-1]]
                for name, field in iter_schema_properties(schema):
                    if not field.get("description", "").strip():
                        undocumented_request_fields.append(f"{label}: {name}")

        undocumented_schema_fields: list[str] = []
        for schema_name, schema in spec["components"]["schemas"].items():
            for field_name, field in iter_schema_properties(schema):
                if not field.get("description", "").strip():
                    undocumented_schema_fields.append(f"{schema_name}.{field_name}")

        shared_errors_without_examples = [
            name
            for name, response in spec["components"]["responses"].items()
            if "example" not in response.get("content", {}).get("application/json", {})
        ]

        self.assertEqual(unbalanced_operation_descriptions, [])
        self.assertEqual(undocumented_parameters, [])
        self.assertEqual(undocumented_request_fields, [])
        self.assertEqual(undocumented_schema_fields, [])
        self.assertEqual(shared_errors_without_examples, [])

    def test_company_search_contract_matches_current_credit_rule(self) -> None:
        spec = json.loads(self.sync.OPENAPI_SOURCE.read_text(encoding="utf-8"))
        self.assertEqual(spec["info"]["version"], "0.26.0")

        by_name = spec["paths"]["/external/personnel/events/by-name"]["get"]
        self.assertIn("up to 50 personnel records", by_name["description"])
        self.assertIn("10 requests", by_name["description"])
        self.assertEqual(
            by_name["responses"]["200"]["content"]["application/json"]["schema"]["oneOf"][0]["$ref"],
            "#/components/schemas/EventPage",
        )
        by_name_200_refs = {
            item["$ref"]
            for item in by_name["responses"]["200"]["content"]["application/json"]["schema"]["oneOf"]
        }
        self.assertIn("#/components/schemas/FeatureUnavailableBusinessError", by_name_200_refs)
        self.assertIn("#/components/schemas/ConcurrencyLimitBusinessError", by_name_200_refs)
        self.assertEqual(
            by_name["responses"]["200"]["content"]["application/json"]["examples"]
            ["concurrencyLimitExceeded"]["value"]["errorKey"],
            "USER_CONCURRENCY_LIMIT_EXCEEDED",
        )
        self.assertEqual(
            by_name["responses"]["200"]["content"]["application/json"]["examples"]
            ["featureUnavailable"]["value"]["errorKey"],
            "USER_HAS_NO_FEATURE",
        )
        self.assertTrue({"400", "401", "402", "403", "429"}.issubset(by_name["responses"]))
        self.assertIn(
            "search_personnel_events_by_name",
            spec["components"]["schemas"]["ActionPrecheckRequest"]["properties"]
            ["action_type"]["examples"],
        )

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
        self.assertEqual(
            event_search["responses"]["200"]["content"]["application/json"]["schema"]["$ref"],
            "#/components/schemas/ConcurrencyLimitBusinessError",
        )
        event_search_fields = request_bodies["SearchEventsByCompanyNameBody"]["content"][
            "application/json"
        ]["schema"]["properties"]
        self.assertEqual(event_search_fields["sponsor_match_starred"]["enum"], [0, 1])

        event_fields = schemas["EventItem"]["properties"]
        self.assertEqual(event_fields["dataSource"]["const"], "Lensmor")
        self.assertEqual(event_fields["sponsorMatchStarred"]["enum"], [0, 1])
        self.assertEqual(event_fields["hasVisitors"]["type"], "boolean")
        self.assertIn("availability signal", event_fields["hasVisitors"]["description"])

        event_list = spec["paths"]["/external/events/list"]["get"]
        event_list_parameter_names = [
            parameter.get("name")
            for parameter in event_list["parameters"]
            if "$ref" not in parameter
        ]
        self.assertIn("has_visitors", event_list_parameter_names)
        self.assertIn("sponsor_match_starred", event_list_parameter_names)
        event_list_parameters = {
            parameter.get("name"): parameter
            for parameter in event_list["parameters"]
            if "$ref" not in parameter
        }
        self.assertEqual(event_list_parameters["has_visitors"]["schema"]["enum"], [0, 1])
        self.assertEqual(
            event_list_parameters["sponsor_match_starred"]["schema"]["enum"],
            [0, 1],
        )
        self.assertTrue(
            event_list["responses"]["200"]["content"]["application/json"]["example"]["items"][0][
                "hasVisitors"
            ]
        )
        self.assertTrue(
            spec["paths"]["/external/events/{id}"]["get"]["responses"]["200"]["content"]
            ["application/json"]["example"]["event"]["hasVisitors"]
        )

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
        paths = spec["paths"]

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
        for task_field in ("task_id", "job_id"):
            self.assertEqual(
                unlock_submission["properties"][task_field]["pattern"],
                "^[0-9]+$",
            )

        email_unlock = paths["/external/contacts/unlock"]["post"]
        email_request = email_unlock["requestBody"]["content"]["application/json"]["schema"]
        self.assertEqual(email_request["required"], ["personnel_ids"])
        self.assertEqual(email_request["properties"]["personnel_ids"]["maxItems"], 2000)

        for schema_name in (
            "PhoneUnlockRequest",
            "LinkedinActivityUnlockRequest",
            "OutreachMessageRequest",
        ):
            with self.subTest(schema=schema_name):
                request_schema = schemas[schema_name]
                self.assertNotIn("event_id", request_schema["required"])
                self.assertEqual(
                    request_schema["properties"]["personnel_ids"]["maxItems"],
                    2000,
                )

        batch_operations = (
            email_unlock,
            paths["/external/contacts/unlock-phone"]["post"],
            paths["/external/personnel/unlock-linkedin-activity"]["post"],
            paths["/external/personnel/generate-outreach-message"]["post"],
        )
        for operation in batch_operations:
            self.assertIn("422", operation["responses"])

        outreach_request_fields = schemas["OutreachMessageRequest"]["properties"]
        self.assertEqual(
            outreach_request_fields["linkedin_message_types"]["items"]["enum"],
            ["inmail", "connection_note", "connected_message"],
        )
        outreach_message_fields = schemas["OutreachDetail"]["properties"]["messages"][
            "properties"
        ]
        self.assertIn("linkedin", outreach_message_fields)
        outreach_operation = paths["/external/personnel/generate-outreach-message"]["post"]
        self.assertNotIn("402", outreach_operation["responses"])
        self.assertIn("409", outreach_operation["responses"])
        self.assertIn("details", schemas["ApiError"]["properties"])
        self.assertEqual(outreach_request_fields["event_id"]["pattern"], "^[0-9]+$")
        self.assertIn("internal Lensmor event row identifier", outreach_request_fields["event_id"]["description"])
        self.assertNotIn("minItems", outreach_request_fields["personnel_ids"])
        self.assertNotIn("minItems", outreach_request_fields["channels"])
        outreach_response = schemas["OutreachMessageResponse"]["properties"]
        self.assertEqual(outreach_response["taskCenterId"]["pattern"], "^[0-9]+$")
        self.assertEqual(
            outreach_response["items"]["items"]["properties"]["taskId"]["pattern"],
            "^[0-9]+$",
        )
        self.assertIsNone(
            outreach_operation["responses"]["201"]["content"]["application/json"]["example"]
            ["items"][0]["taskId"]
        )
        outreach_detail = paths["/external/personnel/outreach"]["get"]
        self.assertIn("400", outreach_detail["responses"])
        self.assertNotIn("404", outreach_detail["responses"])

    def test_numeric_task_ids_match_bigint_runtime_contracts(self) -> None:
        spec = json.loads(self.sync.OPENAPI_SOURCE.read_text(encoding="utf-8"))
        paths = spec["paths"]
        schemas = spec["components"]["schemas"]

        phone_poll = paths["/external/contacts/unlock-phone-tasks/{taskId}"]["get"]
        self.assertEqual(phone_poll["parameters"][0]["schema"]["pattern"], "^[0-9]+$")
        self.assertEqual(phone_poll["parameters"][0]["example"], "321")
        self.assertEqual(
            phone_poll["responses"]["200"]["content"]["application/json"]["example"]["taskId"],
            "321",
        )
        phone_submit = paths["/external/contacts/unlock-phone"]["post"]["responses"]["201"]
        phone_submit_example = phone_submit["content"]["application/json"]["example"]
        self.assertEqual(phone_submit_example["task_id"], "321")
        self.assertEqual(phone_submit_example["job_id"], "321")
        self.assertEqual(schemas["PhoneUnlockTask"]["properties"]["taskId"]["pattern"], "^[0-9]+$")

        linkedin = paths["/external/personnel/unlock-linkedin-activity"]["post"]
        self.assertIsNone(
            linkedin["responses"]["201"]["content"]["application/json"]["example"]
            ["items"][0]["taskId"]
        )
        self.assertEqual(
            schemas["LinkedinActivityUnlockItem"]["properties"]["taskId"]["pattern"],
            "^[0-9]+$",
        )

    def test_profile_matching_inherited_input_and_ranked_event_contract(self) -> None:
        spec = json.loads(self.sync.OPENAPI_SOURCE.read_text(encoding="utf-8"))
        request_schema = spec["components"]["requestBodies"]["ProfileMatchingBody"][
            "content"
        ]["application/json"]["schema"]
        fields = request_schema["properties"]
        inherited = {
            "linkedin_url",
            "company_description",
            "industry",
            "target_industry",
            "planned_events",
            "target_management_level",
            "target_job_titles",
            "timeout_ms",
        }
        self.assertTrue(inherited.issubset(fields))
        self.assertEqual(fields["company_url"]["maxLength"], 500)
        self.assertEqual(fields["company_description"]["maxLength"], 2000)
        self.assertEqual(fields["target_job_titles"]["items"]["maxLength"], 255)
        self.assertIn("first five", fields["target_job_titles"]["description"])
        self.assertEqual(fields["timeout_ms"]["minimum"], 60000)
        self.assertEqual(fields["timeout_ms"]["maximum"], 3600000)

        schemas = spec["components"]["schemas"]
        recommended = schemas["ProfileRecommendedEvent"]
        self.assertEqual(recommended["allOf"][0]["$ref"], "#/components/schemas/EventDetail")
        recommendation_fields = recommended["allOf"][1]["properties"]
        self.assertTrue(
            {
                "declaredExpectedAttendees",
                "estimatedExpectedAttendees",
                "quality",
                "sourceTags",
                "visibilityStatus",
                "createTime",
                "updateTime",
                "matched_exhibitor_count",
                "matched_personnel_count",
                "match_score",
                "unlocked",
                "relevanceReason",
                "rank",
            }.issubset(recommendation_fields)
        )
        page_extension = schemas["ProfileEventRecommendationPage"]["allOf"][1]
        self.assertEqual(
            page_extension["properties"]["items"]["items"]["$ref"],
            "#/components/schemas/ProfileRecommendedEvent",
        )
        self.assertEqual(
            page_extension["properties"]["status"]["enum"],
            ["completed", "completed_empty"],
        )

    def test_validation_business_errors_and_examples_match_runtime(self) -> None:
        spec = json.loads(self.sync.OPENAPI_SOURCE.read_text(encoding="utf-8"))
        paths = spec["paths"]
        validation_operations = [
            paths["/external/events/list"]["get"],
            paths["/external/events/{id}"]["get"],
            paths["/external/events/brief"]["get"],
            paths["/external/events/fit-score"]["post"],
            paths["/external/events/rank"]["post"],
            paths["/external/events/{id}/unlock"]["post"],
            paths["/external/exhibitors/list"]["get"],
            paths["/external/exhibitors/profile"]["get"],
            paths["/external/exhibitors/events"]["get"],
            paths["/external/personnel/list"]["get"],
            paths["/external/personnel/profile"]["get"],
            paths["/external/personnel/events"]["get"],
            paths["/external/personnel/events/by-linkedin"]["get"],
            paths["/external/personnel/outreach"]["get"],
            paths["/external/profile-matching/recommendations/exhibitors"]["get"],
        ]
        for operation in validation_operations:
            self.assertIn("400", operation["responses"])
        self.assertIn("409", paths["/external/events/{id}/unlock"]["post"]["responses"])

        search_events_200 = paths["/external/exhibitors/search-events"]["post"]["responses"]["200"]
        self.assertEqual(
            search_events_200["content"]["application/json"]["example"]["errorKey"],
            "USER_CONCURRENCY_LIMIT_EXCEEDED",
        )
        for path in (
            "/external/events/{id}/visitors/unlock",
            "/external/events/{id}/full-access/unlock",
        ):
            self.assertEqual(
                paths[path]["post"]["responses"]["200"]["content"]["application/json"]
                ["example"]["errorKey"],
                "USER_HAS_NO_FEATURE",
            )

        semantics = paths["/external/exhibitors/list"]["get"]["responses"]["200"]["content"]
        self.assertIn("guidance", semantics["application/json"]["example"]["semantics"])
        buying_signal_source = spec["components"]["schemas"]["ExhibitorSignalFields"][
            "properties"
        ]["buyingSignals"]["items"]["properties"]["sourceType"]
        self.assertIn("Buying-signal evidence", buying_signal_source["description"])

        equal_event_ids: list[str] = []

        def find_equal_event_ids(value: object, label: str = "paths") -> None:
            if isinstance(value, list):
                for index, item in enumerate(value):
                    find_equal_event_ids(item, f"{label}[{index}]")
                return
            if not isinstance(value, dict):
                return
            if isinstance(value.get("id"), str) and value.get("id") == value.get("eventId"):
                equal_event_ids.append(label)
            for key, item in value.items():
                find_equal_event_ids(item, f"{label}.{key}")

        find_equal_event_ids(paths)
        self.assertEqual(equal_event_ids, [])

    def test_v024_access_and_balance_contracts(self) -> None:
        spec = json.loads(self.sync.OPENAPI_SOURCE.read_text(encoding="utf-8"))
        schemas = spec["components"]["schemas"]

        action_type_schema = schemas["ActionPrecheckRequest"]["properties"]["action_type"]
        action_types = set(action_type_schema["examples"])
        self.assertTrue(
            {
                "unlock_event_visitors",
                "unlock_event_full_access",
                "unlock_contact_phones",
                "integration_status",
                "integration_export_contacts",
                "integration_export_exhibitors",
            }.issubset(action_types)
        )
        self.assertNotIn("enum", action_type_schema)
        self.assertEqual(action_type_schema["minLength"], 1)
        self.assertEqual(action_type_schema["maxLength"], 100)
        self.assertIn("unsupported_action", action_type_schema["description"])

        visitor_unlock = spec["paths"]["/external/events/{id}/visitors/unlock"]["post"]
        full_access = spec["paths"]["/external/events/{id}/full-access/unlock"]["post"]
        self.assertIn("3,000", visitor_unlock["description"])
        for expected_cost in ("2,000", "3,000", "5,000"):
            self.assertIn(expected_cost, full_access["description"])
        self.assertTrue(
            {"200", "400", "401", "402", "404", "409", "429"}.issubset(
                visitor_unlock["responses"]
            )
        )
        self.assertTrue(
            {"200", "400", "401", "402", "404", "409", "429"}.issubset(
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

        personnel_list = spec["paths"]["/external/personnel/list"]["get"]
        self.assertNotIn("does not currently accept a source filter", personnel_list["description"])
        source_type_parameter = next(
            parameter
            for parameter in personnel_list["parameters"]
            if parameter.get("name") == "sourceType"
        )
        self.assertNotIn("enum", source_type_parameter["schema"])
        self.assertEqual(source_type_parameter["example"], "social,visitors")
        self.assertIn("comma-separated", source_type_parameter["description"])

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
            ROOT / "api-reference-backup" / "personnel" / "events-by-name.mdx",
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
        self.assertIn("2000", page)
        self.assertIn("422 Unprocessable Entity", page)
        self.assertNotIn("A `201 Created` response means the task was accepted", page)

    def test_outreach_prose_matches_zero_credit_runtime(self) -> None:
        page = (
            ROOT / "api-reference-backup" / "personnel" / "generate-outreach-message.mdx"
        ).read_text(encoding="utf-8")

        self.assertIn("does not deduct credits", page)
        self.assertIn("creditsCost: 0", page)
        self.assertNotIn("402 Payment Required", page)

    def test_agent_integrations_are_explicitly_excluded(self) -> None:
        inventory = (
            ROOT / "docs" / "endpoint-inventory" / "external-api-endpoints.md"
        ).read_text(encoding="utf-8")

        self.assertIn("/external/integrations/*", inventory)
        self.assertIn("Agent-only", inventory)
        self.assertIn("/external/personnel/events/by-name", inventory)
        self.assertIn("exactly 31 customer-facing routes", inventory)
        self.assertIn(
            "git@git.ziniao.com:a60-lensmor/service/a60-lensmor-event-business.git",
            inventory,
        )
        self.assertIn("ce54e3e6e18c756ce154f1ba8800bfc89d7ac193", inventory)

    def test_runtime_limit_and_identifier_caveats_are_prominent(self) -> None:
        rate_page = (ROOT / "concepts" / "rate-limits.mdx").read_text(encoding="utf-8")
        self.assertIn("`60` seconds", rate_page)
        self.assertIn("`120` requests per API key", rate_page)
        self.assertIn("`600` requests per IP", rate_page)

        identifiers = (ROOT / "concepts" / "identifiers.mdx").read_text(encoding="utf-8")
        self.assertIn("generate-outreach-message", identifiers)
        self.assertIn("numeric internal event `id`", identifiers)
        outreach_page = (
            ROOT
            / "api-reference-backup"
            / "personnel"
            / "generate-outreach-message.mdx"
        ).read_text(encoding="utf-8")
        self.assertIn("not public `eventId`", outreach_page)

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
