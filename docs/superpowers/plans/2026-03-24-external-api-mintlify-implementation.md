# External API Mintlify Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Initialize `API-Doc` as a Mintlify docs site and publish the currently implemented `external/*` endpoints from `a60-lensmor-event-business` as developer-facing API reference pages, while updating PM external API docs to match implemented behavior.

**Architecture:** Use a code-first documentation pipeline. First create a committed endpoint inventory artifact from live controllers plus DTO/service/filter/runtime auth checks, then scaffold a manual-MDX Mintlify site with resource-based navigation, then author shared pages and one endpoint page per route, and finally reconcile the PM revision/auth docs to the same inventory.

**Tech Stack:** Mintlify (`mint.json` + MDX), NestJS controller/DTO/service/filter code inspection, PM markdown docs, Git

---

## Inputs

- Spec: `docs/superpowers/specs/2026-03-24-external-api-mintlify-design.md`
- Source controllers:
  - `../a60-lensmor-event-business/src/modules/external-api/controllers/external-events.controller.ts`
  - `../a60-lensmor-event-business/src/modules/external-api/controllers/external-exhibitors.controller.ts`
  - `../a60-lensmor-event-business/src/modules/external-api/controllers/external-personnel.controller.ts`
  - `../a60-lensmor-event-business/src/modules/external-api/controllers/external-contacts.controller.ts`
  - `../a60-lensmor-event-business/src/modules/external-api/controllers/external-profile-matching.controller.ts`
- Runtime auth / error truth:
  - `../a60-lensmor-event-business/src/modules/external-api/external-api-auth.middleware.ts`
  - `../a60-lensmor-event-business/src/common/filters/all-exceptions.filter.ts`
  - `../a60-lensmor-event-business/src/main.ts`
  - `../a60-lensmor-event-business/test/e2e/external-events.e2e-spec.ts`
  - `../a60-lensmor-event-business/test/e2e/external-exhibitors.e2e-spec.ts`
- PM docs:
  - `../a60-lensmor-pm/工作流/研发设计/external-api-platform/README.md`
  - `../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部 API 鉴权与错误契约.md`
  - `../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部 API 接口文档（revision）.md`

## Planned File Structure

### Create

- `mint.json` — Mintlify site settings and navigation
- `index.mdx` — public introduction page
- `authentication.mdx` — shared external auth page using runtime truth
- `concepts/errors.mdx` — shared external error contract page
- `concepts/pagination.mdx` — shared pagination/response conventions page
- `api-reference/events/list.mdx`
- `api-reference/events/fit-score.mdx`
- `api-reference/events/rank.mdx`
- `api-reference/events/brief.mdx`
- `api-reference/exhibitors/list.mdx`
- `api-reference/exhibitors/search.mdx`
- `api-reference/exhibitors/profile.mdx`
- `api-reference/exhibitors/events.mdx`
- `api-reference/personnel/list.mdx`
- `api-reference/personnel/profile.mdx`
- `api-reference/personnel/events.mdx`
- `api-reference/contacts/search.mdx`
- `api-reference/profile-matching/recommendations-events-paged.mdx`
- `api-reference/profile-matching/recommendations-exhibitors.mdx`
- `docs/endpoint-inventory/external-api-endpoints.md` — committed endpoint inventory gate artifact
- `docs/reconciliation/external-api-pm-reconciliation.md` — bounded reconciliation table required by spec
- `docs/response-sources/events.md` — evidence notes for Events response examples and success codes
- `docs/response-sources/exhibitors.md` — evidence notes for Exhibitors response examples and success codes
- `docs/response-sources/personnel-and-contacts.md` — evidence notes for Personnel/Contacts response examples and success codes
- `docs/response-sources/profile-matching.md` — evidence notes for Profile Matching response examples and success codes

### Modify

- `README.md` — local contributor setup / preview instructions for the Mintlify site
- `../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部 API 鉴权与错误契约.md` — align auth prefix and external error contract to runtime truth
- `../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部 API 接口文档（revision）.md` — align endpoint list and examples to implemented controllers only
- `../a60-lensmor-pm/工作流/研发设计/external-api-platform/README.md` — tighten description if needed so revision doc is clearly “implemented now” and older drafts remain historical

## Implementation Notes

