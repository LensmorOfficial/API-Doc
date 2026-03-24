# External API PM Sync Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Synchronize the PM-side `外部 API 接口文档（revision）.md` to near-parity with `API-Doc`, then update the reconciliation artifact so both surfaces reflect the same current contract.

**Architecture:** Treat `API-Doc` as the sole source of truth for contract details. Extract the shared contract and endpoint-by-endpoint baseline from the Mintlify docs, rewrite the PM `revision` in Chinese to mirror that baseline, then replace the stale discrepancy-focused reconciliation table with one that documents the synchronized state and future maintenance rule.

**Tech Stack:** Markdown/MDX, Mintlify content files, PM Markdown docs, `rg`, `sed`, Git

---

## Inputs

- Spec: `docs/superpowers/specs/2026-03-24-external-api-pm-sync-design.md`
- Source-of-truth shared pages:
  - `index.mdx`
  - `authentication.mdx`
  - `concepts/errors.mdx`
  - `concepts/pagination.mdx`
- Source-of-truth endpoint pages:
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
- Inventory artifact:
  - `docs/endpoint-inventory/external-api-endpoints.md`
- Target files:
  - `../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部 API 接口文档（revision）.md`
  - `docs/reconciliation/external-api-pm-reconciliation.md`

## Constraints

- `API-Doc` is the only contract source of truth for this pass.
- The PM document must remain Chinese in style and headings outside the fixed contract sections.
- The PM document lives outside the current writable root. Editing it requires explicit escalated permission.
- Do not widen scope into unrelated PM docs unless a blocking inconsistency is discovered during sync.
- Do not change the Mintlify endpoint pages unless verification proves they are internally inconsistent.

## Planned File Structure

### Modify

- `../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部 API 接口文档（revision）.md`
- `docs/reconciliation/external-api-pm-reconciliation.md`

### Reference Only

- `index.mdx`
- `authentication.mdx`
- `concepts/errors.mdx`
- `concepts/pagination.mdx`
- every file under `api-reference/`
- `docs/endpoint-inventory/external-api-endpoints.md`

## Chunk 1: Build The Sync Baseline

### Task 1: Confirm the shared contract baseline

**Files:**
- Read: `index.mdx`
- Read: `authentication.mdx`
- Read: `concepts/errors.mdx`
- Read: `concepts/pagination.mdx`
- Read: `docs/endpoint-inventory/external-api-endpoints.md`

- [ ] **Step 1: Inspect the shared pages and inventory**

Run:

```bash
sed -n '1,220p' index.mdx
sed -n '1,220p' authentication.mdx
sed -n '1,220p' concepts/errors.mdx
sed -n '1,220p' concepts/pagination.mdx
sed -n '1,220p' docs/endpoint-inventory/external-api-endpoints.md
```

Expected:
- shared auth uses `Authorization: Bearer uak_your_api_key`
- shared error contract includes `traceId`
- shared pagination wording is current
- inventory still lists exactly 14 live endpoints

- [ ] **Step 2: Capture the non-negotiable sync checklist in working notes**

Checklist must include:
- auth prefix is `uak_...`
- no PM-draft-only live routes
- exactly 14 live endpoints
- PM `revision` must mirror status codes, request fields, response keys, and caller-facing notes from `API-Doc`

Expected:
- implementer has a compact checklist before touching the PM file

### Task 2: Confirm the endpoint-by-endpoint baseline

**Files:**
- Read: all files under `api-reference/`

- [ ] **Step 1: Review each endpoint page in resource order**

Run:

```bash
sed -n '1,220p' api-reference/events/list.mdx
sed -n '1,220p' api-reference/events/fit-score.mdx
sed -n '1,220p' api-reference/events/rank.mdx
sed -n '1,220p' api-reference/events/brief.mdx
sed -n '1,220p' api-reference/exhibitors/list.mdx
sed -n '1,220p' api-reference/exhibitors/search.mdx
sed -n '1,220p' api-reference/exhibitors/profile.mdx
sed -n '1,220p' api-reference/exhibitors/events.mdx
sed -n '1,220p' api-reference/personnel/list.mdx
sed -n '1,220p' api-reference/personnel/profile.mdx
sed -n '1,220p' api-reference/personnel/events.mdx
sed -n '1,220p' api-reference/contacts/search.mdx
sed -n '1,220p' api-reference/profile-matching/recommendations-events-paged.mdx
sed -n '1,220p' api-reference/profile-matching/recommendations-exhibitors.mdx
```

