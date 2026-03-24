# External API PM Reconciliation

| Item | API-Doc status | PM revision status | Current alignment | Notes |
| --- | --- | --- | --- | --- |
| Source of truth | `API-Doc` defines the current public external API contract | PM `revision` mirrors `API-Doc` in Chinese for contract content | Aligned | Contract changes must land in `API-Doc` first |
| Auth token prefix | Active auth example is `Authorization: Bearer uak_your_api_key` | Same active wording; `sk_...` appears only as a historical note | Aligned | Historical `sk_...` references must not be reused as current contract wording |
| Shared error body | External errors use `{ code, message, errorKey, traceId }` with real HTTP status codes | Same shared error body and status semantics are documented in Chinese | Aligned | `/external/*` final error body remains the external contract |
| Shared pagination contract | Common envelope fields are `page`, `pageSize`, `total`, `totalPages`, and `hasMore` | Same semantics are summarized in Chinese | Aligned | Route-specific request naming and item fields remain endpoint-specific |
| Live endpoint inventory | 14 live endpoints across 5 controller families | Same 14 live endpoints are listed under the implemented-now summary | Aligned | Draft-only routes are excluded from the live inventory |
| Events endpoints | 4 endpoint pages include success status, request section, response example, error responses, and notes | 4 Chinese endpoint sections mirror the same contract data | Aligned | Response examples and status codes now track `API-Doc` |
| Exhibitors endpoints | 4 endpoint pages define list, search, profile, and related-events behavior | 4 Chinese endpoint sections mirror the same contract data | Aligned | `exhibitor_id`-only profile lookup is preserved |
| Personnel endpoints | 3 endpoint pages define list, profile, and related-events behavior | 3 Chinese endpoint sections mirror the same contract data | Aligned | Lightweight public personnel shape is preserved |
| Contacts endpoint | `GET /external/contacts/search` uses company-based query input and a contact-style response | Chinese endpoint section mirrors the same contract data | Aligned | Email remains intentionally excluded |
| Profile Matching endpoints | Current live contract is `POST /external/profile-matching/recommendations/events/paged` plus `GET /external/profile-matching/recommendations/exhibitors` | Chinese endpoint sections mirror the same live contract | Aligned | The older `GET /external/profile-matching/recommendations/events` route remains historical only |
| Historical draft routes | `job/start`, `job/status`, and `GET /external/profile-matching/recommendations/events` are not live | The PM revision keeps them only as non-live historical notes | Aligned | They must never be promoted back into the implemented-now summary |
| Intentional differences | English Mintlify prose, navigation, and cross-links | Chinese PM prose and PM-facing framing | Intentional wording difference only | This is not a contract mismatch |

## Maintenance rule

1. Update `API-Doc` first whenever the public contract changes.
2. Mirror the same contract change into PM `外部 API 接口文档（revision）.md`.
3. Refresh this reconciliation artifact only when the synchronization rule itself changes or a new divergence appears.

## Review notes

- PM `revision` now carries endpoint-level success status codes, request sections, response examples, error responses, and notes for all 14 live endpoints.
- This artifact now tracks the synchronized state rather than the earlier pre-sync discrepancy snapshot.
- Future discrepancies should be treated as contract mismatches only when method/path, status code, request fields, response structure, or caller-visible note semantics diverge.
