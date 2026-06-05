# External API PM Reconciliation

| Item | API-Doc status | PM revision status | Current alignment | Notes |
| --- | --- | --- | --- | --- |
| Source of truth | `API-Doc` defines the current public external API contract | PM `revision` mirrors `API-Doc` in Chinese for contract content | Aligned | Contract changes must land in `API-Doc` first |
| Auth token prefix | Active auth example is `Authorization: Bearer uak_your_api_key` | Same active wording; `sk_...` appears only as a historical note | Aligned | Historical `sk_...` references must not be reused as current contract wording |
| Shared error body | External errors use `{ code, message, errorKey, traceId }` with real HTTP status codes | Same shared error body and status semantics are documented in Chinese | Aligned | `/external/*` final error body remains the external contract |
| Shared pagination contract | Common envelope fields are `page`, `pageSize`, `total`, `totalPages`, and `hasMore` | Same semantics are summarized in Chinese | Aligned | Route-specific request naming and item fields remain endpoint-specific |
| Customer-facing endpoint inventory | 22 published endpoints across credits, events, exhibitors, personnel, contacts, and profile matching | PM revision needs to mirror this latest customer-facing set | Needs PM sync | Agent-only, debug, and deprecated routes are intentionally excluded |
| Events endpoints | 6 endpoint pages include list, detail, brief, fit-score, rank, and unlock | PM revision needs the same event unlock/access semantics | Needs PM sync | Response examples and status codes now track `API-Doc` |
| Exhibitors endpoints | 6 endpoint pages define list, search, search-by-company-name, search-events, profile, and related-events behavior | PM revision needs the new company-name lookup page | Needs PM sync | `search-events` is documented as credit-consuming |
| Personnel endpoints | 4 endpoint pages define list, profile, related-events, and LinkedIn URL related-events behavior | PM revision needs the LinkedIn URL route | Needs PM sync | Lightweight public personnel/contact shape includes unlock status and unlocked email when available |
| Contacts endpoints | Search, unlock, and unlock task polling are now documented | PM revision needs contact unlock and task polling | Needs PM sync | Email is returned only after unlock |
| Credits endpoint | `GET /external/credits/balance` is now documented | PM revision needs credit balance semantics | Needs PM sync | This supports customer preflight checks |
| Profile Matching endpoints | Current recommended contract is `POST /external/profile-matching/actions/apply-recommended-events/paged` plus `GET /external/profile-matching/recommendations/exhibitors` | PM revision needs the new actions path | Needs PM sync | The older `POST /external/profile-matching/recommendations/events/paged` route is deprecated and excluded from public navigation |
| Excluded routes | Agent files, actions precheck, debug reset, and deprecated profile matching are excluded from Mintlify | PM revision should not promote these as customer-facing APIs | Aligned principle | They may remain internal implementation notes only |
| Intentional differences | English Mintlify prose, navigation, and cross-links | Chinese PM prose and PM-facing framing | Intentional wording difference only | This is not a contract mismatch |

## Maintenance rule

1. Update `API-Doc` first whenever the public contract changes.
2. Mirror the same contract change into PM `外部 API 接口文档（revision）.md`.
3. Refresh this reconciliation artifact only when the synchronization rule itself changes or a new divergence appears.

## Review notes

- API-Doc now carries endpoint-level success status codes, request sections, response examples, error responses, and notes for the 22 customer-facing endpoints.
- This artifact now tracks the API-Doc-first state; PM revision should be synced after this documentation update.
- Future discrepancies should be treated as contract mismatches only when method/path, status code, request fields, response structure, or caller-visible note semantics diverge.