- Do not publish PM-draft-only endpoints in Mintlify.
- Treat controller routes as the only method/path source of truth.
- Treat `/external/*` exception filtering as the final source of truth for error-body shape.
- Treat runtime middleware as the public source of truth for API key prefix and auth examples even if Swagger/tests still differ.
- Record auth/test/Swagger discrepancies in the reconciliation artifact instead of silently smoothing them over.
- Every endpoint page must include `Success status code`.
- Use manual MDX pages for v1 of the docs site; do not build an OpenAPI-driven site in this pass.
- Prefer small commits after each completed task group.

---

### Task 1: Create the committed endpoint inventory gate artifact

**Files:**
- Create: `docs/endpoint-inventory/external-api-endpoints.md`
- Read/inspect only: all five controller files, `../a60-lensmor-event-business/src/common/filters/all-exceptions.filter.ts`, `../a60-lensmor-event-business/src/modules/external-api/external-api-auth.middleware.ts`

- [ ] **Step 1: Write the inventory artifact skeleton**

```md
# External API Endpoint Inventory

## Rules
- Source of truth for method/path: controllers
- Source of truth for auth example: external runtime middleware
- Source of truth for external error body: `/external/*` branch in AllExceptionsFilter

## Endpoint table
| Method | Path | Controller file | Auth required | Success status | Published in Mintlify | Notes |
| --- | --- | --- | --- | --- | --- | --- |
```

- [ ] **Step 2: Fill in the 14 implemented endpoints from live controllers**

Expected rows:
- `GET /external/events/list`
- `POST /external/events/fit-score`
- `POST /external/events/rank`
- `GET /external/events/brief`
- `GET /external/exhibitors/list`
- `POST /external/exhibitors/search`
- `GET /external/exhibitors/profile`
- `GET /external/exhibitors/events`
- `GET /external/personnel/list`
- `GET /external/personnel/profile`
- `GET /external/personnel/events`
- `GET /external/contacts/search`
- `POST /external/profile-matching/recommendations/events/paged`
- `GET /external/profile-matching/recommendations/exhibitors`

- [ ] **Step 3: Add auth and error truth notes to the artifact**

Add a section like:

```md
## Shared runtime truths
- Authorization format enforced by middleware: `Authorization: Bearer uak_...`
- Swagger currently documents `sk_...` and must not be copied into public docs without reconciliation
- External error responses are emitted as `{ code, message, errorKey, traceId }`
- `/external/*` errors do not expose internal `data` or `details` fields in the final HTTP body
```

- [ ] **Step 4: Verify the artifact against controllers and middleware/filter**

Check:
- all 14 routes are present exactly once
- no `job/start`, `job/status`, or `recommendations/events` GET route is listed
- auth note says `uak_...`
- error note says `{ code, message, errorKey, traceId }`

- [ ] **Step 5: Commit the gate artifact**

```bash
git add docs/endpoint-inventory/external-api-endpoints.md
git commit -m "docs: add external api endpoint inventory"
```

---

### Task 2: Create the PM reconciliation artifact before page writing

**Files:**
- Create: `docs/reconciliation/external-api-pm-reconciliation.md`
- Read/inspect: `../a60-lensmor-pm/工作流/研发设计/external-api-platform/README.md`
- Read/inspect: `../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部 API 鉴权与错误契约.md`
- Read/inspect: `../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部 API 接口文档（revision）.md`
- Reference: `docs/endpoint-inventory/external-api-endpoints.md`

- [ ] **Step 1: Write the reconciliation table skeleton**

```md
# External API PM Reconciliation

| Item | Code status | PM status | Mintlify publish status | Discrepancy note | Required PM update |
| --- | --- | --- | --- | --- | --- |
```

- [ ] **Step 2: Add shared contract discrepancy rows first**

At minimum include:
- auth token prefix: code=`uak_...`, PM=`sk_...`, Mintlify=`publish uak_...`
- external error body: code=`{ code, message, errorKey, traceId }`, PM missing/older shape
- success status semantics for POST endpoints when evidenced by runtime/tests

- [ ] **Step 3: Add one row per live endpoint**

Required endpoint rows:
- `GET /external/events/list`
- `POST /external/events/fit-score`
- `POST /external/events/rank`
- `GET /external/events/brief`
- `GET /external/exhibitors/list`
- `POST /external/exhibitors/search`
- `GET /external/exhibitors/profile`
- `GET /external/exhibitors/events`
- `GET /external/personnel/list`
- `GET /external/personnel/profile`
- `GET /external/personnel/events`
- `GET /external/contacts/search`
- `POST /external/profile-matching/recommendations/events/paged`
- `GET /external/profile-matching/recommendations/exhibitors`

- [ ] **Step 4: Add rows for PM-only or stale routes that must not be published**

At minimum include:
- `POST /external/profile-matching/job/start`
- `GET /external/profile-matching/job/status`
- `GET /external/profile-matching/recommendations/events`

- [ ] **Step 5: Review the table against the endpoint inventory**

Expected result:
- every live endpoint appears explicitly
- auth mismatch is explicit
- error-contract mismatch is explicit
- planned-only endpoints are marked non-published

- [ ] **Step 6: Commit the reconciliation artifact**

```bash
git add docs/reconciliation/external-api-pm-reconciliation.md
git commit -m "docs: add external api pm reconciliation"
```

---

### Task 3: Initialize Mintlify settings and top-level navigation

**Files:**
- Create: `mint.json`
- Modify: `README.md`

- [ ] **Step 1: Verify current Mintlify requirements before writing config**

Gather and record in working notes:
- required top-level `mint.json` fields for a valid site
- navigation/group syntax expected by current Mintlify docs/CLI
- local preview command needed to validate the project

Expected outcome:
- the implementer can write `mint.json` using current Mintlify requirements rather than memory

- [ ] **Step 2: Write `mint.json` with minimal valid site settings and the planned navigation**

Navigation must include:
- intro page
- auth page
- one `API Reference` group with all 14 endpoint pages
- one `Concepts` group with shared support pages

- [ ] **Step 3: Update `README.md` with local docs instructions**

Add a concise section like:

```md
## Local development
- install Mintlify CLI if needed
- run local preview from this repo
- edit MDX pages under `api-reference/` and `concepts/`
```

- [ ] **Step 4: Create temporary placeholder page files only if required for config validation**

If Mintlify preview requires referenced pages to exist before startup, create minimal placeholder MDX files for the pages referenced in navigation, then overwrite them in later tasks.

- [ ] **Step 5: Run local Mintlify validation/preview**

Run the current local preview command for Mintlify.
Expected: the site starts successfully or the config is validated without navigation/file errors.

- [ ] **Step 6: Fix any config/path issues revealed by validation and rerun once**

Expected: valid config with no missing-page navigation errors.

- [ ] **Step 7: Commit the site scaffold config**

```bash
git add mint.json README.md
if [ -d api-reference ] || [ -d concepts ]; then git add api-reference concepts index.mdx authentication.mdx; fi
git commit -m "docs: initialize mintlify navigation"
```

---

### Task 4: Author shared public pages from runtime truth

**Files:**
- Create: `index.mdx`
- Create: `authentication.mdx`
- Create: `concepts/errors.mdx`
- Create: `concepts/pagination.mdx`
- Reference: `docs/endpoint-inventory/external-api-endpoints.md`
- Reference: `docs/reconciliation/external-api-pm-reconciliation.md`
- Reference: runtime auth/error files in `a60-lensmor-event-business`

- [ ] **Step 1: Write `index.mdx` with the site purpose and current scope**

Template:

```mdx
# Lensmor External API

This site documents the currently implemented `external/*` endpoints.

## Current scope
- Events
- Exhibitors
- Personnel
- Contacts
- Profile Matching

## What is not included
- PM draft endpoints that are not implemented in the current codebase
```

- [ ] **Step 2: Write `authentication.mdx` from runtime middleware truth**

Template must include:

```mdx
# Authentication

All `external/*` endpoints require a user API key.

## Header format
```http
Authorization: Bearer uak_your_api_key
```

## Notes
- Bearer scheme is case-insensitive at runtime
- Public docs follow runtime middleware behavior
- Older PM/Swagger references to `sk_...` are historical and not the public-doc source of truth for this phase
```

- [ ] **Step 3: Write `concepts/errors.mdx` from `/external/*` filter behavior**

Template must include:

```mdx
# Error conventions

External API errors use real HTTP status codes.

## Error body
```json
{
  "code": 401,
  "message": "Invalid API key.",
  "errorKey": "INVALID_API_KEY",
  "traceId": "..."
}
```

## Notes
- External responses include `traceId`
- External error bodies do not expose internal `data` or `details` fields
```

- [ ] **Step 4: Write `concepts/pagination.mdx` with shared pagination language**

Template should cover:
- common `page`, `pageSize`, `total`, `totalPages`, `hasMore`
- note that exact fields vary by endpoint family
- string identifiers vs internal numeric ids

- [ ] **Step 5: Review these pages against runtime truth and inventory notes**

Expected result:
- auth page uses `uak_...`
- error page includes `traceId`
- no reference to `job/start` or `job/status`

- [ ] **Step 6: Commit the shared pages**

```bash
git add index.mdx authentication.mdx concepts/errors.mdx concepts/pagination.mdx
git commit -m "docs: add shared external api pages"
```

---

### Task 5: Author Events and Profile Matching API pages

**Files:**
- Create: `api-reference/events/list.mdx`
- Create: `api-reference/events/fit-score.mdx`
- Create: `api-reference/events/rank.mdx`
- Create: `api-reference/events/brief.mdx`
- Create: `api-reference/profile-matching/recommendations-events-paged.mdx`
- Create: `api-reference/profile-matching/recommendations-exhibitors.mdx`
- Create: `docs/response-sources/events.md`
- Create: `docs/response-sources/profile-matching.md`
- Read/inspect supporting DTOs, services, response mappers, stable response-building code, and any relevant tests from `../a60-lensmor-event-business/src/modules/external-api/`

- [ ] **Step 1: Write `docs/response-sources/events.md` with evidence for the four Events pages**

For each Events endpoint record:
- method/path source file
- DTO/query/body source file
- success status source (runtime or tests)
- response example source (mapper/service/response builder)
- ambiguity note if any

- [ ] **Step 2: Write `docs/response-sources/profile-matching.md` with evidence for the two Profile Matching pages**

For each Profile Matching endpoint record:
- method/path source file
- DTO/query/body source file
- success status source
- response example source
- error-contract note pointing to shared `/external/*` filter behavior

- [ ] **Step 3: Write one reusable endpoint-page template and apply it to `events/list`**

Template shape:

```mdx
# List events

## Endpoint
`GET /external/events/list`

## Authentication
See [Authentication](/authentication)

## Success status code
`200 OK`

## Query parameters
| Name | Required | Type | Notes |
| --- | --- | --- | --- |

## Response example
```json
{}
```

## Error responses
- `401 Unauthorized`

## Notes
- ...
```

- [ ] **Step 4: Write `fit-score` and `rank` pages with explicit POST success codes**

Use the response-source notes and runtime/tests as evidence. Do not default to `200`.

- [ ] **Step 5: Write `brief` and both profile-matching pages using only live routes**

Important:
- document `POST /external/profile-matching/recommendations/events/paged`
- document `GET /external/profile-matching/recommendations/exhibitors`
- do not create pages for `job/start`, `job/status`, or `GET /recommendations/events`

- [ ] **Step 6: Verify examples against DTO/service/mapper/filter truth**

Expected result:
- no invented fields
- response examples can be traced back to the response-source notes
- error examples point back to shared error contract
- status codes are present on all 6 pages

- [ ] **Step 7: Commit Events and Profile Matching pages plus evidence notes**

```bash
git add api-reference/events api-reference/profile-matching docs/response-sources/events.md docs/response-sources/profile-matching.md
git commit -m "docs: add events and profile matching api pages"
```

---

### Task 6: Author Exhibitors, Personnel, and Contacts API pages

**Files:**
- Create: `api-reference/exhibitors/list.mdx`
- Create: `api-reference/exhibitors/search.mdx`
- Create: `api-reference/exhibitors/profile.mdx`
- Create: `api-reference/exhibitors/events.mdx`
- Create: `api-reference/personnel/list.mdx`
- Create: `api-reference/personnel/profile.mdx`
- Create: `api-reference/personnel/events.mdx`
- Create: `api-reference/contacts/search.mdx`
- Create: `docs/response-sources/exhibitors.md`
- Create: `docs/response-sources/personnel-and-contacts.md`
- Read/inspect supporting DTOs, services, response mappers, stable response-building code, and any relevant tests from `../a60-lensmor-event-business/src/modules/external-api/`

- [ ] **Step 1: Write `docs/response-sources/exhibitors.md` with evidence for the four Exhibitors pages**

For each Exhibitors endpoint record:
- method/path source file
- DTO/query/body source file
- success status source
- response example source
- ambiguity note if any

- [ ] **Step 2: Write `docs/response-sources/personnel-and-contacts.md` with evidence for the four Personnel/Contacts pages**

For each endpoint record:
- method/path source file
- DTO/query source file
- success status source
- response example source
- ambiguity note if any

- [ ] **Step 3: Write the four Exhibitors pages**

Must include:
- `POST /external/exhibitors/search` with explicit success status code from route/tests
- `GET /external/exhibitors/profile` using `exhibitor_id`, not `company_name`

- [ ] **Step 4: Write the three Personnel pages and `contacts/search`**

Must keep implementation-focused facts out of the public text. Explain only caller-relevant query fields and response semantics.

- [ ] **Step 5: Verify all eight pages against controller routes, DTOs, response-source notes, and shared error/auth pages**

Expected result:
- page title matches route purpose
- every page has success status code
- no unsupported query mode is documented
- each response example is traceable to the response-source notes

- [ ] **Step 6: Commit these resource pages plus evidence notes**

```bash
git add api-reference/exhibitors api-reference/personnel api-reference/contacts docs/response-sources/exhibitors.md docs/response-sources/personnel-and-contacts.md

git commit -m "docs: add exhibitor personnel and contact api pages"
```

---

### Task 7: Reconcile PM auth and revision documents to implemented behavior

**Files:**
- Modify: `../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部 API 鉴权与错误契约.md`
- Modify: `../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部 API 接口文档（revision）.md`
- Modify: `../a60-lensmor-pm/工作流/研发设计/external-api-platform/README.md`
- Reference: `docs/reconciliation/external-api-pm-reconciliation.md`

- [ ] **Step 1: Patch PM auth doc to reflect runtime public truth and historical drift**

Required edits:
- replace `sk_...` public examples with `uak_...`
- update error contract to include `traceId`
- note that `/external/*` final error body is the external contract
- preserve history only as note, not as current contract

- [ ] **Step 2: Patch PM revision doc to match live endpoint inventory**

Required edits:
- remove live-status framing for `job/start`, `job/status`, `GET /recommendations/events`
- add implemented routes now missing from the revision summary (`events/list`, `exhibitors/list`, `exhibitors/events`, `personnel/list`, `personnel/profile`, `personnel/events`, `POST /profile-matching/recommendations/events/paged`)
- fix auth examples to `uak_...`

- [ ] **Step 3: Update PM README only if navigation wording is now misleading**

Use minimal wording changes like:

```md
- revision doc = implemented-now interface list
- v1/v2 drafts = historical/planning references
```

- [ ] **Step 4: Review PM docs against the reconciliation artifact**

Expected result:
- current contract uses `uak_...`
- revision doc no longer claims unimplemented routes are live
- implemented-now wording is consistent across PM entry docs

- [ ] **Step 5: Commit the PM alignment changes**

```bash
git add ../a60-lensmor-pm/工作流/研发设计/external-api-platform/README.md \
  ../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部\ API\ 鉴权与错误契约.md \
  ../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部\ API\ 接口文档（revision）.md

git commit -m "docs: align pm external api docs with implementation"
```

---

### Task 8: Final verification and cleanup

**Files:**
- Review only: all created Mintlify pages, `mint.json`, inventory artifact, reconciliation artifact, response-source notes, PM docs

- [ ] **Step 1: Run a final route/page cross-check manually**

Checklist:
- 14 live endpoints in inventory
- 14 endpoint pages in Mintlify nav
- no draft-only endpoint page exists

- [ ] **Step 2: Run a final auth/error truth check manually**

Checklist:
- auth pages/examples use `uak_...`
- external errors show `{ code, message, errorKey, traceId }`
- no public page mentions `data` or `details` as external error-body fields

- [ ] **Step 3: Run a final success-status and response-source check manually**

Checklist:
- each page includes a `Success status code` section
- POST routes do not silently default to `200`
- each endpoint example is traceable to a response-source note

- [ ] **Step 4: Run the local Mintlify preview/validation one more time**

Expected:
- config loads
- navigation resolves
- created pages render without missing-file errors

- [ ] **Step 5: Review `README.md` and `mint.json` for contributor clarity**

Expected result:
- a new contributor can find the main docs files quickly
- nav references only existing pages

- [ ] **Step 6: Commit the final cleanup if needed**

```bash
git add mint.json README.md index.mdx authentication.mdx concepts api-reference docs/endpoint-inventory docs/reconciliation docs/response-sources

git commit -m "docs: finalize external api mintlify docs"
```
