# External API Contract Inventory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade `docs/endpoint-inventory/external-api-endpoints.md` into the canonical self-contained contract inventory for all implemented external API endpoints, remove obsolete `docs/response-sources/*.md`, and leave MDX endpoint pages unchanged for now.

**Architecture:** Treat `docs/endpoint-inventory/external-api-endpoints.md` as the single Phase 1 source of truth. Extract method/path/auth/request/response/error details directly from the live external API controllers, DTOs, services, mappers, and runtime auth/error code in the sibling backend repo, then rewrite the inventory into one summary table plus 17 detailed endpoint sections. Do not use tests as documentation evidence, and do not touch `api-reference/**/*.mdx` in this phase.

**Tech Stack:** Markdown docs, Mintlify docs repo structure, NestJS controllers/DTOs/services/mappers as source of truth, ripgrep verification, git diff review

---

### Task 1: Map the implemented external API surface

**Files:**
- Modify: `docs/endpoint-inventory/external-api-endpoints.md`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/controllers/external-events.controller.ts`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/controllers/external-exhibitors.controller.ts`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/controllers/external-personnel.controller.ts`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/controllers/external-contacts.controller.ts`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/controllers/external-profile-matching.controller.ts`

- [ ] **Step 1: Confirm the exact implemented route list from the five controllers**

Run:
```bash
git -C "/Users/linnan/Documents/Projects/a60-lensmor/API-Doc" diff -- docs/endpoint-inventory/external-api-endpoints.md
```
Expected: existing inventory still present and ready to be replaced

Run:
```bash
rg -n "@Controller\(|@Get\(|@Post\(" \
  "/Users/linnan/Documents/Projects/a60-lensmor/a60-lensmor-event-business/src/modules/external-api/controllers"
