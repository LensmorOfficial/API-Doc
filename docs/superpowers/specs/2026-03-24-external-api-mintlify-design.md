# External API Mintlify Documentation Design

Date: 2026-03-24

## Goal

Initialize the `API-Doc` repository as a Mintlify documentation project and publish the currently implemented `external-api` endpoints from `a60-lensmor-event-business` as developer-facing API reference docs.

The published documentation must use the current codebase as the source of truth for exposed routes, while incorporating PM documentation as the explanation layer for authentication, parameter meaning, business semantics, and error conventions.

## Scope

This effort covers only endpoints that are currently exposed by the code in:

- `../a60-lensmor-event-business/src/modules/external-api/controllers/external-events.controller.ts`
- `../a60-lensmor-event-business/src/modules/external-api/controllers/external-exhibitors.controller.ts`
- `../a60-lensmor-event-business/src/modules/external-api/controllers/external-personnel.controller.ts`
- `../a60-lensmor-event-business/src/modules/external-api/controllers/external-contacts.controller.ts`
- `../a60-lensmor-event-business/src/modules/external-api/controllers/external-profile-matching.controller.ts`

Current intended endpoint inventory:

This inventory is provisional until a dedicated endpoint inventory artifact is produced from the live controllers during implementation. That inventory becomes the required gate before page authoring starts and must record each method/path pair, its controller source, and whether it is published in Mintlify.

### Events
- `GET /external/events/list`
- `POST /external/events/fit-score`
- `POST /external/events/rank`
- `GET /external/events/brief`

### Exhibitors
- `GET /external/exhibitors/list`
- `POST /external/exhibitors/search`
- `GET /external/exhibitors/profile`
- `GET /external/exhibitors/events`

### Personnel
- `GET /external/personnel/list`
- `GET /external/personnel/profile`
- `GET /external/personnel/events`

### Contacts
- `GET /external/contacts/search`

### Profile Matching
- `POST /external/profile-matching/recommendations/events/paged`
- `GET /external/profile-matching/recommendations/exhibitors`

Endpoints that appear only in older PM or spec drafts and are not currently exposed by the code must not be published as active API reference pages in Mintlify.

## Source-of-Truth Rules

### Route truth
Controller definitions are authoritative for:
- HTTP method
- route path
- resource grouping
- whether an endpoint is considered currently implemented

### Contract truth
Contract extraction must use this precedence order when code layers differ:
1. controller decorator shape and method signature
2. DTO validation rules and field names
3. actual service call usage from the controller path
4. response mapper output, exception filter output, or other stable response-building code on the executed route
5. PM wording only when the above layers do not define the meaning clearly

Apply the precedence by concern:
- method/path/grouping: controller only
- request parameters and body fields: controller + DTO first, then confirm service usage
- required vs optional: DTO validation and controller usage first
- response fields: response mapper or stable response-building code first
- error response shape and status semantics: external error mapper / exception filter behavior first for `/external/*` routes, then controller-level exceptions only if they survive unchanged to the final HTTP response
- pagination/filter semantics: DTO and service behavior first

If DTOs, service usage, and response builders disagree, the docs must follow the highest-precedence implemented layer and record the discrepancy in the reconciliation artifact instead of silently merging interpretations.

### Explanation truth
PM documentation is used to supply:
- endpoint purpose and business context
- authentication explanation
- error semantics
- terminology and field meaning

If PM wording conflicts with the code, the Mintlify docs must follow the code. PM documents should then be updated to reflect the implemented state.

## Target Audience

The Mintlify site should be written as external developer documentation, not as internal implementation notes.

Primary emphasis:
- how to authenticate
- what each endpoint does
- which parameters are required or optional
- what the request and response look like
- what error conditions clients should handle

Secondary emphasis:
- concise notes where a business constraint matters to callers

Avoid surfacing internal NestJS structure, controller filenames, or service wiring in the public-facing pages unless needed for internal maintenance notes outside the main API reference.

## Recommended Information Architecture

The Mintlify site should be initialized with a small, resource-oriented structure.

Implementation pattern is fixed for this phase:
- use manual MDX pages as the primary delivery format
- use `mint.json` navigation groups to organize pages by resource
- do not depend on generated OpenAPI rendering for the initial version
- if Mintlify API-specific components are later introduced, they may enhance a page but must not replace the manual MDX content model in this phase

### Top-level pages
- Introduction
- Authentication
- API Reference
- Concepts

### API Reference groups
- Events
- Exhibitors
- Personnel
- Contacts
- Profile Matching

### Concepts pages
- Error conventions
- Pagination and shared response patterns

## Page Organization

Use one endpoint per page.

Each API page should follow a consistent structure:
1. Summary
2. Method and path
3. Authentication
4. Query parameters or request body
5. Success status code
6. Response example
7. Error responses
8. Notes

Example payload rules:
- examples are illustrative unless directly backed by stable response-building code, mappers, tests, or existing approved PM examples that match the implemented fields
- do not invent fields, enum values, status values, or pagination members not evidenced in code or already-approved PM semantics
- when the exact runtime shape is unclear, prefer smaller representative examples and explicitly avoid implying completeness

This keeps each endpoint easy to scan and makes future additions additive rather than requiring large rewrites.

## Proposed Mintlify File Layout

```text
API-Doc/
├── mint.json
├── README.md
├── index.mdx
├── authentication.mdx
├── api-reference/
│   ├── events/
│   │   ├── list.mdx
│   │   ├── fit-score.mdx
│   │   ├── rank.mdx
│   │   └── brief.mdx
│   ├── exhibitors/
│   │   ├── list.mdx
│   │   ├── search.mdx
│   │   ├── profile.mdx
│   │   └── events.mdx
│   ├── personnel/
│   │   ├── list.mdx
│   │   ├── profile.mdx
│   │   └── events.mdx
│   ├── contacts/
│   │   └── search.mdx
│   └── profile-matching/
│       ├── recommendations-events-paged.mdx
│       └── recommendations-exhibitors.mdx
└── concepts/
    ├── errors.mdx
    └── pagination.mdx
```

