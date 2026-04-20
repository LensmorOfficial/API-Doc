# External API Endpoint Inventory

## Rules
- Source of truth for method/path: controllers
- Source of truth for request contracts: controller + DTO
- Source of truth for response contracts: service + mapper + runtime output shape
- Source of truth for auth/error behavior: runtime middleware and external error path
- Tests are not used as contract evidence in this document

## Shared runtime truths
- Authorization header format: `Authorization: Bearer uak_...`
- Bearer scheme stripping is case-insensitive at runtime
- All current external controller routes require authentication through the external API auth flow
- External error responses use the public envelope `{ code, message, errorKey, traceId }`
- Paginated success responses use `{ items, total, page, pageSize, totalPages, hasMore }`, with `totalPages: 0` when `total` is `0`

## Endpoint table
| Method | Path | Controller file | Auth required | Success status | Published in Mintlify | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| GET | /external/events/list | `src/modules/external-api/controllers/external-events.controller.ts` | Yes | `200 OK` | Yes | No implicit date window is applied; date filters only run when provided |
| POST | /external/events/fit-score | `src/modules/external-api/controllers/external-events.controller.ts` | Yes | `201 Created` | Yes | `event_id` accepts either `Event.eventId` or internal `Event.id` |
| POST | /external/events/rank | `src/modules/external-api/controllers/external-events.controller.ts` | Yes | `201 Created` | Yes | `event_ids` accepts either `Event.eventId` or internal `Event.id` |
| POST | /external/events/:id/unlock | `src/modules/external-api/controllers/external-events.controller.ts` | Yes | `201 Created` | Yes | Idempotent event-level unlock; returns `400 Bad Request` when the event has no chargeable contacts |
| GET | /external/events/brief | `src/modules/external-api/controllers/external-events.controller.ts` | Yes | `200 OK` | Yes | `event_id` accepts either `Event.eventId` or internal `Event.id` |
| GET | /external/events/:id | `src/modules/external-api/controllers/external-events.controller.ts` | Yes | `200 OK` | Yes | Path `:id` accepts either internal row `id` or external `eventId` |
| GET | /external/exhibitors/list | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | `200 OK` | Yes | `event_id` accepts either `Event.eventId` or internal `Event.id` |
| POST | /external/exhibitors/search | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | `201 Created` | Yes | Requires `company_url`, `target_audience`, or both; no-match cases stay `200/201` success with empty items |
| POST | /external/exhibitors/search-by-company-name | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | `201 Created` | Yes | Precision-first paged lookup by `company_name` |
| POST | /external/exhibitors/search-events | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | `201 Created` | Yes | Charge-sensitive reverse lookup from `company_name`; longer queries ignore single-character tokens and use strict token/prefix admission |
| GET | /external/exhibitors/profile | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | `200 OK` | Yes | `exhibitor_id` is a numeric string |
| GET | /external/exhibitors/events | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | `200 OK` | Yes | `exhibitor_id` is a numeric string |
| GET | /external/personnel/list | `src/modules/external-api/controllers/external-personnel.controller.ts` | Yes | `200 OK` | Yes | `event_id` accepts either `Event.eventId` or internal `Event.id`; response now includes preview/full-access `semantics` guidance |
| GET | /external/personnel/profile | `src/modules/external-api/controllers/external-personnel.controller.ts` | Yes | `200 OK` | Yes | `personnel_id` is a numeric string; the profile includes user-scoped unlock state |
| GET | /external/personnel/events/by-linkedin | `src/modules/external-api/controllers/external-personnel.controller.ts` | Yes | `200 OK` | Yes | `linkedin_url` normalizes to a LinkedIn profile URL, then returns the matched personnel profile with user-scoped unlock state plus paginated associated events |
| GET | /external/personnel/events | `src/modules/external-api/controllers/external-personnel.controller.ts` | Yes | `200 OK` | Yes | `personnel_id` is a numeric string |
| GET | /external/contacts/search | `src/modules/external-api/controllers/external-contacts.controller.ts` | Yes | `200 OK` | Yes | Search is scoped to the authenticated user context, supports optional `person_name`, and may expose unlocked email state |
| POST | /external/contacts/unlock | `src/modules/external-api/controllers/external-contacts.controller.ts` | Yes | `201 Created` | Yes | Queues an asynchronous email unlock batch for event-scoped personnel IDs |
| GET | /external/contacts/unlock-tasks/:taskId | `src/modules/external-api/controllers/external-contacts.controller.ts` | Yes | `200 OK` | Yes | Returns aggregate batch status plus per-person unlock progress |
| POST | /external/profile-matching/recommendations/events/paged | `src/modules/external-api/controllers/external-profile-matching.controller.ts` | Yes | `201 Created` | Yes | Runs synchronous apply-onboarding, then returns paged recommended events |
| GET | /external/profile-matching/recommendations/exhibitors | `src/modules/external-api/controllers/external-profile-matching.controller.ts` | Yes | `200 OK` | Yes | `event_id` accepts either `Event.eventId` or internal `Event.id` |
| POST | /external/actions/precheck | `src/modules/external-api/controllers/external-actions.controller.ts` | Yes | `200 OK` | Yes | Returns allow/charge truth in-body, including preview unlock guidance and `no_contacts_available` for event unlock prechecks |

## GET /external/events/list

### Authentication
Bearer token required.

### Success status code
`200 OK`

### Query parameters
| Name | Required | Type | Notes |
| --- | --- | --- | --- |
| `page` | No | integer | Defaults to `1`. |
| `pageSize` | No | integer | Defaults to `20`, max `100`. |
| `keyword` | No | string | Free-text event search. |
| `country` | No | string | Country filter. |
| `city` | No | string | City filter. |
| `date_start_from` | No | `YYYY-MM-DD` string | Optional lower date bound. |
| `date_start_to` | No | `YYYY-MM-DD` string | Optional upper date bound. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `items` | object[] | Event summaries for the current page. |
| `total` | integer | Total matched rows. |
| `page` | integer | Current page number. |
| `pageSize` | integer | Page size used at runtime. |
| `totalPages` | integer | `0` when `total` is `0`. |
| `hasMore` | boolean | `true` when another page exists. |

#### `items[]` fields
| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Internal event row identifier. |
| `eventId` | string | External event identifier. |
| `name` | string | Event name. |
| `nickname` | string or `null` | Event short name. |
| `description` | string or `null` | Event description. |
| `url` | string or `null` | Event website URL. |
| `dateStart` | `YYYY-MM-DD` string or `null` | Start date. |
| `dateEnd` | `YYYY-MM-DD` string or `null` | End date. |
| `venue` | string or `null` | Venue name. |
| `city` | string or `null` | City. |
| `region` | string or `null` | Region or state. |
| `country` | string or `null` | Country. |
| `exhibitorCount` | integer or `null` | Exhibitor count snapshot. |
| `image` | string or `null` | Image URL. |
| `dataSource` | string or `null` | Upstream data source label. |

### Response example
```json
{
  "items": [
    {
      "id": "123",
      "eventId": "139574",
      "name": "Shoptalk",
      "nickname": null,
      "description": null,
      "url": "https://example.com",
      "dateStart": "2026-03-25",
      "dateEnd": "2026-03-28",
      "venue": "Convention Center",
      "city": "Las Vegas",
      "region": "Nevada",
      "country": "United States",
      "exhibitorCount": 250,
      "image": null,
      "dataSource": "vendelux"
    }
  ],
  "total": 1,
  "page": 1,
  "pageSize": 20,
  "totalPages": 1,
  "hasMore": false
}
```

### Error responses
- `401 Unauthorized` when the API key is missing, malformed, or invalid.

### Notes
- The route applies date filters only when `date_start_from` and/or `date_start_to` are supplied; no implicit default date window is added at runtime.
- List-summary items intentionally omit `attendeeCount` and `personnelCount`; those values were removed from this response because they were inaccurate in list context.

## POST /external/events/fit-score

### Authentication
Bearer token required.

### Success status code
`201 Created`

