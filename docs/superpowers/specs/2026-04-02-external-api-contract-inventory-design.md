# External API Contract Inventory Design

Date: 2026-04-02

## Goal

Restructure the `API-Doc` documentation workflow for Lensmor external APIs so that the canonical documentation source becomes a self-contained contract inventory first, followed by endpoint page updates.

The immediate objective is to upgrade `docs/endpoint-inventory/external-api-endpoints.md` into a complete, reviewable contract reference for all implemented external API endpoints derived from the live code in `a60-lensmor-event-business`.

The updated inventory must be self-contained and include, for every implemented endpoint:
- method
- path
- authentication expectation
- success status code
- path parameters
- query parameters
- request body fields
- response body structure
- response examples
- error responses
- runtime notes and caveats

After that inventory is approved, the MDX endpoint pages will be updated in Phase 2 to match the new inventory exactly.

## Requested Delivery Sequence

The work is intentionally split into two phases.

### Phase 1: Canonical contract inventory
Upgrade:
- `docs/endpoint-inventory/external-api-endpoints.md`

This file becomes the canonical self-contained contract document for the current external API surface.

In the same phase:
- keep the endpoint inventory file
- remove `docs/response-sources/*.md`
- do not update `api-reference/**/*.mdx` yet

### Phase 2: Public API page refresh
After the new inventory is complete and reviewed, update:
- `api-reference/**/*.mdx`

Each MDX page must be rewritten to follow the approved inventory contract, so the public pages become self-contained and no longer depend on source-tracing documents.

## Scope

This design covers only the currently implemented routes exposed by these live controllers:
- `../a60-lensmor-event-business/src/modules/external-api/controllers/external-events.controller.ts`
- `../a60-lensmor-event-business/src/modules/external-api/controllers/external-exhibitors.controller.ts`
- `../a60-lensmor-event-business/src/modules/external-api/controllers/external-personnel.controller.ts`
- `../a60-lensmor-event-business/src/modules/external-api/controllers/external-contacts.controller.ts`
- `../a60-lensmor-event-business/src/modules/external-api/controllers/external-profile-matching.controller.ts`

Current implemented route count: 17.

Route families in scope:
- Events
- Exhibitors
- Personnel
- Contacts
- Profile Matching

Out of scope for Phase 1:
- modifying business code
- changing API behavior
- introducing unimplemented endpoints into docs
- updating the 17 MDX endpoint pages before the inventory is finished

## Source-of-Truth Rules

### Route truth
Controllers are authoritative for:
- HTTP method
- route path
- grouping under resource namespaces
- whether an endpoint exists now

### Request truth
Request contracts must be extracted from:
1. controller decorators and handler signatures
2. DTO field definitions and validation metadata
3. runtime normalization behavior that can be confirmed from the executed path

Apply by concern:
- `@Param()` => path parameters
- `@Query()` DTO => query parameters
- `@Body()` DTO => request body
- optional vs required => DTO validation / optionality and controller usage
- defaults / normalization => DTO transformation rules or code-backed runtime behavior

### Response truth
Response contracts must be extracted from:
1. service return shape on the actual route
2. response mapper output where used
3. stable envelope builders and pagination helpers
4. endpoint tests only when they confirm observable behavior already implied by the runtime code

The inventory must document actual emitted fields only.

If PM drafts or old docs contain fields not returned by the current implementation, those fields must not appear as live contract fields.

### Error truth
External error behavior is defined by the shared `/external/*` runtime path.

The inventory must document:
- actual HTTP status behavior
- shared external error body shape
- endpoint-specific common error statuses when evidenced by runtime code or tests

Default external error envelope:
- `code`
- `message`
- `errorKey`
- `traceId`

### Conflict resolution
If controller, DTO, old docs, PM drafts, and runtime response-building logic disagree, the inventory must follow current implemented runtime behavior, with clarifying notes where confusion is likely.

## Documentation Model

### Phase 1 target file model
`docs/endpoint-inventory/external-api-endpoints.md` will stop being a thin inventory table and become an expanded contract reference.

Recommended structure:

1. Title and source-of-truth rules
2. Shared runtime truths
3. Endpoint summary table
4. Detailed endpoint sections, one per route

Each detailed endpoint section should contain:
1. endpoint title
2. method and path
3. authentication
4. success status code
5. path parameters, if any
6. query parameters, if any
7. request body, if any
8. response body
   - top-level field table
   - nested object field tables where needed
9. response example
10. error responses
11. notes

This keeps the inventory self-contained and immediately reusable for Phase 2.

