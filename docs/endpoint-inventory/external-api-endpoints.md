# External API Endpoint Inventory

## Rules
- Source of truth for method/path: controllers
- Source of truth for auth example: external runtime middleware
- Source of truth for external error body: `/external/*` branch in AllExceptionsFilter

## Endpoint table
| Method | Path | Controller file | Auth required | Success status | Published in Mintlify | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| GET | /external/credits/balance | `src/modules/external-api/controllers/external-credits.controller.ts` | Yes | `200 OK` | Yes | Customer credit balance check |
| GET | /external/events/list | `src/modules/external-api/controllers/external-events.controller.ts` | Yes | `200 OK` | Yes | `@Get('list')` under `@Controller('external/events')` |
| GET | /external/events/:id | `src/modules/external-api/controllers/external-events.controller.ts` | Yes | `200 OK` | Yes | Event detail |
| GET | /external/events/brief | `src/modules/external-api/controllers/external-events.controller.ts` | Yes | `200 OK` | Yes | Lightweight event summary |
| POST | /external/events/fit-score | `src/modules/external-api/controllers/external-events.controller.ts` | Yes | `201 Created` | Yes | Profile-dependent score |
| POST | /external/events/rank | `src/modules/external-api/controllers/external-events.controller.ts` | Yes | `201 Created` | Yes | Rank a supplied event set |
| POST | /external/events/:id/unlock | `src/modules/external-api/controllers/external-events.controller.ts` | Yes | `201 Created` | Yes | Credit-consuming event unlock |
| GET | /external/exhibitors/list | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | `200 OK` | Yes | Event-scoped exhibitor list with preview semantics |
| POST | /external/exhibitors/search | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | `201 Created` | Yes | Heuristic exhibitor search by company URL/audience |
| POST | /external/exhibitors/search-by-company-name | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | `201 Created` | Yes | Precision-first exhibitor lookup |
| POST | /external/exhibitors/search-events | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | `201 Created` | Yes | `@Post('search-events')` under `@Controller('external/exhibitors')` |
| GET | /external/exhibitors/profile | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | `200 OK` | Yes | `@Get('profile')` under `@Controller('external/exhibitors')` |
| GET | /external/exhibitors/events | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | `200 OK` | Yes | `@Get('events')` under `@Controller('external/exhibitors')` |
| GET | /external/personnel/list | `src/modules/external-api/controllers/external-personnel.controller.ts` | Yes | `200 OK` | Yes | Event-scoped personnel list with preview semantics |
| GET | /external/personnel/profile | `src/modules/external-api/controllers/external-personnel.controller.ts` | Yes | `200 OK` | Yes | `@Get('profile')` under `@Controller('external/personnel')` |
| GET | /external/personnel/events | `src/modules/external-api/controllers/external-personnel.controller.ts` | Yes | `200 OK` | Yes | `@Get('events')` under `@Controller('external/personnel')` |
| GET | /external/personnel/events/by-linkedin | `src/modules/external-api/controllers/external-personnel.controller.ts` | Yes | `200 OK` | Yes | LinkedIn URL to related events |
| GET | /external/contacts/search | `src/modules/external-api/controllers/external-contacts.controller.ts` | Yes | `200 OK` | Yes | `@Get('search')` under `@Controller('external/contacts')` |
| POST | /external/contacts/unlock | `src/modules/external-api/controllers/external-contacts.controller.ts` | Yes | `201 Created` | Yes | Async email unlock |
| GET | /external/contacts/unlock-tasks/:taskId | `src/modules/external-api/controllers/external-contacts.controller.ts` | Yes | `200 OK` | Yes | Poll contact unlock task |
| POST | /external/profile-matching/actions/apply-recommended-events/paged | `src/modules/external-api/controllers/external-profile-matching.controller.ts` | Yes | `201 Created` | Yes | Recommended event workflow entry |
| GET | /external/profile-matching/recommendations/exhibitors | `src/modules/external-api/controllers/external-profile-matching.controller.ts` | Yes | `200 OK` | Yes | Recommended exhibitors for an event |

## Explicit exclusions
| Method | Path | Reason |
| --- | --- | --- |
| POST | /external/actions/precheck | Agent/tooling support endpoint; not customer-facing documentation. |
| GET/POST | /external/agent-files/* | Agent file transport endpoints; not customer-facing documentation. |
| POST | /external/debug/events/:id/reset-unlock | Debug endpoint behind `ExternalApiDebugEnabledGuard`; never publish. |
| POST | /external/profile-matching/recommendations/events/paged | Deprecated compatibility path; new docs use `/actions/apply-recommended-events/paged`. |

## Shared runtime truths
- Authorization format enforced by middleware: `Authorization: Bearer uak_...`
- Bearer scheme stripping is case-insensitive at runtime via `/^Bearer\s+/i`
- Swagger currently documents `Use Authorization: Bearer sk_...` in `src/main.ts` and must not be copied into public docs without reconciliation
- External error responses are emitted as `{ code, message, errorKey, traceId }`
- `/external/*` errors do not expose internal `data` or `details` fields in the final HTTP body
- The external exception path uses real HTTP status codes for the final response status
- External rate limiting can emit `429 RATE_LIMIT_EXCEEDED` with `Retry-After`

## Verification notes
- Included exactly 22 customer-facing routes in Mintlify and OpenAPI
- Confirmed Agent Files, Actions precheck, Debug, and deprecated profile-matching route are intentionally excluded
- Confirmed auth middleware rejects tokens that do not start with `uak_`
- Confirmed `/external/*` exceptions are replied with only `code`, `message`, `errorKey`, and `traceId`