Expected:
- every endpoint page exposes method/path, success status, request section, response example, error responses, and notes

- [ ] **Step 2: Build the endpoint sync matrix in scratch notes**

For each of the 14 endpoints, record:
- section title to use in Chinese
- success status code
- whether the request section is query parameters or request body
- exact request field names and requiredness
- exact response example top-level keys
- exact error response statuses
- notes that must survive translation

Expected:
- implementer can patch the PM file without reopening the Mintlify pages repeatedly

## Chunk 2: Patch The PM Revision Document

### Task 3: Obtain permission and rewrite the shared PM sections

**Files:**
- Modify: `../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部 API 接口文档（revision）.md`
- Reference: `index.mdx`
- Reference: `authentication.mdx`
- Reference: `concepts/errors.mdx`
- Reference: `concepts/pagination.mdx`

- [ ] **Step 1: Request escalated permission to edit the PM file**

Expected:
- approval is obtained before any write outside the current writable root

- [ ] **Step 2: Rewrite the PM shared sections from the Mintlify baseline**

Update:
- overview and scope framing
- auth section
- identifier-field conventions
- shared error/pagination wording where present

Keep:
- Chinese PM prose
- internal PM-style headings where they do not weaken contract clarity

Expected:
- PM top sections match current `API-Doc` contract but still read like a Chinese PM document

- [ ] **Step 3: Normalize the PM endpoint subsection template**

For each endpoint subsection, use this stable section mapping:
- `接口`
- `鉴权要求`
- `成功状态码`
- `查询参数` or `请求体`
- `响应示例`
- `错误响应`
- `说明`

Expected:
- the PM file has one consistent contract structure across all 14 endpoints

### Task 4: Rewrite the Events and Exhibitors sections

**Files:**
- Modify: `../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部 API 接口文档（revision）.md`
- Reference: `api-reference/events/list.mdx`
- Reference: `api-reference/events/fit-score.mdx`
- Reference: `api-reference/events/rank.mdx`
- Reference: `api-reference/events/brief.mdx`
- Reference: `api-reference/exhibitors/list.mdx`
- Reference: `api-reference/exhibitors/search.mdx`
- Reference: `api-reference/exhibitors/profile.mdx`
- Reference: `api-reference/exhibitors/events.mdx`

- [ ] **Step 1: Rewrite all Events endpoint sections**

Endpoints:
- `GET /external/events/list`
- `POST /external/events/fit-score`
- `POST /external/events/rank`
- `GET /external/events/brief`

Expected:
- each Events section mirrors the Mintlify page for status, request fields, response shape, error statuses, and notes

- [ ] **Step 2: Rewrite all Exhibitors endpoint sections**

Endpoints:
- `GET /external/exhibitors/list`
- `POST /external/exhibitors/search`
- `GET /external/exhibitors/profile`
- `GET /external/exhibitors/events`

Expected:
- Exhibitors sections use the same field names and notes as `API-Doc`, including any identifier constraints

### Task 5: Rewrite the Personnel, Contacts, and Profile Matching sections

**Files:**
- Modify: `../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部 API 接口文档（revision）.md`
- Reference: `api-reference/personnel/list.mdx`
- Reference: `api-reference/personnel/profile.mdx`
- Reference: `api-reference/personnel/events.mdx`
- Reference: `api-reference/contacts/search.mdx`
- Reference: `api-reference/profile-matching/recommendations-events-paged.mdx`
- Reference: `api-reference/profile-matching/recommendations-exhibitors.mdx`

- [ ] **Step 1: Rewrite all Personnel and Contacts endpoint sections**

Endpoints:
- `GET /external/personnel/list`
- `GET /external/personnel/profile`
- `GET /external/personnel/events`
- `GET /external/contacts/search`

Expected:
- Personnel and Contacts sections match the Mintlify contract and preserve caller-facing notes

- [ ] **Step 2: Rewrite the Profile Matching endpoint sections and stale-route notes**

Endpoints:
- `POST /external/profile-matching/recommendations/events/paged`
- `GET /external/profile-matching/recommendations/exhibitors`