### Request body
| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `event_id` | Yes | string | Supports either external `Event.eventId` or internal `Event.id`. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `event` | object | Same event summary shape as `GET /external/events/list` `items[]`. |
| `score` | number | Normalized to a `0.0`-`10.0` style scale. |
| `recommendation` | string | One of `recommended`, `consider`, or `not_recommended`. |
| `breakdown` | object | Contains `profile_match`, `matched_exhibitor_density`, and `event_scale`. |

### Response example
```json
{
  "event": {
    "id": "123",
    "eventId": "139574",
    "name": "Shoptalk",
    "nickname": null,
    "description": null,
    "url": "https://example.com",
    "dateStart": "2026-03-25",
    "dateEnd": "2026-03-28",
    "venue": "Convention Center",
    "city": "Las Vegas",
    "region": "Nevada",
    "country": "United States",
    "exhibitorCount": 250,
    "image": null,
    "dataSource": "vendelux"
  },
  "score": 7.8,
  "recommendation": "recommended",
  "breakdown": {
    "profile_match": 7.8,
    "matched_exhibitor_density": 2.4,
    "event_scale": 2.5
  }
}
```

### Error responses
- `400 Bad Request` when `event_id` is missing or invalid.
- `401 Unauthorized` when the API key is missing, malformed, or invalid.
- `404 Not Found` when the target event cannot be resolved.
- `409 Conflict` when the recommendation dependency is still processing.

### Notes
- `event_id` accepts either the internal row `id` or external `eventId`.

## POST /external/events/rank

### Authentication
Bearer token required.

### Success status code
`201 Created`

### Request body
| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `event_ids` | Yes | string[] | Each value supports either external `Event.eventId` or internal `Event.id`. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `items` | object[] | Ranked event summaries in descending match-score order. |

#### `items[]` fields
| Field | Type | Notes |
| --- | --- | --- |
| `event_id` | string | External event identifier. |
| `name` | string | Event name. |
| `rank` | integer | One-based rank in the returned order. |
| `match_score` | number | Raw profile score rounded to two decimals. |
| `reasons` | array | Currently returned as an empty array. |

### Response example
```json
{
  "items": [
    {
      "event_id": "139574",
      "name": "Shoptalk",
      "rank": 1,
      "match_score": 0.82,
      "reasons": []
    }
  ]
}
```

### Error responses
- `400 Bad Request` when any `event_ids` entry is invalid.
- `401 Unauthorized` when the API key is missing, malformed, or invalid.
- `404 Not Found` when any requested event cannot be resolved.
- `409 Conflict` when the recommendation dependency is still processing.

### Notes
- `POST /external/events/rank` currently returns an empty `reasons` array for each item.

## POST /external/events/:id/unlock

### Authentication
Bearer token required.

### Success status code
`201 Created`

### Path parameters
| Name | Required | Type | Notes |
| --- | --- | --- | --- |
| `id` | Yes | string | Supports either internal `Event.id` or external `Event.eventId`. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `success` | boolean | Currently always `true` when the execute step completes. |
| `alreadyUnlocked` | boolean | `true` when the caller already had event-level access. |
| `creditsUsed` | integer | `0` on idempotent repeats; otherwise the charged event-unlock amount. |
| `balanceAfter` | object or `null` | Remaining balances after a charged unlock, or `null` when no charge was needed. |
| `event` | object | Identity of the unlocked event. |

#### `balanceAfter` fields
| Field | Type | Notes |
| --- | --- | --- |
| `subscriptionBalance` | integer | Remaining subscription credits. |
| `permanentBalance` | integer | Remaining gift/permanent credits. |
| `totalBalance` | integer | Remaining total credits. |
| `unlimited` | boolean | Currently `false`. |

#### `event` fields
| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Internal event row identifier. |
| `eventId` | string | External event identifier. |
| `name` | string | Event name. |

### Response example
```json
{
  "success": true,
  "alreadyUnlocked": false,
  "creditsUsed": 2000,
  "balanceAfter": {
    "subscriptionBalance": 18000,
    "permanentBalance": 0,
    "totalBalance": 18000,
    "unlimited": false
  },
  "event": {
    "id": "123",
    "eventId": "139574",
    "name": "Shoptalk"
  }
}
```

### Error responses
- `400 Bad Request` when the event exists but has no chargeable contacts to unlock.
- `401 Unauthorized` when the API key is missing, malformed, or invalid.
- `402 Payment Required` when the caller lacks sufficient credits for an event unlock.
- `404 Not Found` when the target event cannot be resolved.
- `409 Conflict` when another credit operation is already in progress for this caller.

### Notes
- `:id` accepts either the internal row `id` or the external `eventId`.
- Repeating the same unlock is idempotent: the route returns `alreadyUnlocked: true`, `creditsUsed: 0`, and `balanceAfter: null`.
- The route only succeeds when the event still has chargeable contacts; otherwise it fails fast with `400 Bad Request`.
- Successful charged unlocks return the remaining credit balances alongside the event identity.

## GET /external/events/brief

### Authentication
Bearer token required.

### Success status code
`200 OK`

### Query parameters
| Name | Required | Type | Notes |
| --- | --- | --- | --- |
| `event_id` | Yes | string | Supports either external `Event.eventId` or internal `Event.id`. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `event` | object | Same event summary shape as `GET /external/events/list` `items[]`. |
| `summary` | object | Brief rollup metadata. |

#### `summary` fields
| Field | Type | Notes |
| --- | --- | --- |
| `attendeeCount` | integer | Defaults to `0` when absent in storage or when the event has no personnel relations. |
| `exhibitorCount` | integer | Defaults to `0` when absent in storage. |
| `personnelCount` | integer | Defaults to `0` when absent in storage or when the event has no personnel relations. |
| `topCategories` | array | Currently returned as an empty array. |
| `dataFreshness` | string | Currently hard-coded to `database_snapshot`. |

### Response example
```json
{
  "event": {
    "id": "123",
    "eventId": "139574",
    "name": "Shoptalk",
    "nickname": null,
    "description": null,
    "url": "https://example.com",
    "dateStart": "2026-03-25",
    "dateEnd": "2026-03-28",
    "venue": "Convention Center",
    "city": "Las Vegas",
    "region": "Nevada",
    "country": "United States",
    "exhibitorCount": 250,
    "image": null,
    "dataSource": "vendelux"
  },
  "summary": {
    "attendeeCount": 10000,
    "exhibitorCount": 250,
    "personnelCount": 1800,
    "topCategories": [],
    "dataFreshness": "database_snapshot"
  }
}
```

### Error responses
- `400 Bad Request` when `event_id` is invalid.
- `401 Unauthorized` when the API key is missing, malformed, or invalid.
- `404 Not Found` when the target event cannot be resolved.

### Notes
- `GET /external/events/brief` currently returns `topCategories` as an empty array.

## GET /external/events/:id

### Authentication
Bearer token required.

### Success status code
`200 OK`

### Path parameters
| Name | Required | Type | Notes |
| --- | --- | --- | --- |
| `id` | Yes | string | Accepts either internal event row `id` or external `eventId`. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `event` | object | Detailed event payload. |

#### `event` fields
| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Internal event row identifier. |
| `eventId` | string | External event identifier. |
| `name` | string or `null` | Event name. |
| `nickname` | string or `null` | Event short name. |
| `description` | string or `null` | Event description. |
| `url` | string or `null` | Event website URL. |
| `dateStart` | `YYYY-MM-DD` string or `null` | Start date. |
| `dateEnd` | `YYYY-MM-DD` string or `null` | End date. |
| `venue` | string or `null` | Venue name. |
| `city` | string or `null` | City. |
| `region` | string or `null` | Region or state. |
| `country` | string or `null` | Country. |
| `latitude` | string or `null` | Latitude rendered as a string. |
| `longitude` | string or `null` | Longitude rendered as a string. |
| `attendeeCount` | integer or `null` | `null` when the event has no personnel relations; otherwise defaults to `0` when absent. |
| `declaredExpectedAttendees` | string or `null` | Declared attendance expectation rendered as a string. |
| `estimatedExpectedAttendees` | string or `null` | Estimated attendance expectation rendered as a string. |
| `priceLower` | string or `null` | Lower ticket price rendered as a string. |
| `priceUpper` | string or `null` | Upper ticket price rendered as a string. |
| `eventType` | string or `null` | Primary event-type label. |
| `categories` | object[] | Event category metadata. |
| `topics` | string[] | Topics array parsed from stored JSON or string data. |
| `topicsCount` | integer | Topic count. |
| `verified` | integer | Verification flag. |
| `future` | integer | Future-event flag. |
| `historic` | integer | Historic-event flag. |
| `historicEvent` | string or `null` | Historic event marker. |
| `image` | string or `null` | Image URL. |
| `dataSource` | string or `null` | Upstream data source label. |
| `exhibitorCount` | integer | Defaults to `0` when absent. |
| `personnelCount` | integer or `null` | `null` when the event has no personnel relations; otherwise defaults to `0` when absent. |
| `eventTypes` | object[] | Detailed event-type rows. |

