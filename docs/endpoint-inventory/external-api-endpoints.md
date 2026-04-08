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
| GET | /external/events/list | `src/modules/external-api/controllers/external-events.controller.ts` | Yes | `200 OK` | Yes | Default date window is yesterday through one year ahead when no date filter is provided |
| POST | /external/events/fit-score | `src/modules/external-api/controllers/external-events.controller.ts` | Yes | `201 Created` | Yes | `event_id` accepts either `Event.eventId` or internal `Event.id` |
| POST | /external/events/rank | `src/modules/external-api/controllers/external-events.controller.ts` | Yes | `201 Created` | Yes | `event_ids` accepts either `Event.eventId` or internal `Event.id` |
| GET | /external/events/brief | `src/modules/external-api/controllers/external-events.controller.ts` | Yes | `200 OK` | Yes | `event_id` accepts either `Event.eventId` or internal `Event.id` |
| GET | /external/events/:id | `src/modules/external-api/controllers/external-events.controller.ts` | Yes | `200 OK` | Yes | Path `:id` accepts either internal row `id` or external `eventId` |
| GET | /external/exhibitors/list | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | `200 OK` | Yes | `event_id` accepts either `Event.eventId` or internal `Event.id` |
| POST | /external/exhibitors/search | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | `201 Created` | Yes | Requires `company_url`, `target_audience`, or both; no-match cases stay `200/201` success with empty items |
| POST | /external/exhibitors/search-by-company-name | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | `201 Created` | Yes | Precision-first paged lookup by `company_name` |
| POST | /external/exhibitors/search-events | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | `201 Created` | Yes | Reverse lookup from `company_name` to matching events |
| GET | /external/exhibitors/profile | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | `200 OK` | Yes | `exhibitor_id` is a numeric string |
| GET | /external/exhibitors/events | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | `200 OK` | Yes | `exhibitor_id` is a numeric string |
| GET | /external/personnel/list | `src/modules/external-api/controllers/external-personnel.controller.ts` | Yes | `200 OK` | Yes | `event_id` accepts either `Event.eventId` or internal `Event.id` |
| GET | /external/personnel/profile | `src/modules/external-api/controllers/external-personnel.controller.ts` | Yes | `200 OK` | Yes | `personnel_id` is a numeric string |
| GET | /external/personnel/events/by-linkedin | `src/modules/external-api/controllers/external-personnel.controller.ts` | Yes | `200 OK` | No | `linkedin_url` normalizes to a LinkedIn profile URL, then returns the matched personnel profile plus paginated associated events |
| GET | /external/personnel/events | `src/modules/external-api/controllers/external-personnel.controller.ts` | Yes | `200 OK` | Yes | `personnel_id` is a numeric string |
| GET | /external/contacts/search | `src/modules/external-api/controllers/external-contacts.controller.ts` | Yes | `200 OK` | Yes | Search is scoped to the authenticated user context |
| POST | /external/profile-matching/recommendations/events/paged | `src/modules/external-api/controllers/external-profile-matching.controller.ts` | Yes | `201 Created` | Yes | Runs synchronous apply-onboarding, then returns paged recommended events |
| GET | /external/profile-matching/recommendations/exhibitors | `src/modules/external-api/controllers/external-profile-matching.controller.ts` | Yes | `200 OK` | Yes | `event_id` accepts either `Event.eventId` or internal `Event.id` |

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
- When neither `date_start_from` nor `date_start_to` is supplied, the runtime defaults to events starting from yesterday through one year from now.
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
      "techStacks": []
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

### Notes
- No matches return an empty success response rather than `404`.
- Short queries stay exact-only after normalization; longer queries use strict token and prefix admission instead of permissive substring matching.

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
| `search_query` | No | string | Matches relation position or personnel full name. |

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

#### `items[]` fields
| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Internal personnel row identifier. |
| `fullName` | string | Full name. |
| `title` | string or `null` | For this route, sourced from `personnel.bio`. |
| `department` | string or `null` | Department value. |
| `seniorityLevel` | string or `null` | Seniority or level value. |
| `linkedinUrl` | string or `null` | LinkedIn URL. |
| `companyName` | string or `null` | Associated exhibitor company name. |
| `sourceType` | string or `null` | Source label. |

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
      "sourceType": "exhibitor"
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
- `400 Bad Request` when `event_id` or `exhibitor_id` is invalid.
- `401 Unauthorized` when the API key is missing, malformed, or invalid.
- `404 Not Found` when the target event cannot be resolved.

### Notes
- Request-side identifiers use `event_id` and optional `exhibitor_id`, while response-side identifiers use only `id`.
- `search_query` matches either relation `position` text or personnel `fullName`.

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
  "sourceType": "exhibitor"
}
```

### Error responses
- `400 Bad Request` when `personnel_id` is not a valid numeric string.
- `401 Unauthorized` when the API key is missing, malformed, or invalid.
- `404 Not Found` when the personnel row cannot be resolved.

### Notes
- Request-side `personnel_id` differs from the response-side `id` field.

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
    "sourceType": "exhibitor"
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
| `company_name` | Yes | string | Company lookup term. |
| `role` | No | string | Optional position or role filter. |
| `page` | No | integer | Defaults to `1`. |
| `pageSize` | No | integer | Defaults to `20`, max `100`. |

### Response body
#### Top-level fields
| Field | Type | Notes |
| --- | --- | --- |
| `items` | object[] | Same contact summary shape as `GET /external/personnel/list` `items[]`. |
| `total` | integer | Total distinct personnel matches. |
| `page` | integer | Current page number. |
| `pageSize` | integer | Page size used at runtime. |
| `totalPages` | integer | `0` when `total` is `0`. |
| `hasMore` | boolean | `true` when another page exists. |

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
      "sourceType": "exhibitor"
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
- Short company queries use a direct contains-style fallback; longer company queries use scored matching.
- Results are scoped to the authenticated user because the service computes user-specific reveal and task state before mapping the response.

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
