# External API MDX Refresh From Inventory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update all external API MDX reference pages so they match the approved self-contained contract in `docs/endpoint-inventory/external-api-endpoints.md`.

**Architecture:** Treat `docs/endpoint-inventory/external-api-endpoints.md` as the only Phase 2 contract source. Rewrite the 17 endpoint MDX pages to align with the new inventory structure and details, keeping endpoint pages self-contained and consistent. Do not re-derive contracts from scattered source notes, and do not change backend code.

**Tech Stack:** Mintlify MDX pages, `docs.json` navigation, markdown tables, ripgrep verification, git diff review

---

### Task 1: Lock the Phase 2 source of truth

**Files:**
- Read only: `docs/endpoint-inventory/external-api-endpoints.md`
- Read only: `docs.json`

- [ ] **Step 1: Verify the inventory is the approved Phase 2 source**

Run:
```bash
rg -n "^## (GET|POST) /external/" \
  "/Users/linnan/Documents/Projects/a60-lensmor/API-Doc/docs/endpoint-inventory/external-api-endpoints.md"
```
Expected: `17` endpoint headings in the inventory

- [ ] **Step 2: Verify the published MDX page list from docs navigation**

Run:
```bash
python3 - <<'PY'
import json
from pathlib import Path
p = Path('/Users/linnan/Documents/Projects/a60-lensmor/API-Doc/docs.json')
data = json.loads(p.read_text())
for tab in data['navigation']['tabs']:
    for group in tab['groups']:
        if group['group'] == 'API Reference':
            print(group)
PY
```
Expected: the navigation still lists the 17 external API pages to update

- [ ] **Step 3: Confirm this phase only updates endpoint MDX pages**

Phase boundary:
```text
Modify only api-reference/**/*.mdx endpoint pages.
Do not modify docs/endpoint-inventory/external-api-endpoints.md in this phase unless a typo in the inventory blocks exact alignment.
```

### Task 2: Rewrite the Events MDX pages from the inventory

**Files:**
- Modify: `api-reference/events/list.mdx`
- Modify: `api-reference/events/fit-score.mdx`
- Modify: `api-reference/events/rank.mdx`
- Modify: `api-reference/events/brief.mdx`
- Modify: `api-reference/events/detail.mdx`
- Read only: `docs/endpoint-inventory/external-api-endpoints.md`

- [ ] **Step 1: Rewrite `api-reference/events/list.mdx` to match the inventory exactly**

Required page structure:
```mdx
# Events list

<short purpose>

## Endpoint
`GET /external/events/list`

## Authentication
See [Authentication](/authentication)

## Success status code
`200 OK`

## Query parameters
...

## Response body
### Top-level fields
...
### `items[]` fields
...

## Response example
```json
...
```

## Error responses
...

## Notes
...
```

- [ ] **Step 2: Apply the same contract-first rewrite to the other four Events pages**

Required page files:
```text
api-reference/events/fit-score.mdx
api-reference/events/rank.mdx
api-reference/events/brief.mdx
api-reference/events/detail.mdx
```

- [ ] **Step 3: Verify the five Events pages now include response body field tables**

Run:
```bash
rg -n "^## Response body|^### Top-level fields|^### `items\[\]` fields|^### `item` fields" \
  "/Users/linnan/Documents/Projects/a60-lensmor/API-Doc/api-reference/events"
```
Expected: each Events page contains explicit response body sections, not just endpoint and example sections

### Task 3: Rewrite the Exhibitors MDX pages from the inventory

**Files:**
- Modify: `api-reference/exhibitors/list.mdx`
- Modify: `api-reference/exhibitors/search.mdx`
- Modify: `api-reference/exhibitors/search-by-company-name.mdx`
- Modify: `api-reference/exhibitors/search-events.mdx`
- Modify: `api-reference/exhibitors/profile.mdx`
- Modify: `api-reference/exhibitors/events.mdx`
- Read only: `docs/endpoint-inventory/external-api-endpoints.md`

- [ ] **Step 1: Rewrite all six Exhibitors pages so each one is self-contained**

Required sections per page:
```md
## Endpoint
## Authentication
## Success status code
## Path parameters (if applicable)
## Query parameters (if applicable)
## Request body (if applicable)
## Response body
## Response example
## Error responses
## Notes
```

- [ ] **Step 2: Preserve inventory-backed caveats in page Notes instead of dropping them**

Required note themes to carry through where applicable:
```md
- empty success responses instead of `404`
- `matched_event_ids` array behavior
- `techStacks` array behavior
```

- [ ] **Step 3: Verify all six Exhibitors pages expose request and response structure explicitly**

Run:
```bash
rg -n "^## (Query parameters|Request body|Response body|Notes)" \
  "/Users/linnan/Documents/Projects/a60-lensmor/API-Doc/api-reference/exhibitors"
```
Expected: the exhibitor pages contain explicit contract sections rather than example-only documentation