#### `event.categories[]` fields
| Field | Type | Notes |
| --- | --- | --- |
| `id` | integer | Category identifier. |
| `code` | string | Category code. |
| `name` | string | Category name. |
| `description` | string or `null` | Category description. |
| `confidence` | string or `null` | Confidence rendered as a string. |

#### `event.eventTypes[]` fields
| Field | Type | Notes |
| --- | --- | --- |
| `id` | integer | Event type identifier. |
| `typeName` | string | Event type name. |
| `slug` | string | Event type slug. |
| `isPrimary` | boolean | Primary-type marker. |

### Response example
```json
{
  "event": {
    "id": "123",
    "eventId": "139574",
    "name": "Shoptalk",
    "nickname": null,
    "description": null,
    "url": "https://example.com",
    "dateStart": "2026-03-25",
    "dateEnd": "2026-03-28",
    "venue": "Convention Center",
    "city": "Las Vegas",
    "region": "Nevada",
    "country": "United States",
    "latitude": "36.1147",
    "longitude": "-115.1728",
    "attendeeCount": 10000,
    "declaredExpectedAttendees": null,
    "estimatedExpectedAttendees": null,
    "priceLower": null,
    "priceUpper": null,
    "eventType": null,
    "categories": [],
    "topics": [],
    "topicsCount": 0,
    "verified": 1,
    "future": 1,
    "historic": 0,
    "historicEvent": null,
    "image": null,
    "dataSource": "vendelux",
    "exhibitorCount": 250,
    "personnelCount": 1800,
    "eventTypes": []
  }
}
```

### Error responses
- `401 Unauthorized` when the API key is missing, malformed, or invalid.
- `404 Not Found` when the target event cannot be resolved.

### Notes
- `GET /external/events/:id` accepts either the internal row `id` or external `eventId` in the `:id` segment.
- Numeric `:id` values are resolved against internal `Event.id` first, then retried as external `eventId`.
- `attendeeCount` and `personnelCount` may be `null` on detail responses when the event has no personnel relations.

## GET /external/exhibitors/list

### Authentication
Bearer token required.

### Success status code
`200 OK`

### Query parameters
| Name | Required | Type | Notes |
| --- | --- | --- | --- |
| `event_id` | Yes | string | Supports either external `Event.eventId` or internal `Event.id`. |
| `page` | No | integer | Defaults to `1`. |
| `pageSize` | No | integer | Defaults to `20`, max `100`. |
| `keyword` | No | string | Exhibitor search term for the event. |
| `country` | No | string | Exhibitor country filter. |
| `category` | No | string[] | Exhibitor category filters; repeated query params are supported. |
| `industry` | No | string[] | Exhibitor industry filters; repeated query params are supported. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `items` | object[] | Exhibitors associated with the resolved event. |
| `total` | integer | Total matched exhibitors. |
| `page` | integer | Current page number. |
| `pageSize` | integer | Page size used at runtime. |
| `totalPages` | integer | `0` when `total` is `0`. |
| `hasMore` | boolean | `true` when another page exists. |

#### `items[]` fields
| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Internal exhibitor row identifier. |
| `companyName` | string | Exhibitor company name. |
| `domain` | string or `null` | Exhibitor domain. |
| `description` | string or `null` | Exhibitor description. |
| `website` | string or `null` | Website URL. |
| `industry` | string or `null` | Industry label. |
| `employeeCount` | integer or `null` | Employee-count snapshot. |
| `country` | string or `null` | Country. |
| `logo` | string or `null` | Logo URL. |
| `dataSource` | string or `null` | Upstream data source label. |
| `linkedinUrl` | string or `null` | LinkedIn URL. |
| `fundingRound` | string or `null` | Funding-round label. |
| `matched_event_ids` | string[] | For this route, contains the resolved event's external `eventId`. |
| `techStacks` | string[] | Normalized tech-stack names. |
| `categories` | string[] | Optional. Exhibitor categories. Event-scoped when the upstream query is event-scoped. Present only when non-empty. |

### Response example
```json
{
  "items": [
    {
      "id": "456",
      "companyName": "Acme",
      "domain": "acme.com",
      "description": null,
      "website": "https://acme.com",
      "industry": "Retail Technology",
      "employeeCount": 120,
      "country": "United States",
      "logo": null,
      "dataSource": "vendelux",
      "linkedinUrl": null,
      "fundingRound": null,
      "matched_event_ids": [
        "139574"
      ],
      "techStacks": [
        "React",
        "PostgreSQL"
      ],
      "categories": [
        "Retail",
        "Fintech"
      ]
    }
  ],
  "total": 1,
  "page": 1,
  "pageSize": 20,
  "totalPages": 1,
  "hasMore": false
}
```

### Error responses
- `400 Bad Request` when `event_id` is invalid or list filters fail validation.
- `401 Unauthorized` when the API key is missing, malformed, or invalid.
- `404 Not Found` when the target event cannot be resolved.

### Notes
- Request-side `event_id` can be either the external event identifier or internal row id, while response-side event references remain in `matched_event_ids`.

## POST /external/exhibitors/search

### Authentication
Bearer token required.

### Success status code
`201 Created`

### Request body
| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `company_url` | Conditionally | string | Optional URL; at least one of `company_url` or `target_audience` is required. |
| `target_audience` | Conditionally | string | Optional free-text audience string; at least one of `company_url` or `target_audience` is required. |
| `page` | No | integer | Defaults to `1`. |
| `pageSize` | No | integer | Defaults to `20`, max `100`. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `items` | object[] | Same exhibitor summary shape as `GET /external/exhibitors/list` `items[]`. |
| `total` | integer | Total matched exhibitors after the resolver search. |
| `page` | integer | Current page number. |
| `pageSize` | integer | Page size used at runtime. |
| `totalPages` | integer | `0` when `total` is `0`. |
| `hasMore` | boolean | `true` when another page exists. |

### Response example
```json
{
  "items": [
    {
      "id": "456",
      "companyName": "Acme",
      "domain": "acme.com",
      "description": null,
      "website": "https://acme.com",
      "industry": "Retail Technology",
      "employeeCount": 120,
      "country": "United States",
      "logo": null,
      "dataSource": "vendelux",
      "linkedinUrl": null,
      "fundingRound": null,
      "matched_event_ids": [],
      "techStacks": [
        "React"
      ],
      "categories": [
        "Retail"
      ]
    }
  ],
  "total": 1,
  "page": 1,
  "pageSize": 20,
  "totalPages": 1,
  "hasMore": false
}
```

### Error responses
- `400 Bad Request` when neither `company_url` nor `target_audience` is provided, or `company_url` is not a valid URL.
- `401 Unauthorized` when the API key is missing, malformed, or invalid.

### Notes
- No matches return an empty success response rather than `404`.
- `company_url` is reduced to its hostname with leading `www.` removed before the runtime builds the domain filter.
- If both `company_url` and `target_audience` are sent, `target_audience` drives the company-name search string while the extracted domain is still applied as an exact filter.
- `matched_event_ids` is an empty array when no event scope or match data exists.
- `techStacks` is always returned as an array.