### Response body granularity
The user explicitly requested detailed response field coverage.

Therefore response documentation must include:
- top-level fields
- nested item/object fields in separate tables when needed
- enough structure that a reader does not need to infer fields only from JSON examples

Examples alone are not sufficient.

## Phase 1 Content Rules

### What to preserve
Keep `docs/endpoint-inventory/external-api-endpoints.md` as the single retained internal documentation artifact in `docs/` for endpoint coverage.

### What to remove
Remove these source-tracing documents because they no longer fit the desired model:
- `docs/response-sources/events.md`
- `docs/response-sources/exhibitors.md`
- `docs/response-sources/personnel-and-contacts.md`
- `docs/response-sources/profile-matching.md`

### What not to touch yet
Do not edit the 17 MDX endpoint pages during Phase 1.

## Phase 2 Content Rules

After Phase 1 is approved, update the existing MDX pages listed in `docs.json`.

Each page should become a consumer-friendly projection of the approved inventory contract.

MDX pages should follow a consistent structure:
1. title
2. short purpose statement
3. endpoint
4. authentication
5. success status code
6. path parameters, if any
7. query parameters, if any
8. request body, if any
9. response body
10. response example
11. error responses
12. notes

Phase 2 must not invent any contract details beyond what was locked in by the new inventory.

## Approach Options Considered

### Option A: Update MDX pages first
Pros:
- visible public docs quickly

Cons:
- duplicates contract extraction work across 17 pages
- higher risk of inconsistency between pages
- harder to review correctness before rollout

### Option B: Build a new set of contract markdown files
Pros:
- can separate internal contract detail from public docs

Cons:
- introduces another documentation layer
- duplicates the purpose already served by endpoint inventory
- user explicitly chose not to add a separate contract doc set

### Option C: Upgrade endpoint inventory first, then refresh MDX pages
Pros:
- one canonical contract source
- easier review and correction before page rollout
- clean two-phase workflow
- matches the requested delivery order exactly

Cons:
- public MDX pages remain temporarily older until Phase 2

### Recommendation
Use Option C.

## Extraction Rules by Concern

### Authentication
Document external bearer authentication consistently.

The inventory must state the expected auth format and keep it aligned with runtime middleware behavior.

### Success status codes
Use controller behavior plus verified runtime defaults:
- `GET` routes default to `200 OK` unless overridden
- `POST` routes default to `201 Created` unless overridden
- if tests or explicit decorators confirm different behavior, document the actual behavior

### Request fields
For every request field include, where applicable:
- field name
- required/optional status
- type
- format constraints
- defaults
- max/min bounds when evident
- conditional requirements
- normalization rules if they materially affect callers

### Response fields
For every response field include, where applicable:
- field name
- type
- nullability if evident
- semantic meaning
- notes on always-empty arrays, optional values, or alias behavior when relevant

### Runtime caveats
Use `Notes` to capture important behavior such as:
- `id` vs `eventId`
- routes that accept multiple identifier forms
- empty arrays returned deliberately
- fields present in drafts but absent from real output
- POST routes returning `201` for successful searches/recommendations

## Verification Strategy

Phase 1 is complete only when:
- all 17 routes in the live controllers are represented in the inventory
- each route has method/path/auth/success status documented
- each route has request documentation matching controller + DTO usage
- each route has response documentation matching service/mapper runtime shape
- each route has example payloads aligned to real shape
- shared error body contract is documented consistently
- `docs/response-sources/*.md` are removed
- no MDX files are changed yet

Phase 2 is complete only when:
- every MDX endpoint page matches the approved inventory contract
- no MDX page still relies on response-sources docs
- page structure is consistent across all resources
- `docs.json` navigation remains correct

## Risks and Mitigations

### Risk: DTO and runtime shape drift
Mitigation:
Document runtime output as source of truth and add notes where DTO naming or drafts may mislead readers.

### Risk: Large inventory becomes hard to scan
Mitigation:
Keep a compact summary table near the top, then use repeatable detailed sections below.

### Risk: Phase 1 and Phase 2 diverge
Mitigation:
Treat the upgraded inventory as the sole contract source and update MDX only from that approved version.

## Expected Outcome

After Phase 1:
- `docs/endpoint-inventory/external-api-endpoints.md` is the canonical self-contained contract reference for all implemented external APIs
- `docs/response-sources/*.md` are removed
- the repo has a stable review point before public page updates

After Phase 2:
- all external API MDX pages are updated according to the approved inventory
- each public page becomes self-contained
- the documentation set no longer depends on source-tracing markdown files to understand live API contracts