Also update any historical notes so:
- draft-only `job/start`
- draft-only `job/status`
- draft-only `GET /recommendations/events`

are not described as current live routes

Expected:
- Profile Matching is aligned to current live behavior and clearly marks the older draft routes as non-live history only

## Chunk 3: Replace The Reconciliation View

### Task 6: Rewrite the reconciliation artifact for the synchronized state

**Files:**
- Modify: `docs/reconciliation/external-api-pm-reconciliation.md`
- Reference: `docs/superpowers/specs/2026-03-24-external-api-pm-sync-design.md`
- Reference: `docs/endpoint-inventory/external-api-endpoints.md`
- Reference: `../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部 API 接口文档（revision）.md`

- [ ] **Step 1: Remove rows that assume the PM revision is still generally stale**

Remove or rewrite rows that still claim:
- revision uses `sk_...`
- revision is missing endpoints now present
- revision still presents old draft routes as live

Expected:
- no row contradicts the newly synchronized PM file

- [ ] **Step 2: Replace the artifact with a synchronized-state table**

The new table should document:
- `API-Doc` as source of truth
- PM `revision` as synchronized mirror
- any remaining intentional expression-only differences
- future maintenance order: update `API-Doc` first, then mirror PM `revision`

Expected:
- reconciliation becomes a maintenance artifact, not a stale discrepancy report

## Chunk 4: Verify Parity And Prepare Execution Closeout

### Task 7: Verify the PM file and reconciliation artifact against the sync checklist

**Files:**
- Verify: `../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部 API 接口文档（revision）.md`
- Verify: `docs/reconciliation/external-api-pm-reconciliation.md`

- [ ] **Step 1: Verify live-route inventory and stale-route handling**

Run:

```bash
rg -n "/external/" "../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部 API 接口文档（revision）.md"
rg -n "job/start|job/status|recommendations/events" "../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部 API 接口文档（revision）.md"
```

Expected:
- the 14 live endpoints are present
- old draft routes appear only in historical or non-live notes, not as implemented-now endpoints

- [ ] **Step 2: Verify auth and legacy-token wording**

Run:

```bash
rg -n "uak_|sk_" "../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部 API 接口文档（revision）.md"
rg -n "traceId|401 Unauthorized|400 Bad Request|409 Conflict" "../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部 API 接口文档（revision）.md"
```

Expected:
- `uak_...` is the active contract wording
- `sk_...` appears only if clearly marked historical
- error wording is compatible with the Mintlify shared contract

- [ ] **Step 3: Verify section completeness per endpoint**

Run:

```bash
rg -n "成功状态码|查询参数|请求体|响应示例|错误响应|说明" "../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部 API 接口文档（revision）.md"
```

Expected:
- each endpoint section includes the required contract subsections

- [ ] **Step 4: Verify the reconciliation artifact no longer reports stale-state mismatches**

Run:

```bash
rg -n "Missing from revision doc|Present in revision doc|sk_...|stale planned|Do not publish" docs/reconciliation/external-api-pm-reconciliation.md
sed -n '1,220p' docs/reconciliation/external-api-pm-reconciliation.md
```

Expected:
- the artifact reflects the synchronized state rather than the earlier discrepancy framing

- [ ] **Step 5: Review git diff for only the intended files**

Run:

```bash
git diff -- "../a60-lensmor-pm/工作流/研发设计/external-api-platform/外部 API 接口文档（revision）.md" docs/reconciliation/external-api-pm-reconciliation.md
git status --short
```

Expected:
- only the PM `revision` and reconciliation artifact are modified for this sync pass

- [ ] **Step 6: Commit the synchronized docs if commit history should be preserved in this session**

Run:

```bash
git add docs/reconciliation/external-api-pm-reconciliation.md
git commit -m "📝 docs(sync): refresh external api reconciliation"
```

And, in the PM repo if you are also preserving local history there:

```bash
git -C ../a60-lensmor-pm add "工作流/研发设计/external-api-platform/外部 API 接口文档（revision）.md"
git -C ../a60-lensmor-pm commit -m "📝 docs(external-api-platform): sync revision with api-doc"
```

Expected:
- commits are created only if the session intends to preserve the synchronization history now