## POST /external/exhibitors/search-by-company-name

### Authentication
Bearer token required.

### Success status code
`201 Created`

### Request body
| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `company_name` | Yes | string | Precision-first exhibitor lookup term. |
| `page` | No | integer | Defaults to `1`. |
| `pageSize` | No | integer | Defaults to `20`, max `100`. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `items` | object[] | Same exhibitor summary shape as `GET /external/exhibitors/list` `items[]`. |
| `total` | integer | Total matched exhibitors for the paged strict search. |
| `page` | integer | Current page number. |
| `pageSize` | integer | Page size used at runtime. |
| `totalPages` | integer | `0` when `total` is `0`. |
| `hasMore` | boolean | `true` when another page exists. |

### Response example
```json
{
  "items": [
    {
      "id": "456",
      "companyName": "Acme",
      "domain": null,
      "description": null,
      "website": null,
      "industry": "Retail Technology",
      "employeeCount": null,
      "country": null,
      "logo": null,
      "dataSource": null,
      "linkedinUrl": null,
      "fundingRound": null,
      "matched_event_ids": [],
      "techStacks": [],
      "categories": []
    }
  ],
  "total": 1,
  "page": 1,
  "pageSize": 20,
  "totalPages": 1,
  "hasMore": false
}
```

### Error responses
- `400 Bad Request` when `company_name` is empty or invalid.
- `401 Unauthorized` when the API key is missing, malformed, or invalid.

### Notes
- No matches return an empty success response rather than `404`.
- `matched_event_ids` is an empty array when no event scope or match data exists.
- `techStacks` is always returned as an array.

## POST /external/exhibitors/search-events

### Authentication
Bearer token required.

### Success status code
`201 Created`

### Request body
| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `company_name` | Yes | string | Reverse-lookup source string. |
| `page` | No | integer | Defaults to `1`. |
| `pageSize` | No | integer | Defaults to `20`, max `100`. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `items` | object[] | Event summaries enriched with matching exhibitor stubs. |
| `total` | integer | Total matched events. |
| `page` | integer | Current page number. |
| `pageSize` | integer | Page size used at runtime. |
| `totalPages` | integer | `0` when `total` is `0`. |
| `hasMore` | boolean | `true` when another page exists. |

#### `items[]` fields
| Field | Type | Notes |
| --- | --- | --- |
| All event summary fields | object | Same event summary shape as `GET /external/events/list` `items[]`. |
| `matchedExhibitors` | object[] | Matching exhibitors for this event page row. |

#### `items[].matchedExhibitors[]` fields
| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Internal exhibitor row identifier. |
| `companyName` | string | Matching exhibitor company name. |

### Response example
```json
{
  "items": [
    {
      "id": "123",
      "eventId": "139574",
      "name": "Shoptalk",
      "nickname": null,
      "description": null,
      "url": "https://example.com",
      "dateStart": "2026-03-25",
      "dateEnd": "2026-03-28",
      "venue": "Convention Center",
      "city": "Las Vegas",
      "region": "Nevada",
      "country": "United States",
      "exhibitorCount": 250,
      "image": null,
      "dataSource": "vendelux",
      "matchedExhibitors": [
        {
          "id": "456",
          "companyName": "Acme"
        }
      ]
    }
  ],
  "total": 1,
  "page": 1,
  "pageSize": 20,
  "totalPages": 1,
  "hasMore": false
}
```

### Error responses
- `400 Bad Request` when `company_name` is empty or invalid.
- `401 Unauthorized` when the API key is missing, malformed, or invalid.
- `402 Payment Required` when the caller lacks sufficient credits for the search charge.

### Notes
- The route consumes `50` credits on execution; if downstream search logic throws, the service refunds that charge.
- No matches return an empty success response rather than `404`.
- Short queries stay exact-only after normalization; longer queries ignore single-character company tokens and use strict token and prefix admission instead of permissive substring matching.

## GET /external/exhibitors/profile

### Authentication
Bearer token required.

### Success status code
`200 OK`

### Query parameters
| Name | Required | Type | Notes |
| --- | --- | --- | --- |
| `exhibitor_id` | Yes | string | Numeric-string exhibitor identifier. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Internal exhibitor row identifier. |
| `companyName` | string | Exhibitor company name. |
| `domain` | string or `null` | Exhibitor domain. |
| `description` | string or `null` | Exhibitor description. |
| `website` | string or `null` | Website URL. |
| `industry` | string or `null` | Industry label. |
| `employeeCount` | integer or `null` | Employee-count snapshot. |
| `country` | string or `null` | Country. |
| `logo` | string or `null` | Logo URL. |
| `dataSource` | string or `null` | Upstream data source label. |
| `linkedinUrl` | string or `null` | LinkedIn URL. |
| `fundingRound` | string or `null` | Funding-round label. |
| `matched_event_ids` | string[] | Empty unless explicit match scope is attached to the source object. |
| `categories` | string[] | Optional. Exhibitor categories. Present only when non-empty. |
| `events` | object[] | First page of associated events, limited to 20 rows. |

#### `events[]` fields
| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Internal event row identifier. |
| `eventId` | string | External event identifier. |
| `name` | string | Event name. |

### Response example
```json
{
  "id": "456",
  "companyName": "Acme",
  "domain": "acme.com",
  "description": null,
  "website": "https://acme.com",
  "industry": "Retail Technology",
  "employeeCount": 120,
  "country": "United States",
  "logo": null,
  "dataSource": "vendelux",
  "linkedinUrl": null,
  "fundingRound": null,
  "matched_event_ids": [],
  "categories": [
    "Retail"
  ],
  "events": [
    {
      "id": "123",
      "eventId": "139574",
      "name": "Shoptalk"
    }
  ]
}
```

### Error responses
- `400 Bad Request` when `exhibitor_id` is not a valid numeric string.
- `401 Unauthorized` when the API key is missing, malformed, or invalid.
- `404 Not Found` when the exhibitor cannot be resolved.

### Notes
- `matched_event_ids` is an empty array when no event scope or match data exists.
- The embedded `events` array is not paginated; it is populated from the first 20 associated events only.

## GET /external/exhibitors/events

### Authentication
Bearer token required.

### Success status code
`200 OK`

### Query parameters
| Name | Required | Type | Notes |
| --- | --- | --- | --- |
| `exhibitor_id` | Yes | string | Numeric-string exhibitor identifier. |
| `page` | No | integer | Defaults to `1`. |
| `pageSize` | No | integer | Defaults to `20`, max `100`. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `items` | object[] | Same event summary shape as `GET /external/events/list` `items[]`. |
| `total` | integer | Total associated events. |
| `page` | integer | Current page number. |
| `pageSize` | integer | Page size used at runtime. |
| `totalPages` | integer | `0` when `total` is `0`. |
| `hasMore` | boolean | `true` when another page exists. |

### Response example
```json
{
  "items": [
    {
      "id": "123",
      "eventId": "139574",
      "name": "Shoptalk",
      "nickname": null,
      "description": null,
      "url": "https://example.com",
      "dateStart": "2026-03-25",
      "dateEnd": "2026-03-28",
      "venue": "Convention Center",
      "city": "Las Vegas",
      "region": "Nevada",
      "country": "United States",
      "exhibitorCount": 250,
      "image": null,
      "dataSource": "vendelux"
    }
  ],
  "total": 1,
  "page": 1,
  "pageSize": 20,
  "totalPages": 1,
  "hasMore": false
}
```

### Error responses
- `400 Bad Request` when `exhibitor_id` is not a valid numeric string.
- `401 Unauthorized` when the API key is missing, malformed, or invalid.
- `404 Not Found` when the exhibitor cannot be resolved.

### Notes
- Request-side `exhibitor_id` is snake_case, while response-side identifiers remain `id` and `eventId`.

## GET /external/personnel/list

### Authentication
Bearer token required.

### Success status code
`200 OK`

