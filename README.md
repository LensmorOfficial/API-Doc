# Lensmor API

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![API](https://img.shields.io/badge/API-REST-orange.svg)](https://www.lensmor.com/platform?utm_source=github&utm_medium=readme&utm_campaign=API-Doc)
[![Docs](https://img.shields.io/badge/Docs-api.lensmor.com-green.svg)](https://api.lensmor.com/)

Lensmor provides developer-facing access to event, exhibitor, attendee-source, registered Visitor, contact, and profile-matching data through the Lensmor API.

This repository hosts the public documentation site for developers integrating with [Lensmor](https://www.lensmor.com/?utm_source=github&utm_medium=readme&utm_campaign=API-Doc) — an AI-native event intelligence platform for B2B teams.

## Why Lensmor API

Use the API to:

- Check credit balance before running credit-consuming workflows
- Browse and inspect event data
- Build attendee intelligence with Exhibitor, Social Signals, and registered Visitor source labels
- Search exhibitors using company context and optional event scope
- Retrieve exhibitor and personnel profiles
- Search contacts with company-based inputs and unlock contact emails
- Request profile-matching recommendations for discovery workflows

## Base URL

`https://platform.lensmor.com`

All documented paths are relative to this base URL. For example:

- `GET /external/events/list`
- `POST /external/exhibitors/search`

## Quick start

1. Create an account at [app.lensmor.com](https://app.lensmor.com), upgrade to a paid subscription plan, then create a user API key from **Settings → API Keys**.
2. Send requests to `https://platform.lensmor.com`.
3. Include the authorization header on every request.
4. Browse the full interactive docs at **[api.lensmor.com](https://api.lensmor.com/)** or use the reference files in this repository.

```http
Authorization: Bearer sk_your_api_key
```

## Example request

```bash
curl -X GET "https://platform.lensmor.com/external/events/list?page=1&pageSize=20" \
  -H "Authorization: Bearer sk_your_api_key"
```

## Main documentation entry points

- `index.mdx` — overview and quick start
- `authentication.mdx` — authentication and authorization format
- `openapi.json` — OpenAPI 3.1 specification for documented endpoints
- `api-catalog.json` — machine-readable API catalog pointing to the OpenAPI file
- `llms.txt` and `llms-full.txt` — LLM-friendly documentation entry points
- `zh-Hans/` — Simplified Chinese core onboarding, attendee, access, and contact-unlock guides
- `api-reference/credits/` — credit balance endpoint
- `concepts/errors.mdx` — shared error conventions
- `concepts/pagination.mdx` — pagination behavior
- `concepts/identifiers.mdx` — identifier conventions
- `concepts/attendee-source-types.mdx` — product-to-API attendee source mapping and multi-source behavior
- `concepts/credits-and-access.mdx` — credit costs, preview access, and unlock behavior
- `concepts/rate-limits.mdx` — rate-limit headers and `429` behavior
- `api-reference/events/` — event endpoints
- `api-reference/exhibitors/` — exhibitor endpoints
- `api-reference/personnel/` — personnel endpoints
- `api-reference/contacts/` — contact search and email unlock endpoints
- `api-reference/profile-matching/` — recommendation endpoints

## Typical use cases

- Build event discovery and field-marketing workflows
- Segment accessible attendees by Exhibitor, Social Signals, and registered Visitor source
- Match target accounts and exhibiting companies to relevant events
- Prioritize selected attendees and enrich their contact data for sales engagement or CRM workflows

## Local preview

```bash
pnpm dlx mintlify dev
```

## Changelog

See `changelog.mdx` for versioned documentation updates. The current documentation version is `v0.26.0`.

---

Built by [Lensmor](https://www.lensmor.com/?utm_source=github&utm_medium=readme&utm_campaign=API-Doc) — AI-native event intelligence platform. Turn trade show data into qualified pipeline.