### Task 4: Rewrite the Personnel and Contacts MDX pages from the inventory

**Files:**
- Modify: `api-reference/personnel/list.mdx`
- Modify: `api-reference/personnel/profile.mdx`
- Modify: `api-reference/personnel/events.mdx`
- Modify: `api-reference/contacts/search.mdx`
- Read only: `docs/endpoint-inventory/external-api-endpoints.md`

- [ ] **Step 1: Rewrite the three Personnel pages to match the inventory’s request/response structure**

Required files:
```text
api-reference/personnel/list.mdx
api-reference/personnel/profile.mdx
api-reference/personnel/events.mdx
```

- [ ] **Step 2: Rewrite `api-reference/contacts/search.mdx` to the same self-contained structure**

Required minimum page shape:
```md
# Contacts search

## Endpoint
`GET /external/contacts/search`

## Authentication
See [Authentication](/authentication)

## Success status code
`200 OK`

## Query parameters
...

## Response body
...
```

- [ ] **Step 3: Verify all four pages now contain explicit response body sections**

Run:
```bash
rg -n "^## Response body" \
  "/Users/linnan/Documents/Projects/a60-lensmor/API-Doc/api-reference/personnel" \
  "/Users/linnan/Documents/Projects/a60-lensmor/API-Doc/api-reference/contacts"
```
Expected: four matches, one per page

### Task 5: Rewrite the Profile Matching MDX pages from the inventory

**Files:**
- Modify: `api-reference/profile-matching/recommendations-events-paged.mdx`
- Modify: `api-reference/profile-matching/recommendations-exhibitors.mdx`
- Read only: `docs/endpoint-inventory/external-api-endpoints.md`

- [ ] **Step 1: Rewrite the paged events recommendations page from the inventory**

Required content to preserve from inventory if present:
```md
- conditional request requirements such as `company_url` vs `target_audience`
- top-level recommendation metadata like `status`, `profile_version`, `active_result_version`, `is_stale`
- nested recommendation item fields
```

- [ ] **Step 2: Rewrite the exhibitors recommendations page from the inventory**

Required content to preserve from inventory if present:
```md
- query/body contract shape used by the endpoint
- response body field tables
- route-specific Notes for identifier mapping or nullable fields
```

- [ ] **Step 3: Verify both profile-matching pages are self-contained**

Run:
```bash
rg -n "^## (Request body|Query parameters|Response body|Response example|Notes)" \
  "/Users/linnan/Documents/Projects/a60-lensmor/API-Doc/api-reference/profile-matching"
```
Expected: both pages include full contract sections and do not rely on external source docs

### Task 6: Normalize endpoint page structure across all 17 MDX files

**Files:**
- Modify: `api-reference/**/*.mdx`

- [ ] **Step 1: Ensure every endpoint page starts with the same top-level contract sequence**

Required order:
```md
# Title
<short purpose>
## Endpoint
## Authentication
## Success status code
```

- [ ] **Step 2: Ensure parameter sections appear only when relevant, but response sections always appear**

Required invariant:
```text
Every endpoint page must include:
- Response body
- Response example
- Error responses
- Notes
```

- [ ] **Step 3: Verify the section order is consistent across the full API reference set**

Run:
```bash
rg -n "^## (Endpoint|Authentication|Success status code|Path parameters|Query parameters|Request body|Response body|Response example|Error responses|Notes)" \
  "/Users/linnan/Documents/Projects/a60-lensmor/API-Doc/api-reference"
```
Expected: all endpoint pages follow the same section vocabulary and roughly the same order

### Task 7: Final verification for the MDX refresh

**Files:**
- Verify only: `api-reference/**/*.mdx`
- Verify only: `docs.json`
- Verify only: `docs/endpoint-inventory/external-api-endpoints.md`

- [ ] **Step 1: Verify every MDX endpoint page still matches a docs.json navigation entry**

Run:
```bash
rg -n '"api-reference/' \
  "/Users/linnan/Documents/Projects/a60-lensmor/API-Doc/docs.json"
```
Expected: all 17 endpoint pages are still listed in navigation

- [ ] **Step 2: Review the final diff to confirm this phase only changes endpoint MDX pages**

Run:
```bash
git -C "/Users/linnan/Documents/Projects/a60-lensmor/API-Doc" diff -- api-reference docs.json docs/endpoint-inventory/external-api-endpoints.md
```
Expected: substantive changes appear in `api-reference/**/*.mdx`; `docs.json` and the inventory remain unchanged unless a small alignment fix was absolutely necessary

- [ ] **Step 3: Run a final search to ensure no MDX page still depends on response-sources wording**

Run:
```bash
rg -n "response-sources|source document|source-of-truth note" \
  "/Users/linnan/Documents/Projects/a60-lensmor/API-Doc/api-reference"
```
Expected: no matches