### Query parameters
| Name | Required | Type | Notes |
| --- | --- | --- | --- |
| `event_id` | Yes | string | Supports either external `Event.eventId` or internal `Event.id`. |
| `page` | No | integer | Defaults to `1`. |
| `pageSize` | No | integer | Defaults to `20`, max `100`. |
| `exhibitor_id` | No | string | Optional numeric-string exhibitor filter. |
| `department` | No | string | Case-insensitive department filter. |
| `level` | No | string | Case-insensitive management-level filter. |
| `search_query` | No | string | Matches relation `position` text or personnel full name. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `items` | object[] | Personnel contact summaries for the event. |
| `total` | integer | Total distinct personnel matches. |
| `page` | integer | Current page number. |
| `pageSize` | integer | Page size used at runtime. |
| `totalPages` | integer | `0` when `total` is `0`. |
| `hasMore` | boolean | `true` when another page exists. |
| `semantics` | object | Event-access semantics describing preview/full mode, accessible paging, and unlock guidance. |

#### `items[]` fields
| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Internal personnel row identifier. |
| `fullName` | string | Full name. |
| `title` | string or `null` | For this route, sourced from the event-personnel relation `jobTitle`. |
| `department` | string or `null` | Department value. |
| `seniorityLevel` | string or `null` | Seniority or level value. |
| `linkedinUrl` | string or `null` | LinkedIn URL. |
| `companyName` | string or `null` | Associated exhibitor company name. |
| `sourceType` | string or `null` | Source label. |
| `email` | string or `null` | Email when this caller has already unlocked the contact; otherwise `null`. |
| `contactUnlockStatus` | string | User-scoped contact state. Current complete enum: `locked`, `unlocking`, `unlocked`, `failed`. |

#### `semantics` fields
| Field | Type | Notes |
| --- | --- | --- |
| `accessMode` | string | `preview` when the event is still preview-locked, `full` when the caller already has full event access. |
| `previewLimit` | integer or `null` | Currently `50` in preview mode; `null` in full mode. |
| `counts` | object | Actual-versus-visible match counts for the current query. |
| `pageState` | object | Whether the requested page is currently accessible. |
| `unlock` | object | Whether event unlock is required to see more results. |
| `guidance` | object | User-facing machine-readable guidance for the current access state. |

#### `semantics.counts` fields
| Field | Type | Notes |
| --- | --- | --- |
| `actualTotal` | integer | Total matching personnel for the current query before preview gating. |
| `visibleTotal` | integer | Total currently accessible under the present access mode. |
| `remainingLockedCount` | integer | Count of matching personnel that remain inaccessible until event unlock. |

#### `semantics.pageState` fields
| Field | Type | Notes |
| --- | --- | --- |
| `requestedPage` | integer | Echoes the requested page number. |
| `accessible` | boolean | `false` when the requested page falls outside the preview-accessible window. |
| `maxAccessiblePage` | integer | Highest page currently accessible under the present access mode. |

#### `semantics.unlock` fields
| Field | Type | Notes |
| --- | --- | --- |
| `requiredForMoreResults` | boolean | `true` when event unlock is required to continue beyond the current preview boundary. |
| `actionType` | string or `null` | Recommended follow-up action type, currently `unlock_event_contacts` when unlock is needed. |
| `credits` | integer or `null` | Credits required by the recommended unlock action when present, currently `2000`. |

#### `semantics.guidance` fields
| Field | Type | Notes |
| --- | --- | --- |
| `code` | string | Current codes include `preview_page_inaccessible`, `preview_results_truncated`, `preview_complete_for_query`, `full_access`, and `no_matching_results`. |
| `message` | string | Human-readable explanation of the current access state. |

### Response example
```json
{
  "items": [
    {
      "id": "789",
      "fullName": "Jane Doe",
      "title": "VP Marketing",
      "department": "Marketing",
      "seniorityLevel": "vp",
      "linkedinUrl": "https://linkedin.com/in/jane-doe",
      "companyName": "Acme",
      "sourceType": "exhibitor",
      "email": null,
      "contactUnlockStatus": "locked"
    }
  ],
  "total": 237,
  "page": 1,
  "pageSize": 20,
  "totalPages": 12,
  "hasMore": true,
  "semantics": {
    "accessMode": "preview",
    "previewLimit": 50,
    "counts": {
      "actualTotal": 237,
      "visibleTotal": 50,
      "remainingLockedCount": 187
    },
    "pageState": {
      "requestedPage": 1,
      "accessible": true,
      "maxAccessiblePage": 1
    },
    "unlock": {
      "requiredForMoreResults": true,
      "actionType": "unlock_event_contacts",
      "credits": 2000
    },
    "guidance": {
      "code": "preview_results_truncated",
      "message": "This event is locked. Only the first 50 matching personnel are currently accessible. Unlock the event to access the remaining matching results."
    }
  }
}
```

### Error responses
- `400 Bad Request` when `event_id` or `exhibitor_id` is invalid.
- `401 Unauthorized` when the API key is missing, malformed, or invalid.
- `404 Not Found` when the target event cannot be resolved.

### Notes
- Request-side identifiers use `event_id` and optional `exhibitor_id`, while response-side identifiers use only `id`.
- `title` comes from the event-scoped personnel relation, while `email` and `contactUnlockStatus` are user-scoped overlays computed for the authenticated caller.
- `search_query` matches either relation `position` text or personnel `fullName`.
- `semantics` exposes whether the caller is in preview or full-access mode for this event, including unlock guidance and actual-versus-visible result counts.
- When `semantics.pageState.accessible` is `false`, the route can return an empty page while `semantics.counts.actualTotal` still shows more matching results behind the preview boundary.

## GET /external/personnel/profile

### Authentication
Bearer token required.

### Success status code
`200 OK`

### Query parameters
| Name | Required | Type | Notes |
| --- | --- | --- | --- |
| `personnel_id` | Yes | string | Numeric-string personnel identifier. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Internal personnel row identifier. |
| `fullName` | string | Full name. |
| `title` | string or `null` | Sourced from `personnel.bio`. |
| `department` | string or `null` | Department value. |
| `seniorityLevel` | string or `null` | Seniority or level value. |
| `linkedinUrl` | string or `null` | LinkedIn URL. |
| `companyName` | string or `null` | Latest current exhibitor association, if any. |
| `sourceType` | string or `null` | Source label. |
| `email` | string or `null` | Email when this caller has already unlocked the contact; otherwise `null`. |
| `contactUnlockStatus` | string | User-scoped contact state. Current complete enum: `locked`, `unlocking`, `unlocked`, `failed`. |

### Response example
```json
{
  "id": "789",
  "fullName": "Jane Doe",
  "title": "VP Marketing",
  "department": "Marketing",
  "seniorityLevel": "vp",
  "linkedinUrl": "https://linkedin.com/in/jane-doe",
  "companyName": "Acme",
  "sourceType": "exhibitor",
  "email": null,
  "contactUnlockStatus": "locked"
}
```

### Error responses
- `400 Bad Request` when `personnel_id` is not a valid numeric string.
- `401 Unauthorized` when the API key is missing, malformed, or invalid.
- `404 Not Found` when the personnel row cannot be resolved.

### Notes
- Request-side `personnel_id` differs from the response-side `id` field.
- `title` is sourced from `personnel.bio`, while `companyName` reflects the latest current exhibitor association.
- `email` and `contactUnlockStatus` are user-scoped and may differ across callers.

## GET /external/personnel/events/by-linkedin

### Authentication
Bearer token required.

### Success status code
`200 OK`

### Query parameters
| Name | Required | Type | Notes |
| --- | --- | --- | --- |
| `linkedin_url` | Yes | string | Must normalize to a valid LinkedIn profile URL. Query strings, fragments, and trailing slashes are ignored during matching. |
| `page` | No | integer | Defaults to `1`. |
| `pageSize` | No | integer | Defaults to `20`, max `100`. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `personnel` | object | Same personnel profile shape as `GET /external/personnel/profile`. |
| `events` | object | Same paginated event-list shape as `GET /external/personnel/events`. |

