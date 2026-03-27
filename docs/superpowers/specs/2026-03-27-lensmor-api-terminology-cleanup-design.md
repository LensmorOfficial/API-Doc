# Lensmor API Terminology Cleanup Design

Date: 2026-03-27

## Goal

Remove the explicit `External` product naming from the public Mintlify documentation so the published site consistently presents itself as `Lensmor API`.

The actual implemented HTTP routes remain unchanged under `/external/*`. This effort is terminology cleanup in the documentation layer only.

## Scope

This effort includes:

- `docs.json` site name
- top-level public pages such as `index.mdx`, `authentication.mdx`, and shared concepts pages
- public endpoint-page prose in `api-reference/**/*.mdx`

This effort does not include:

- changing any request path, method, or parameter name
- changing code-source tracking documents under `docs/`
- renaming internal implementation references such as `external-api`
- updating PM sync artifacts or historical design/plan documents

## Terminology Rules

- Use `Lensmor API` as the product/site name
- Avoid `External API` as a public-facing product label
- Keep `/external/*` only when referring to the literal implemented route path
- Keep `external-api` only when referring to internal code modules or source-truth references
- Replace natural-language phrases such as `external error contract`, `external event identifier`, and `external contact result set` with neutral public wording such as `API error contract`, `event identifier`, or `contact result set`

## Affected Content Areas

### Site identity

- Site title in `docs.json`
- Homepage heading and introduction

### Shared conventions

- Authentication wording
- Error-contract wording
- Pagination/identifier wording

### Endpoint prose

- Summary paragraphs
- parameter descriptions
- notes sections

Endpoint code snippets, literal paths, and examples remain unchanged unless they contain an avoidable natural-language `External` label.

## Validation

After editing:

- `Lensmor External API` should no longer appear in public docs
- public-facing natural-language `External API` references should be replaced with `Lensmor API` or neutral wording
- literal `/external/*` paths must still remain intact
- internal `docs/` artifacts may still contain `External` because they document implementation history rather than the published site
