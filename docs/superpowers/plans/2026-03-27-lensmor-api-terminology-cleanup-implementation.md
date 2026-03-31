# Lensmor API Terminology Cleanup Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove explicit `External` product naming from the public docs while preserving the implemented `/external/*` endpoint paths.

**Architecture:** Treat this as a docs-layer terminology cleanup. Update the Mintlify site name and all public natural-language references that surface `External` as part of the product identity, but leave literal route paths and internal implementation/source-truth references unchanged.

**Tech Stack:** Mintlify `docs.json`, MDX documentation pages, ripgrep verification, Git diff review

---

### Task 1: Update site identity and entry-point copy

**Files:**
- Modify: `docs.json`
- Modify: `index.mdx`

- [ ] **Step 1: Rename the published site to `Lensmor API`**

- [ ] **Step 2: Rewrite the homepage introduction so `/external/*` appears only as the literal route prefix**

- [ ] **Step 3: Verify no public entry-point copy still uses `Lensmor External API`**

Run: `rg -n "Lensmor External API" docs.json index.mdx`
Expected: no matches

### Task 2: Rewrite shared-concept wording

**Files:**
- Modify: `authentication.mdx`
- Modify: `concepts/errors.mdx`
- Modify: `concepts/pagination.mdx`

- [ ] **Step 1: Replace public-facing `external` terminology with neutral API wording**

- [ ] **Step 2: Keep `/external/*` only where the docs are naming the actual implemented routes**

- [ ] **Step 3: Verify shared pages no longer present `External API` as the product name**

Run: `rg -n "External API|external error contract|External responses|External identifiers" authentication.mdx concepts/errors.mdx concepts/pagination.mdx`
Expected: no matches

### Task 3: Rewrite endpoint-page prose

**Files:**
- Modify: `api-reference/**/*.mdx`

- [ ] **Step 1: Update endpoint summaries, parameter notes, and note sections that use natural-language `external` terminology**

- [ ] **Step 2: Leave literal endpoint strings such as `GET /external/...` untouched**

- [ ] **Step 3: Verify remaining `external` matches in public endpoint files are either route literals or intentionally internal-source wording**

Run: `rg -n "External|external" api-reference`
Expected: matches are limited to `/external/*` route strings or intentionally retained wording approved by the design

### Task 4: Final verification

**Files:**
- Verify only

- [ ] **Step 1: Review the final diff for accidental route changes**

Run: `git diff -- docs.json index.mdx authentication.mdx concepts api-reference`
Expected: copy changes only; `/external/*` route literals unchanged

- [ ] **Step 2: Run a final search sweep across public docs**

Run: `rg -n "Lensmor External API|External API" docs.json *.mdx concepts api-reference`
Expected: no matches