#### `personnel` fields
| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Internal personnel row identifier. |
| `fullName` | string | Full name. |
| `title` | string or `null` | Sourced from `personnel.bio`. |
| `department` | string or `null` | Department value. |
| `seniorityLevel` | string or `null` | Seniority or level value. |
| `linkedinUrl` | string or `null` | LinkedIn URL. |
| `companyName` | string or `null` | Latest current exhibitor association, if any. |
| `sourceType` | string or `null` | Source label. |
| `email` | string or `null` | Email when this caller has already unlocked the contact; otherwise `null`. |
| `contactUnlockStatus` | string | User-scoped contact state. Current complete enum: `locked`, `unlocking`, `unlocked`, `failed`. |

#### `events` fields
| Field | Type | Notes |
| --- | --- | --- |
| `items` | object[] | Same event summary shape as `GET /external/events/list` `items[]`. |
| `total` | integer | Total distinct associated events. |
| `page` | integer | Current page number. |
| `pageSize` | integer | Page size used at runtime. |
| `totalPages` | integer | `0` when `total` is `0`. |
| `hasMore` | boolean | `true` when another page exists. |

### Response example
```json
{
  "personnel": {
    "id": "789",
    "fullName": "Jane Doe",
    "title": "VP Marketing",
    "department": "Marketing",
    "seniorityLevel": "vp",
    "linkedinUrl": "https://linkedin.com/in/jane-doe",
    "companyName": "Acme",
    "sourceType": "exhibitor",
    "email": null,
    "contactUnlockStatus": "locked"
  },
  "events": {
    "items": [
      {
        "id": "123",
        "eventId": "139574",
        "name": "Shoptalk",
        "nickname": null,
        "description": null,
        "url": "https://example.com",
        "dateStart": "2026-03-25",
        "dateEnd": "2026-03-28",
        "venue": "Convention Center",
        "city": "Las Vegas",
        "region": "Nevada",
        "country": "United States",
        "exhibitorCount": 250,
        "image": null,
        "dataSource": "vendelux"
      }
    ],
    "total": 1,
    "page": 1,
    "pageSize": 20,
    "totalPages": 1,
    "hasMore": false
  }
}
```

### Error responses
- `400 Bad Request` when `linkedin_url` is missing or does not normalize to a valid LinkedIn profile URL.
- `401 Unauthorized` when the API key is missing, malformed, or invalid.
- `404 Not Found` when no personnel row can be resolved from the normalized LinkedIn URL.

### Notes
- Runtime matching normalizes the URL to `https://linkedin.com/in/<slug>` form before lookup.
- `personnel` reuses the same profile shape as `GET /external/personnel/profile`, including user-scoped `email` and `contactUnlockStatus`.
- If the personnel row exists but has no exhibitor associations, `events` returns an empty paginated success response instead of `404`.

## GET /external/personnel/events

### Authentication
Bearer token required.

### Success status code
`200 OK`

### Query parameters
| Name | Required | Type | Notes |
| --- | --- | --- | --- |
| `personnel_id` | Yes | string | Numeric-string personnel identifier. |
| `page` | No | integer | Defaults to `1`. |
| `pageSize` | No | integer | Defaults to `20`, max `100`. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `items` | object[] | Same event summary shape as `GET /external/events/list` `items[]`. |
| `total` | integer | Total distinct associated events. |
| `page` | integer | Current page number. |
| `pageSize` | integer | Page size used at runtime. |
| `totalPages` | integer | `0` when `total` is `0`. |
| `hasMore` | boolean | `true` when another page exists. |

### Response example
```json
{
  "items": [
    {
      "id": "123",
      "eventId": "139574",
      "name": "Shoptalk",
      "nickname": null,
      "description": null,
      "url": "https://example.com",
      "dateStart": "2026-03-25",
      "dateEnd": "2026-03-28",
      "venue": "Convention Center",
      "city": "Las Vegas",
      "region": "Nevada",
      "country": "United States",
      "exhibitorCount": 250,
      "image": null,
      "dataSource": "vendelux"
    }
  ],
  "total": 1,
  "page": 1,
  "pageSize": 20,
  "totalPages": 1,
  "hasMore": false
}
```

### Error responses
- `400 Bad Request` when `personnel_id` is not a valid numeric string.
- `401 Unauthorized` when the API key is missing, malformed, or invalid.
- `404 Not Found` when the personnel row cannot be resolved.

### Notes
- If the personnel row exists but has no exhibitor associations, the route returns an empty paginated success response instead of `404`.

## GET /external/contacts/search

### Authentication
Bearer token required.

### Success status code
`200 OK`

### Query parameters
| Name | Required | Type | Notes |
| --- | --- | --- | --- |
| `company_name` | Yes | string | Company lookup term. Length `1` to `200`. |
| `role` | No | string | Optional position or role filter. Blank values are normalized away. |
| `person_name` | No | string | Optional person-name filter. Blank values are normalized away. |
| `page` | No | integer | Defaults to `1`. |
| `pageSize` | No | integer | Defaults to `20`, max `100`. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `items` | object[] | Contact-style personnel summaries for the company query. |
| `total` | integer | Total distinct personnel matches. |
| `page` | integer | Current page number. |
| `pageSize` | integer | Page size used at runtime. |
| `totalPages` | integer | `0` when `total` is `0`. |
| `hasMore` | boolean | `true` when another page exists. |

#### `items[]` fields
| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Internal personnel row identifier. |
| `fullName` | string | Full name. |
| `title` | string or `null` | Title or position summary. |
| `department` | string or `null` | Department value. |
| `seniorityLevel` | string or `null` | Seniority or level value. |
| `linkedinUrl` | string or `null` | LinkedIn URL. |
| `companyName` | string or `null` | Company name. |
| `sourceType` | string or `null` | Source label. |
| `email` | string or `null` | Email when this caller has already unlocked the contact; otherwise `null`. |
| `contactUnlockStatus` | string | User-scoped contact state. Current complete enum: `locked`, `unlocking`, `unlocked`, `failed`. |

### Response example
```json
{
  "items": [
    {
      "id": "789",
      "fullName": "Jane Doe",
      "title": "VP Marketing",
      "department": "Marketing",
      "seniorityLevel": "vp",
      "linkedinUrl": "https://linkedin.com/in/jane-doe",
      "companyName": "Acme",
      "sourceType": "exhibitor",
      "email": null,
      "contactUnlockStatus": "locked"
    }
  ],
  "total": 1,
  "page": 1,
  "pageSize": 20,
  "totalPages": 1,
  "hasMore": false
}
```

### Error responses
- `400 Bad Request` when `company_name` is empty or invalid.
- `401 Unauthorized` when the API key is missing, malformed, or invalid.

### Notes
- Request-side `company_name` is snake_case, while response-side fields are camelCase.
- `person_name` can narrow the company-scoped result set by personnel name without requiring an event context.
- `email` and `contactUnlockStatus` are user-scoped; unlocked emails are only returned for the authenticated caller that has already unlocked them.
- Short company queries use a direct contains-style fallback; longer company queries use scored matching.
- Results are scoped to the authenticated user because the service computes user-specific reveal and task state before mapping the response.

## POST /external/contacts/unlock

### Authentication
Bearer token required.

### Success status code
`201 Created`

### Request body
| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `personnel_ids` | Yes | string[] | One or more personnel IDs to unlock. Duplicate values are deduplicated before precheck and charging. |
| `event_id` | Yes | string | Supports either external `Event.eventId` or internal `Event.id`. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `status` | string | Currently `accepted` when the async job is queued. |
| `task_id` | string | Async unlock task identifier. |
| `job_id` | string | Alias of `task_id`. |

### Response example
```json
{
  "status": "accepted",
  "task_id": "901",
  "job_id": "901"
}
```

### Error responses
- `400 Bad Request` when the body is invalid or the requested personnel are not valid for the supplied event.
- `401 Unauthorized` when the API key is missing, malformed, or invalid.
- `402 Payment Required` when the caller lacks credits for the requested unlock batch.
- `404 Not Found` when the target event or one of the requested personnel rows cannot be resolved.
- `409 Conflict` when one or more requested contacts are already unlocked or currently unlocking.

