# Lensmor API

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![API](https://img.shields.io/badge/API-REST-orange.svg)](https://www.lensmor.com/platform?utm_source=github&utm_medium=readme&utm_campaign=API-Doc)
[![Docs](https://img.shields.io/badge/Docs-api.lensmor.com-green.svg)](https://api.lensmor.com/)

Lensmor provides developer-facing access to event, exhibitor, personnel, contact, and profile-matching data through a public API contract under `https://platform.lensmor.com/external/*`.

This repository hosts the public documentation site for developers integrating with [Lensmor](https://www.lensmor.com/?utm_source=github&utm_medium=readme&utm_campaign=API-Doc) — an AI-native event intelligence platform for B2B teams.

## Why Lensmor API

Use the API to:

- Browse and inspect event data
- Search exhibitors using company context and optional event scope
- Retrieve exhibitor and personnel profiles
- Search contacts with company-based inputs
- Request profile-matching recommendations for discovery workflows

## Base URL

`https://platform.lensmor.com`

All documented paths are relative to this base URL. For example:

- `GET /external/events/list`
- `POST /external/exhibitors/search`

## Quick start

1. Obtain a valid user API key. API access is available to paying customers — contact [hello@lensmor.com](mailto:hello@lensmor.com) to purchase.
2. Send requests to `https://platform.lensmor.com`.
3. Include the authorization header on every request.
4. Browse the full interactive docs at **[api.lensmor.com](https://api.lensmor.com/)** or use the reference files in this repository.

```http
Authorization: Bearer uak_your_api_key
```

## Example request

```bash
curl -X GET "https://platform.lensmor.com/external/events/list?page=1&pageSize=20" \
  -H "Authorization: Bearer uak_your_api_key"
```

## Main documentation entry points

- `index.mdx` — overview and quick start
- `authentication.mdx` — authentication and authorization format
- `concepts/errors.mdx` — shared error conventions
- `concepts/pagination.mdx` — pagination behavior
- `api-reference/events/` — event endpoints
- `api-reference/exhibitors/` — exhibitor endpoints
- `api-reference/personnel/` — personnel endpoints
- `api-reference/contacts/` — contact search endpoints
- `api-reference/profile-matching/` — recommendation endpoints

## Typical use cases

- Build event discovery workflows
- Match exhibitors to a company profile or target audience
- Enrich sales, partnership, or market research pipelines
- Explore people and organizations connected to relevant events

## Scope

This documentation reflects the current public API contract only. It excludes internal implementation details and historical draft references that are not part of the external developer experience.

---

Built by [Lensmor](https://www.lensmor.com/?utm_source=github&utm_medium=readme&utm_campaign=API-Doc) — AI-native event intelligence platform. Turn trade show data into qualified pipeline.
