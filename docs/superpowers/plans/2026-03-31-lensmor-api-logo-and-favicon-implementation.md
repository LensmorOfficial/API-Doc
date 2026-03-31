# Lensmor API Logo and Favicon Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Mintlify `API-Doc` site show the Lensmor logo beside the `Lensmor API` name and use the same logo asset as the favicon.

**Architecture:** Keep this as a docs-repo-only branding change. Copy the upstream logo asset from the app repo into `API-Doc/logo.svg`, then point Mintlify `docs.json` at that single published asset for both `logo` and `favicon`.

**Tech Stack:** Mintlify `docs.json`, SVG static asset, shell copy/verification commands, ripgrep verification

---

### Task 1: Add the published logo asset

**Files:**
- Create: `logo.svg`
- Source reference: `../a60-lensmor-event-playground/public/assets/logo.svg`

- [ ] **Step 1: Verify the upstream logo asset exists and inspect its current SVG content**

Run: `test -f ../a60-lensmor-event-playground/public/assets/logo.svg && sed -n '1,20p' ../a60-lensmor-event-playground/public/assets/logo.svg`
Expected: file exists and prints the square SVG icon markup beginning with:

```svg
<svg width="240" height="240" viewBox="0 0 240 240" fill="none" xmlns="http://www.w3.org/2000/svg">
<rect width="240" height="240" fill="#0D0D0F"/>
```

- [ ] **Step 2: Copy the upstream asset into the docs repo as the published Mintlify logo**

Run: `cp ../a60-lensmor-event-playground/public/assets/logo.svg ./logo.svg`
Expected: `logo.svg` now exists in the `API-Doc` repo root

- [ ] **Step 3: Verify the copied file matches the upstream source exactly**

Run: `cmp -s ../a60-lensmor-event-playground/public/assets/logo.svg ./logo.svg && echo MATCH`
Expected: `MATCH`

- [ ] **Step 4: Review the published asset content before config changes**

Run: `sed -n '1,20p' ./logo.svg`
Expected: output matches the copied SVG icon markup, including:

```svg
<svg width="240" height="240" viewBox="0 0 240 240" fill="none" xmlns="http://www.w3.org/2000/svg">
<rect width="240" height="240" fill="#0D0D0F"/>
<path d="M110.625 82.5C84.7367 82.5 63.75 103.487 63.75 129.375C63.75 155.263 84.7367 176.25 110.625 176.25C136.513 176.25 157.5 155.263 157.5 129.375H176.25..." fill="white"/>
```

- [ ] **Step 5: Commit the asset addition**

Run:

```bash
git add logo.svg
git commit -m "docs: add lensmor logo asset for mintlify branding"
```

Expected: one commit created containing `logo.svg`

### Task 2: Point Mintlify branding and favicon at the shared logo

**Files:**
- Modify: `docs.json`

- [ ] **Step 1: Write the failing config diff by replacing the old favicon-only setup with shared logo branding**

Change `docs.json` from:

```json
{
  "$schema": "https://mintlify.com/docs.json",
  "name": "Lensmor API",
  "theme": "mint",
  "favicon": "/favicon.svg",
  "colors": {
```

To:

```json
{
  "$schema": "https://mintlify.com/docs.json",
  "name": "Lensmor API",
  "theme": "mint",
  "logo": {
    "light": "/logo.svg",
    "dark": "/logo.svg"
  },
  "favicon": "/logo.svg",
  "colors": {
```

- [ ] **Step 2: Verify the old config no longer points at `favicon.svg`**

Run: `rg -n 'favicon\.svg|"logo"|"favicon"' docs.json`
Expected:

```text
5:  "logo": {
6:    "light": "/logo.svg",
7:    "dark": "/logo.svg"
9:  "favicon": "/logo.svg",
```

- [ ] **Step 3: Validate the final `docs.json` shape around the branding block**

Run: `sed -n '1,20p' docs.json`
Expected: the top of the file shows the shared `logo` object and `favicon` both pointing to `/logo.svg`

- [ ] **Step 4: Commit the Mintlify config update**

Run:

```bash
git add docs.json
git commit -m "docs: configure mintlify logo and favicon"
```

Expected: one commit created containing only the `docs.json` branding change

### Task 3: Verify site behavior and final repo state

**Files:**
- Verify only

- [ ] **Step 1: Run a focused search to confirm the site uses the shared logo asset in config**

Run: `rg -n '"logo"|/logo\.svg|/favicon\.svg' docs.json`
Expected:

```text
5:  "logo": {
6:    "light": "/logo.svg",
7:    "dark": "/logo.svg"
9:  "favicon": "/logo.svg",
```

and no remaining `/favicon.svg` reference in `docs.json`

- [ ] **Step 2: Start the Mintlify preview and visually verify the brand area and browser tab**

Run: `pnpm dlx mintlify dev`
Expected: local Mintlify dev server starts successfully; in the browser, the site chrome shows the Lensmor logo beside `Lensmor API` and the browser tab favicon uses the same logo asset

- [ ] **Step 3: Review the final diff for scope control**

Run: `git diff -- logo.svg docs.json`
Expected: only two scoped changes appear — the new `logo.svg` file and the `docs.json` branding block update

- [ ] **Step 4: Check git status for the intended modified files only**

Run: `git status --short`
Expected:

```text
A  logo.svg
M  docs.json
```

before commits, or a clean working tree after the task commits are complete

- [ ] **Step 5: Commit the final verification pass if the workflow requires a single squashed docs commit instead of the per-task commits above**

Run:

```bash
git status --short
```

Expected: if per-task commits were used, no additional commit is needed; if the execution workflow batches changes instead, create one final docs commit with:

```bash
git add logo.svg docs.json
git commit -m "docs: align mintlify branding with lensmor app logo"
```