### Notes
- The route queues an asynchronous email unlock batch; use `GET /external/contacts/unlock-tasks/:taskId` to poll the returned `task_id`.
- The request is event-scoped: every `personnel_id` must belong to the supplied `event_id`.
- A `201 Created` response means the batch was accepted for processing, not that emails are already available.

## GET /external/contacts/unlock-tasks/:taskId

### Authentication
Bearer token required.

### Success status code
`200 OK`

### Path parameters
| Name | Required | Type | Notes |
| --- | --- | --- | --- |
| `taskId` | Yes | string | Async task identifier returned by `POST /external/contacts/unlock`. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `taskId` | string | Echoes the requested task identifier. |
| `taskStatus` | string | Aggregate batch status: `pending`, `processing`, `completed`, or `failed`. |
| `items` | object[] | Per-person async unlock progress. |

#### `items[]` fields
| Field | Type | Notes |
| --- | --- | --- |
| `personnelId` | string | Target personnel identifier. |
| `status` | string | Per-person status: `pending`, `processing`, `unlocked`, or `failed`. |
| `email` | string or `null` | Email when `status` is `unlocked`; otherwise omitted or `null`. |
| `errorCode` | string | Failure code when available, such as `TASK_NOT_FOUND` or `TASK_FAILED`. |

### Response example
```json
{
  "taskId": "901",
  "taskStatus": "completed",
  "items": [
    {
      "personnelId": "789",
      "status": "unlocked",
      "email": "jane.doe@example.com"
    },
    {
      "personnelId": "790",
      "status": "failed",
      "errorCode": "TASK_FAILED"
    }
  ]
}
```

### Error responses
- `401 Unauthorized` when the API key is missing, malformed, or invalid.
- `404 Not Found` when the unlock task cannot be resolved for the authenticated caller.

### Notes
- `taskStatus` maps internal task-center states to `pending`, `processing`, `completed`, or `failed`.
- `email` is returned only for items whose status is `unlocked`.
- If an underlying per-person subtask record is missing, the item surfaces as `status: "failed"` with `errorCode: "TASK_NOT_FOUND"`.

## POST /external/profile-matching/recommendations/events/paged

### Authentication
Bearer token required.

### Success status code
`201 Created`

### Request body
| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `company_url` | Conditionally | string | Optional public `http(s)` URL. At least one of `company_url` or `target_audience` is required. |
| `target_audience` | Conditionally | string | Optional audience description. At least one of `company_url` or `target_audience` is required. |
| `timeout_ms` | No | integer | Optional synchronous onboarding timeout, min `60000`, max `3600000`. |
| `page` | No | integer | Defaults to `1`. |
| `pageSize` | No | integer | Defaults to `20`, max `100`. |
| `city` | No | string | Exact city filter. |
| `region` | No | string | Exact region filter. |
| `country` | No | string | Exact country filter. |
| `category` | No | string[] | Category filters; accepts an array or a comma-separated string. |
| `eventTypeIds` | No | integer[] | Event type filters; accepts an array or a comma-separated string. |
| `dateStartFrom` | No | `YYYY-MM-DD` string | Lower date bound. |
| `dateStartTo` | No | `YYYY-MM-DD` string | Upper date bound. |
| `future` | No | integer | Future-only flag. |
| `attendeeCountMin` | No | integer | Minimum attendee count. |
| `attendeeCountMax` | No | integer | Maximum attendee count. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `status` | string | One of `processing`, `failed`, `completed_empty`, or `completed`. |
| `items` | object[] | Recommended events for the current page. |
| `total` | integer | Total merged recommended events after filtering. |
| `page` | integer | Current page number. |
| `pageSize` | integer | Page size used at runtime. |
| `totalPages` | integer | `0` when `total` is `0`. |
| `hasMore` | boolean | `true` when another page exists. |
| `condition_tags` | object | Structured filter conditions for downstream rendering. |
| `parsed_filters_snapshot` | object, optional | Parsed filter snapshot, when available. |
| `relaxed_conditions` | object, optional | Currently used for relaxed-matching metadata. |
| `profile_version` | integer | Current profile version. |
| `active_result_version` | integer or `null` | Active recommendation snapshot version. |
| `is_stale` | boolean | `true` when recalculation is in progress over an older active snapshot. |
| `empty_reason` | string, optional | Empty-result reason when status is empty or failed. |
| `failed_filters` | string[], optional | Filters that did not match. |
| `candidate_count` | integer, optional | Candidate count before semantic matching. |
| `suggestions` | string[], optional | Suggested filter adjustments. |

#### `items[]` fields
| Field | Type | Notes |
| --- | --- | --- |
| `id` | integer | Internal event row identifier. |
| `eventId` | string | External event identifier. |
| `name` | string or `null` | Event name. |
| `nickname` | string or `null` | Event short name. |
| `description` | string or `null` | Event description. |
| `url` | string or `null` | Event website URL. |
| `dateStart` | `YYYY-MM-DD` string or `null` | Start date. |
| `dateEnd` | `YYYY-MM-DD` string or `null` | End date. |
| `venue` | string or `null` | Venue name. |
| `city` | string or `null` | City. |
| `region` | string or `null` | Region or state. |
| `country` | string or `null` | Country. |
| `latitude` | string or `null` | Latitude rendered as a string. |
| `longitude` | string or `null` | Longitude rendered as a string. |
| `attendeeCount` | integer | Attendance count. |
| `declaredExpectedAttendees` | integer | Declared attendance expectation. |
| `estimatedExpectedAttendees` | string or `null` | Estimated attendance expectation rendered as a string. |
| `priceLower` | string or `null` | Lower ticket price rendered as a string. |
| `priceUpper` | string or `null` | Upper ticket price rendered as a string. |
| `eventType` | string or `null` | Primary event-type label. |
| `categories` | object[] | Category metadata. |
| `topics` | string[] | Topic list. |
| `topicsCount` | integer | Topic count. |
| `verified` | integer | Verification flag. |
| `future` | integer | Future-event flag. |
| `historic` | integer | Historic-event flag. |
| `historicEvent` | string or `null` | Historic event marker. |
| `image` | string or `null` | Image URL. |
| `dataSource` | string or `null` | Upstream data source label. |
| `exhibitorCount` | integer | Exhibitor count. |
| `personnelCount` | integer | Personnel count. |
| `eventTypes` | object[] | Event-type rows. |
| `createTime` | integer-like value | Millisecond timestamp from the event row. |
| `updateTime` | integer-like value | Millisecond timestamp from the event row. |
| `unlocked` | boolean | User-specific unlock flag. |
| `matched_exhibitor_count` | integer | Number of matched exhibitors at the event. |
| `match_score` | number | Raw profile recommendation score after runtime numeric coercion. |

### Response example
```json
{
  "status": "completed",
  "items": [
    {
      "id": 123,
      "eventId": "139574",
      "name": "Shoptalk",
      "nickname": null,
      "description": null,
      "url": "https://example.com",
      "dateStart": "2026-03-25",
      "dateEnd": "2026-03-28",
      "venue": "Convention Center",
      "city": "Las Vegas",
      "region": "Nevada",
      "country": "United States",
      "latitude": null,
      "longitude": null,
      "attendeeCount": 10000,
      "declaredExpectedAttendees": 0,
      "estimatedExpectedAttendees": null,
      "priceLower": null,
      "priceUpper": null,
      "eventType": null,
      "categories": [],
      "topics": [],
      "topicsCount": 0,
      "verified": 1,
      "future": 1,
      "historic": 0,
      "historicEvent": null,
      "image": null,
      "dataSource": "vendelux",
      "exhibitorCount": 250,
      "personnelCount": 1800,
      "eventTypes": [],
      "createTime": 1711000000000,
      "updateTime": 1711000000000,
      "unlocked": false,
      "matched_exhibitor_count": 12,
      "match_score": 0.82
    }
  ],
  "total": 1,
  "page": 1,
  "pageSize": 20,
  "totalPages": 1,
  "hasMore": false,
  "condition_tags": {},
  "profile_version": 3,
  "active_result_version": 3,
  "is_stale": false
}
```