The exact Mintlify navigation syntax should follow current Mintlify settings guidance, but the content model should stay resource-oriented.

Required initial navigation expectation:
- top-level intro and auth pages
- one `API Reference` group containing the five resource sections
- one `Concepts` group containing shared support pages
- no separate published group for planned-only or historical endpoints in this phase

## Documentation Workflow

### Step 1: Endpoint inventory from code
Read the current controllers and supporting DTOs/services/mappers to extract:
- route list
- parameter names
- required vs optional fields
- request payload structures
- representative response payloads
- effective error response shape and status behavior, including any `/external/*` exception filter branch and external error mapper usage
- auth usage patterns

Required output of this step:
- a checked endpoint inventory artifact stored in the documentation repo in a reviewable location; working notes may assist drafting but do not satisfy this gate
- for each endpoint: method, path, controller file, publish status, and notes on any contract ambiguity
- page authoring must not begin until this inventory is complete and reviewed against the live controllers

### Step 2: PM document reconciliation
Read PM external API design documents and align them to the current endpoint inventory.

Required reconciliation output:
- a bounded reconciliation table with columns: endpoint, code status, PM status, Mintlify publish status, discrepancy note, and required PM update
- when there is a dispute about whether something is implemented, code status wins for public docs in this phase
- PM updates in this phase are limited to external API documents directly related to the published endpoints and shared auth/error semantics
- shared auth documentation must verify the exact `Authorization` header pattern and example token prefix against the runtime middleware before publication
- if Swagger text, tests, or PM docs disagree with runtime auth validation, record the discrepancy and use runtime behavior as the public-doc source of truth for this phase

Outcomes:
- implemented endpoints get updated descriptions aligned to current code
- planned-only endpoints are marked as future or historical, not published as active reference
- terminology is normalized between PM and Mintlify docs

### Step 3: Mintlify initialization
Create the Mintlify configuration and the initial page/navigation structure for the site.

### Step 4: Public API page authoring
Write endpoint pages using a shared structure and consistent terminology.

### Step 5: PM updates
Update PM-facing API documentation so it clearly distinguishes:
- implemented now
- planned / historical draft

### Step 6: Final cross-check
Compare the generated docs against current controllers, DTOs, response builders, and `/external/*` error-shaping code again to ensure the published docs do not promise endpoints, fields, or error semantics the code does not expose.

## Approach Options Considered

### Option A: Mintlify-first scaffolding
Initialize the site first, then backfill endpoint content.

Pros:
- fastest way to see a visible site structure

Cons:
- more likely to require structural rework after endpoint reconciliation
- higher chance of early page placeholders drifting from code

### Option B: Code-first inventory, then Mintlify generation
Extract the actual endpoints first, reconcile PM semantics second, then initialize Mintlify and write final pages.

Pros:
- strongest alignment with implemented behavior
- least likely to create doc drift
- easiest to keep the public docs trustworthy

Cons:
- slightly more upfront analysis before visible docs appear

### Option C: Parallel “implemented” and “planned” doc trees
Publish both current and future APIs in the same documentation site.

Pros:
- preserves the full roadmap context

Cons:
- likely to confuse external readers
- weakens trust in the published API reference
- not aligned with the goal of initializing the current documentation project around real endpoints

### Recommendation
Use Option B.

## Error Handling Design for Docs

The public docs should include a shared error conventions page and avoid repeating long generic prose on every endpoint page.

Each endpoint page should include only endpoint-specific error cases plus a short pointer to the shared error conventions page.

Where existing PM materials mention historical error behavior that is not implemented, keep that discussion in PM context rather than the public docs.

Shared error guidance describes the default contract only. If a specific endpoint has a real deviation in status code usage, error body shape, or notable failure mode, that deviation must be called out explicitly on that endpoint page.

## Authentication Design for Docs

The public docs should centralize auth in one dedicated page and repeat only a short reminder in each endpoint page.

The docs must describe the shared auth pattern once and keep endpoint pages concise, but the Authentication page and all auth examples must first be reconciled against the runtime auth middleware and current tests. If token prefix, bearer example, Swagger text, or tests disagree, the published docs must follow the implemented runtime check and record the discrepancy in the reconciliation artifact.

The shared authentication page describes the default auth model. If an endpoint differs in guard usage, bearer requirement, or caller context, the endpoint page must document that deviation explicitly.

## Testing and Verification Strategy

Before considering the documentation complete:
- verify every published page maps to a current controller route
- verify method/path pairs against controller decorators
- verify documented success status code against the implemented route behavior and available tests
- verify parameter names against DTOs where available
- verify request/response examples against service, mapper, filter, and runtime response-shaping behavior as far as the code reveals
- verify Mintlify navigation includes every intended page and no stale ones

## Out of Scope

- Publishing unimplemented endpoints as active API reference pages
- Refactoring the NestJS external-api module itself
- Generating a full OpenAPI spec unless the codebase already exposes one and it becomes useful as a secondary artifact
- Documenting non-external internal APIs in this pass

## Expected Outcome

After implementation:
1. `API-Doc` becomes a valid Mintlify documentation project
2. external developers can browse the currently implemented external API by resource
3. PM external API docs become aligned with what the code currently exposes
4. future implementation reviews can compare code, PM docs, and Mintlify docs against the same endpoint inventory
