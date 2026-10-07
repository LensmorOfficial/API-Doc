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

1. Create an account at [app.lensmor.com](https://app.lensmor.com/signup?utm_source=github&utm_medium=readme&utm_campaign=api-doc&utm_content=quickstart), upgrade to a paid subscription plan, then create a user API key from **Settings → API Keys**.
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

| Start here | Purpose |
| --- | --- |
| [Quickstart](https://api.lensmor.com/guides/quickstart) | Make your first authenticated request |
| [Authentication](authentication.mdx) | API key requirements and authorization format |
| [Find and unlock an event](guides/find-and-unlock-event.mdx) | Move from event discovery to event access |
| [Build attendee intelligence](guides/build-attendee-intelligence.mdx) | Interpret Exhibitor, Social Signals, and Visitor sources |
| [Credits and access](concepts/credits-and-access.mdx) | Understand preview access and credit-consuming actions |
| [Production readiness](guides/production-readiness.mdx) | Prepare an integration for reliable operation |
| [OpenAPI specification](openapi.json) | Machine-readable endpoint definitions |
| [API catalog](api-catalog.json) | Discover the machine-readable API resources |
| [llms.txt](llms.txt) · [llms-full.txt](llms-full.txt) | Agent-readable documentation |
| [Simplified Chinese guides](zh-Hans/index.mdx) | Core onboarding and access guidance in Chinese |

Use the [interactive API reference](https://api.lensmor.com/) to browse individual endpoints. The generated references are stored in `openapi.json` and its copies under `api-reference/` and `api-reference-backup/`.

## Typical use cases

- Build event discovery and field-marketing workflows
- Segment accessible attendees by Exhibitor, Social Signals, and registered Visitor source
- Match target accounts and exhibiting companies to relevant events
- Prioritize selected attendees and enrich their contact data for sales engagement or CRM workflows

## Help and contributions

Found a confusing example, missing explanation, or broken documentation link? [Open a documentation issue](https://github.com/LensmorOfficial/API-Doc/issues/new/choose) with the page URL, expected behavior, and a redacted example. For account or billing help, use the [Lensmor Help Center](https://help.lensmor.com/).

After editing documentation, run the local checks before opening a pull request:

```bash
python3 -m unittest scripts/test_sync_public_assets.py
python3 scripts/sync-public-assets.py --check
```

Generated public assets should be regenerated with `python3 scripts/sync-public-assets.py` when their source files change. The existing Docs Quality workflow checks the generated assets, OpenAPI, and Mintlify build on pull requests.

## Local preview

```bash
pnpm dlx mintlify dev
```

## Changelog

See `changelog.mdx` for versioned documentation updates. The current documentation version is `v0.27.0`.

---

Built by [Lensmor](https://www.lensmor.com/?utm_source=github&utm_medium=readme&utm_campaign=API-Doc) — AI-native event intelligence platform. Turn trade show data into qualified pipeline.