### Error responses
- `400 Bad Request` when the body fails validation.
- `401 Unauthorized` when the API key is missing, malformed, or invalid.
- `409 Conflict` when a recommendation task is already running for the user.

### Notes
- The route runs synchronous apply-onboarding first, then returns the current paged recommendation snapshot.
- Paging is applied after the service merges duplicate recommendation rows by event.
- Top-level metadata includes `status`, `condition_tags`, `profile_version`, `active_result_version`, and `is_stale`; empty-result responses may also include `empty_reason`, `failed_filters`, `candidate_count`, and `suggestions`.
- `match_score` here is the raw recommendation score; `POST /external/events/fit-score` separately normalizes a score onto a `0-10` style scale.

## GET /external/profile-matching/recommendations/exhibitors

### Authentication
Bearer token required.

### Success status code
`200 OK`

### Query parameters
| Name | Required | Type | Notes |
| --- | --- | --- | --- |
| `event_id` | Yes | string | Supports either external `Event.eventId` or internal `Event.id`. |
| `page` | No | integer | Defaults to `1`. |
| `pageSize` | No | integer | Defaults to `20`, max `100`. |
| `location` | No | string | Country or location filter. |
| `searchQuery` | No | string | Search term over company name or description. |
| `exhibitorName` | No | string[] | Exact exhibitor-name filter; repeated query params or a single value become an array. |
| `category` | No | string[] | Category-name filter; repeated query params or a single value become an array. |
| `industry` | No | string[] | Industry-name filter; repeated query params or a single value become an array. |
| `employeesMin` | No | integer | Minimum employee count. |
| `employeesMax` | No | integer | Maximum employee count. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `items` | object[] | Recommended exhibitors for the resolved event. |
| `total` | integer | Total exhibitors after filtering. |
| `page` | integer | Current page number. |
| `pageSize` | integer | Page size used at runtime. |
| `totalPages` | integer | `0` when `total` is `0`. |
| `hasMore` | boolean | `true` when another page exists. |
| `code` | string, optional | Present only for fallback responses; currently `AI_SEARCH_RESULT_MISMATCH`. |
| `show_refresh_hint` | boolean, optional | Present only for fallback responses. |

#### `items[]` fields
| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Internal exhibitor row identifier. |
| `companyName` | string | Exhibitor company name. |
| `description` | string or `null` | Exhibitor description. |
| `logo` | string or `null` | Logo URL. |
| `website` | string or `null` | Website URL. |
| `country` | string or `null` | Country. |
| `industry` | string or `null` | Industry label. |
| `categories` | string[] | Event-scoped business tags. |
| `employeeCount` | integer or `null` | Employee-count snapshot. |
| `companySize` | string or `null` | Raw `company_size` value. |
| `fundingRound` | string or `null` | Funding-round label. |
| `techStacks` | string[] | Normalized tech-stack names. |

### Response example
```json
{
  "items": [
    {
      "id": "456",
      "companyName": "Acme",
      "description": null,
      "logo": null,
      "website": "https://acme.com",
      "country": "United States",
      "industry": "Retail Technology",
      "categories": [
        "Commerce"
      ],
      "employeeCount": 120,
      "companySize": "51-200",
      "fundingRound": null,
      "techStacks": [
        "React"
      ]
    }
  ],
  "total": 1,
  "page": 1,
  "pageSize": 20,
  "totalPages": 1,
  "hasMore": false
}
```

### Error responses
- `400 Bad Request` when `event_id` is invalid or filters fail validation.
- `401 Unauthorized` when the API key is missing, malformed, or invalid.
- `404 Not Found` when the target event cannot be resolved.

### Notes
- Request-side `event_id` differs from the response-side `id` field on exhibitors.
- The route may return fallback metadata at the top level: `code: "AI_SEARCH_RESULT_MISMATCH"` and `show_refresh_hint: true`.
- In fallback mode, `items.length` may be smaller than `pageSize` even when `hasMore` is true because stored recommended exhibitor ids can resolve to deleted or missing exhibitor rows.
- `techStacks` is always returned as an array.

## POST /external/actions/precheck

### Authentication
Bearer token required.

### Success status code
`200 OK`

### Request body
| Field | Required | Type | Notes |
| --- | --- | --- | --- |
| `action_type` | Yes | string | Supported values currently include `query_event_personnel`, `unlock_event_contacts`, `unlock_contact_emails`, `search_exhibitor_events`, and `others`. |
| `call_source` | No | string | Optional caller source string used to derive sourced credit business codes. |
| `params` | Yes | object | Action-specific payload evaluated by the precheck. |
| `locale` | No | string | Optional locale hint. |
| `trace_id` | No | string | Optional trace identifier. |
| `conversation_id` | No | string | Optional conversation identifier. |
| `channel_message_id` | No | string | Optional channel message identifier. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `ok` | boolean | Currently always `true` when the request body passes validation. |
| `action_type` | string | Echoes the evaluated action type. |
| `allowed` | boolean | Whether the downstream action may proceed. |
| `should_charge` | boolean | Whether the downstream action would consume credits if executed now. |
| `credits` | integer | Credit amount for the action if it would charge; otherwise `0`. |
| `reason_code` | string | Decision code such as `ok`, `already_unlocked`, `unlock_in_progress`, `state_conflict`, `insufficient_balance`, `no_contacts_available`, `invalid_subject`, `unsupported_action`, or `not_found`. |
| `biz_code` | string | Derived business code used for credit attribution. Empty for actions that do not charge. |
| `detail` | object | Action-specific decision detail. |

#### `detail` fields
| Field | Type | Notes |
| --- | --- | --- |
| `event_id` | string or `null` | Canonical event identifier when relevant, or the unresolved input in `not_found` cases. |
| `access_mode` | string | For `query_event_personnel`, currently `full` or `preview`. |
| `preview_limit` | integer | For `query_event_personnel`, currently `50` when preview mode applies. |
| `unlock_action_type` | string or `null` | For `query_event_personnel`, suggested paid follow-up action when preview access blocks more results; currently `unlock_event_contacts`. |
| `unlock_credits` | integer or `null` | For `query_event_personnel`, credits required by the suggested unlock action when present. |
| `available_balance` | integer | Remaining balance snapshot for event unlock prechecks. |
| `company_name` | string | Echoed for exhibitor-event search prechecks. |
| `personnel_ids` | string[] | Deduplicated personnel ids that would be charged for email unlock. |
| `missing_personnel_ids` | string[] | Returned when requested personnel rows are missing. |
| `invalid_personnel_ids` | string[] | Returned when requested personnel are not valid for the supplied event. |
| `requested_count` | integer | Count of unique requested personnel ids. |
| `chargeable_count` | integer | Count of records that would consume credits. Event unlock prechecks return `0` here when no chargeable contacts are available. |
| `already_unlocked_count` | integer | Count of already unlocked contacts that blocks requeue. |
| `unlocking_count` | integer | Count of in-progress contacts that blocks requeue. |

### Response example
```json
{
  "ok": true,
  "action_type": "query_event_personnel",
  "allowed": true,
  "should_charge": false,
  "credits": 0,
  "reason_code": "ok",
  "biz_code": "",
  "detail": {
    "event_id": "139574",
    "access_mode": "preview",
    "preview_limit": 50,
    "unlock_action_type": "unlock_event_contacts",
    "unlock_credits": 2000
  }
}
```

### Error responses
- `400 Bad Request` when the request body fails validation.
- `401 Unauthorized` when the API key is missing, malformed, or invalid.

### Notes
- This endpoint performs truth evaluation only; it does not execute the downstream action.
- Unsupported `action_type` values still return `200 OK` with `allowed: false`, `should_charge: false`, and `reason_code: "unsupported_action"`.
- `detail` is intentionally action-specific: query-personnel prechecks return access-mode hints plus unlock guidance, unlock prechecks return charge or blocking context, and search prechecks echo the normalized company input.
- Event unlock prechecks can return `reason_code: "no_contacts_available"` with `detail.chargeable_count: 0` when the event has nothing left to charge for.