```
Expected: exactly the implemented `external/*` controller groups and handler decorators are listed

- [ ] **Step 2: Keep the summary table at the top of the inventory, but prepare to replace the old thin notes with detailed contract sections**

Target top-of-file structure:
```md
# External API Endpoint Inventory

## Rules
- Source of truth for method/path: controllers
- Source of truth for request contracts: controller + DTO
- Source of truth for response contracts: service + mapper + runtime output shape
- Source of truth for auth/error behavior: runtime middleware and external error path
- Tests are not used as contract evidence in this document

## Endpoint table
| Method | Path | Controller file | Auth required | Success status | Published in Mintlify | Notes |
| --- | --- | --- | --- | --- | --- | --- |
```

- [ ] **Step 3: Verify the route count still matches 17 before writing detailed sections**

Run:
```bash
rg -n "@Get\(|@Post\(" \
  "/Users/linnan/Documents/Projects/a60-lensmor/a60-lensmor-event-business/src/modules/external-api/controllers" \
  | wc -l
```
Expected: `17`

### Task 2: Extract shared auth and error contract once

**Files:**
- Modify: `docs/endpoint-inventory/external-api-endpoints.md`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/guards/api-key-only.guard.ts`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/external-api-auth.middleware.ts`
- Read only: `../a60-lensmor-event-business/src/common/filters/all-exceptions.filter.ts`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/filters/external-api-exception.filter.ts`

- [ ] **Step 1: Document the shared auth rules in the inventory’s shared runtime section**

Insert or update this shape near the top of `docs/endpoint-inventory/external-api-endpoints.md`:
```md
## Shared runtime truths
- Authorization header format: `Authorization: Bearer uak_...`
- Bearer scheme stripping is case-insensitive at runtime
- All current external controller routes require authentication through the external API auth flow
- External error responses use the public envelope `{ code, message, errorKey, traceId }`
```

- [ ] **Step 2: Verify the auth token prefix and bearer parsing from runtime code, not tests**

Run:
```bash
rg -n "Bearer|uak_" \
  "/Users/linnan/Documents/Projects/a60-lensmor/a60-lensmor-event-business/src/modules/external-api"
```
Expected: runtime auth files show the live bearer parsing and token prefix behavior

- [ ] **Step 3: Verify the external error response envelope from runtime code, not tests**

Run:
```bash
rg -n "traceId|errorKey|code|message|external" \
  "/Users/linnan/Documents/Projects/a60-lensmor/a60-lensmor-event-business/src/common/filters" \
  "/Users/linnan/Documents/Projects/a60-lensmor/a60-lensmor-event-business/src/modules/external-api/filters"
```
Expected: the external error path confirms the public error envelope fields

### Task 3: Expand the Events endpoint contracts in the inventory

**Files:**
- Modify: `docs/endpoint-inventory/external-api-endpoints.md`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/controllers/external-events.controller.ts`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/dto/events/*.ts`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/dto/common/*.ts`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/services/external-events.service.ts`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/mappers/external-event-response.mapper.ts`

- [ ] **Step 1: Add detailed sections for the five Events endpoints below the summary table**

Use this repeated section pattern:
```md
## GET /external/events/list

### Authentication
Bearer token required.

### Success status code
`200 OK`

### Query parameters
| Name | Required | Type | Notes |
| --- | --- | --- | --- |
| `page` | No | integer | Defaults to `1`. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `items` | object[] | Paginated event items. |

#### `items[]` fields
| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Internal row identifier exposed by the API. |

### Response example
```json
{}
```

### Error responses
- `401 Unauthorized`

### Notes
- Add route-specific runtime caveats only.
```

- [ ] **Step 2: Populate request and response structures from DTOs plus service/mapper output for all five Events routes**

Run:
```bash
rg -n "class ExternalEvent|listEvents|fitScore|rankEvents|getEventBrief|getEventDetail|toEvent" \
  "/Users/linnan/Documents/Projects/a60-lensmor/a60-lensmor-event-business/src/modules/external-api"
```
Expected: DTOs, service methods, and mapper methods for all Events endpoints are visible for contract extraction

- [ ] **Step 3: Capture route-specific caveats in Notes where the runtime behavior is easy to misunderstand**

Required notes to preserve if still true in code:
```md
- `GET /external/events/:id` accepts either the internal row `id` or external `eventId` in the `:id` segment.
- `POST /external/events/rank` currently returns an empty `reasons` array for each item.
- `GET /external/events/brief` currently returns `topCategories` as an empty array.
```

### Task 4: Expand the Exhibitors endpoint contracts in the inventory

**Files:**
- Modify: `docs/endpoint-inventory/external-api-endpoints.md`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/controllers/external-exhibitors.controller.ts`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/dto/exhibitors/*.ts`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/dto/common/*.ts`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/services/external-exhibitors.service.ts`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/mappers/*.ts`

- [ ] **Step 1: Add detailed sections for all six Exhibitors endpoints**

Required headings:
```md
## GET /external/exhibitors/list
## POST /external/exhibitors/search
## POST /external/exhibitors/search-by-company-name
## POST /external/exhibitors/search-events
## GET /external/exhibitors/profile
## GET /external/exhibitors/events
```

- [ ] **Step 2: Document body/query structures and nested response item fields for each Exhibitors route**

Run:
```bash
rg -n "searchByCompanyName|searchEvents|profile|events|companyName|matched_event_ids|techStacks" \
  "/Users/linnan/Documents/Projects/a60-lensmor/a60-lensmor-event-business/src/modules/external-api"
```
Expected: exhibitor request inputs and response fields are traceable in DTO/service/mapper code

- [ ] **Step 3: Preserve the important runtime Notes for exhibitor responses when still true in code**

Required notes to evaluate and keep only if supported by current implementation:
```md
- No matches return an empty success response rather than `404`.
- `matched_event_ids` is an empty array when no event scope or match data exists.
- `techStacks` is always returned as an array.
```

### Task 5: Expand the Personnel, Contacts, and Profile Matching contracts in the inventory

**Files:**
- Modify: `docs/endpoint-inventory/external-api-endpoints.md`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/controllers/external-personnel.controller.ts`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/controllers/external-contacts.controller.ts`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/controllers/external-profile-matching.controller.ts`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/dto/personnel/*.ts`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/dto/contacts/*.ts`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/dto/profile-matching/*.ts`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/services/*.ts`
- Read only: `../a60-lensmor-event-business/src/modules/external-api/mappers/*.ts`

- [ ] **Step 1: Add detailed sections for the remaining six endpoints**

Required headings:
```md
## GET /external/personnel/list
## GET /external/personnel/profile
## GET /external/personnel/events
## GET /external/contacts/search
## POST /external/profile-matching/recommendations/events/paged
## GET /external/profile-matching/recommendations/exhibitors
```

- [ ] **Step 2: Document each route’s path/query/body contract and detailed response fields**

Run:
```bash
rg -n "recommendations|paged|condition_tags|profile_version|active_result_version|is_stale|contacts|personnel" \
  "/Users/linnan/Documents/Projects/a60-lensmor/a60-lensmor-event-business/src/modules/external-api"
```
Expected: profile matching, contacts, and personnel contracts are traceable in runtime code

- [ ] **Step 3: Add Notes for identifier aliasing, paged recommendation metadata, and any route-specific runtime caveats**

Required note themes:
```md
- Whether the request-side identifier names differ from response-side identifier names.
- Which profile-matching metadata fields are returned at the top level.
- Any empty-array or nullable-field behavior that callers should expect.
```

### Task 6: Remove obsolete response-sources documents

**Files:**
- Delete: `docs/response-sources/events.md`
- Delete: `docs/response-sources/exhibitors.md`
- Delete: `docs/response-sources/personnel-and-contacts.md`
- Delete: `docs/response-sources/profile-matching.md`

- [ ] **Step 1: Delete the four obsolete source-tracing markdown files**

Target removal list:
```text
docs/response-sources/events.md
docs/response-sources/exhibitors.md
docs/response-sources/personnel-and-contacts.md
docs/response-sources/profile-matching.md
```

- [ ] **Step 2: Verify the deleted files are not still referenced anywhere in the docs repo**

Run:
```bash
rg -n "response-sources" \
  "/Users/linnan/Documents/Projects/a60-lensmor/API-Doc"
```
Expected: no matches outside git history or deleted-file diffs

- [ ] **Step 3: Confirm no MDX files were changed during Phase 1**

Run:
```bash
git -C "/Users/linnan/Documents/Projects/a60-lensmor/API-Doc" diff --name-only
```
Expected:
```text
docs/endpoint-inventory/external-api-endpoints.md
docs/response-sources/events.md
docs/response-sources/exhibitors.md
docs/response-sources/personnel-and-contacts.md
docs/response-sources/profile-matching.md
```

### Task 7: Verify the rewritten inventory before handoff

**Files:**
- Verify only: `docs/endpoint-inventory/external-api-endpoints.md`

- [ ] **Step 1: Verify every implemented route appears exactly once in the detailed sections**

Run:
```bash
rg -n "^## (GET|POST) /external/" \
  "/Users/linnan/Documents/Projects/a60-lensmor/API-Doc/docs/endpoint-inventory/external-api-endpoints.md"
```
Expected: `17` detailed endpoint headings

- [ ] **Step 2: Verify the inventory documents request and response sections consistently**

Run:
```bash
rg -n "^### (Authentication|Success status code|Path parameters|Query parameters|Request body|Response body|Response example|Error responses|Notes)" \
  "/Users/linnan/Documents/Projects/a60-lensmor/API-Doc/docs/endpoint-inventory/external-api-endpoints.md"
```
Expected: repeated section headings for each relevant endpoint, with no missing core contract sections

- [ ] **Step 3: Review the final diff to ensure this phase is inventory-only and self-contained**

Run:
```bash
git -C "/Users/linnan/Documents/Projects/a60-lensmor/API-Doc" diff -- docs/endpoint-inventory/external-api-endpoints.md docs/response-sources
```
Expected: the inventory is substantially expanded, the four response-sources files are removed, and no unrelated docs are modified
