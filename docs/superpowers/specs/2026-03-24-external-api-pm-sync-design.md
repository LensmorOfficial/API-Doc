# External API PM Sync Design

Date: 2026-03-24

## Goal

Keep `API-Doc` as the source of truth for the public external API contract and bring the PM-side `外部 API 接口文档（revision）.md` to near-parity with it while preserving Chinese PM writing style.

## Background

The current Mintlify documentation in `API-Doc` was produced through a code-first workflow:

- live controllers and runtime behavior define the contract
- PM docs provide explanation and business framing
- discrepancies are reconciled after the public docs are written

The current PM revision document has already been partially aligned to the live routes, but it is still materially less detailed than the Mintlify pages. The reconciliation artifact in `API-Doc` also still reflects an earlier state where the PM revision was behind.

## Problem

The project currently has two documentation surfaces for the same external API:

1. `API-Doc`, which is detailed and structured per endpoint
2. PM-side `外部 API 接口文档（revision）.md`, which is Chinese and easier for internal coordination

The user wants these two surfaces to stay almost the same in contract content. Right now they are close at the inventory level, but not yet close enough at the endpoint-detail level.

## Source-of-Truth Decision

`API-Doc` remains the only source of truth for public contract details in this sync pass.

Reasoning:

- it was built from code/runtime evidence first
- it already contains endpoint-by-endpoint parameter, status, example, and note sections
- using one source of truth avoids reintroducing PM-draft-only routes or stale auth/error wording

PM documents must mirror `API-Doc` for contract content, not the other way around.

## Scope

### In scope

- synchronize PM `外部 API 接口文档（revision）.md` to match `API-Doc` at endpoint-detail level
- keep PM writing in Chinese
- update `docs/reconciliation/external-api-pm-reconciliation.md` so it reflects the new synchronized state instead of the earlier pre-sync discrepancies
- preserve current `API-Doc` page structure and contract wording as the baseline

### Out of scope

- changing the Mintlify navigation or information architecture
- turning the PM document into a page-by-page English mirror
- rewriting unrelated PM platform docs unless they block contract consistency
- changing runtime behavior, controllers, DTOs, or response examples unless evidence shows the docs are already wrong

## Synchronization Boundary

This effort targets contract-level parity, not literal text duplication.

The following must match between `API-Doc` and PM `revision`:

- implemented endpoint inventory
- authentication expectations relevant to callers
- success status codes
- query parameter and request body field sets
- required vs optional semantics
- response example structure
- listed error responses
- caller-relevant notes and limitations

The following may differ:

- language (`API-Doc` English, PM doc Chinese)
- paragraph phrasing and prose style
- Mintlify-specific navigation and cross-link style
- document-level introduction wording where contract meaning is unchanged

## Endpoint Mapping Rule

Each endpoint page in `API-Doc` maps to one Chinese section in PM `revision`.

Stable section mapping:

- `Endpoint` -> `接口`
- `Authentication` -> `鉴权要求`
- `Success status code` -> `成功状态码`
- `Query parameters` -> `查询参数`
- `Request body` -> `请求体`
- `Response example` -> `响应示例`
- `Error responses` -> `错误响应`
- `Notes` -> `说明`

The PM doc should use this structure consistently for every endpoint, while keeping Chinese wording around it.

## Shared Content Rule

Shared contract content in the PM `revision` should also be aligned to the Mintlify shared pages:

- auth header and token prefix must match `authentication.mdx`
- shared external error shape must match `concepts/errors.mdx`
- shared pagination wording must match `concepts/pagination.mdx`
- resource inventory must match `docs.json` navigation and endpoint pages

If a shared PM statement conflicts with `API-Doc`, the PM statement must be rewritten to match `API-Doc`.

## Files To Change

### Primary edits

- `../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部 API 接口文档（revision）.md`
- `docs/reconciliation/external-api-pm-reconciliation.md`

### Reference inputs

- `index.mdx`
- `authentication.mdx`
- `concepts/errors.mdx`
- `concepts/pagination.mdx`
- all files under `api-reference/`
- `docs/endpoint-inventory/external-api-endpoints.md`

## Implementation Strategy

1. Read the shared Mintlify pages and all endpoint pages.
2. Build a per-endpoint sync checklist from `API-Doc`.
3. Rewrite the PM `revision` endpoint sections so each one includes the same contract data as the corresponding Mintlify page, in Chinese.
4. Preserve PM-level headings where they still make sense, but normalize endpoint subsections to the stable mapping rule.
5. Update the reconciliation artifact so it documents the synchronized state and any remaining non-contract differences.
6. Re-read both surfaces to verify there are no endpoint mismatches in route list, auth wording, status codes, request fields, response example keys, or historical notes.

## Reconciliation Artifact Outcome

After this sync, `docs/reconciliation/external-api-pm-reconciliation.md` should no longer describe the PM revision as generally stale.

Instead, it should document:

- that `API-Doc` is the contract source of truth
- that PM `revision` has been synchronized to it
- any remaining expression-only differences that are intentional
- the maintenance rule for future updates: update `API-Doc` first, then mirror PM `revision`

## Risks

### Risk 1: Copy drift during manual sync

Because the PM doc is prose-heavy and Chinese, manual transcription can introduce small field or status mismatches.

Mitigation:

- verify every endpoint against the corresponding Mintlify page after editing
- check names, required flags, status codes, and response example keys line by line

### Risk 2: Over-synchronizing non-contract wording

Trying to force exact structural duplication would make the PM doc harder to read and maintain.

Mitigation:

- keep the contract sections aligned
- allow prose-level differences where no contract meaning changes

### Risk 3: Leaving stale reconciliation notes behind

If the PM revision is synchronized but reconciliation is not updated, internal readers will see contradictory status reporting.

Mitigation:

- update reconciliation in the same change set

## Success Criteria

The work is successful when:

- PM `revision` contains the same 14 live endpoints as `API-Doc`
- each endpoint in PM `revision` includes the same contract-level data categories as its Mintlify counterpart
- auth wording uses the same current public contract as `API-Doc`
- stale PM-only route framing is not reintroduced
- `docs/reconciliation/external-api-pm-reconciliation.md` reflects the synchronized state

## Follow-up Plan Direction

The implementation plan should focus on a bounded documentation sync pass:

- inventory the `API-Doc` endpoint pages as the sync baseline
- patch PM `revision`
- patch reconciliation
- run a final parity review across the two surfaces
