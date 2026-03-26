# External API Endpoint Inventory

## Rules
- Source of truth for method/path: controllers
- Source of truth for auth example: external runtime middleware
- Source of truth for external error body: `/external/*` branch in AllExceptionsFilter

## Endpoint table
| Method | Path | Controller file | Auth required | Success status | Published in Mintlify | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| GET | /external/events/list | `src/modules/external-api/controllers/external-events.controller.ts` | Yes | TBD at endpoint-page stage | Yes | `@Get('list')` under `@Controller('external/events')` |
| POST | /external/events/fit-score | `src/modules/external-api/controllers/external-events.controller.ts` | Yes | TBD at endpoint-page stage | Yes | `@Post('fit-score')` under `@Controller('external/events')` |
| POST | /external/events/rank | `src/modules/external-api/controllers/external-events.controller.ts` | Yes | TBD at endpoint-page stage | Yes | `@Post('rank')` under `@Controller('external/events')` |
| GET | /external/events/brief | `src/modules/external-api/controllers/external-events.controller.ts` | Yes | TBD at endpoint-page stage | Yes | `@Get('brief')` under `@Controller('external/events')` |
| GET | /external/exhibitors/list | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | TBD at endpoint-page stage | Yes | `@Get('list')` under `@Controller('external/exhibitors')` |
| POST | /external/exhibitors/search | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | TBD at endpoint-page stage | Yes | `@Post('search')` under `@Controller('external/exhibitors')` |
| POST | /external/exhibitors/search-events | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | `201 Created` | Yes | `@Post('search-events')` under `@Controller('external/exhibitors')` |
| GET | /external/exhibitors/profile | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | TBD at endpoint-page stage | Yes | `@Get('profile')` under `@Controller('external/exhibitors')` |
| GET | /external/exhibitors/events | `src/modules/external-api/controllers/external-exhibitors.controller.ts` | Yes | TBD at endpoint-page stage | Yes | `@Get('events')` under `@Controller('external/exhibitors')` |
| GET | /external/personnel/list | `src/modules/external-api/controllers/external-personnel.controller.ts` | Yes | TBD at endpoint-page stage | Yes | `@Get('list')` under `@Controller('external/personnel')` |
| GET | /external/personnel/profile | `src/modules/external-api/controllers/external-personnel.controller.ts` | Yes | TBD at endpoint-page stage | Yes | `@Get('profile')` under `@Controller('external/personnel')` |
| GET | /external/personnel/events | `src/modules/external-api/controllers/external-personnel.controller.ts` | Yes | TBD at endpoint-page stage | Yes | `@Get('events')` under `@Controller('external/personnel')` |
| GET | /external/contacts/search | `src/modules/external-api/controllers/external-contacts.controller.ts` | Yes | TBD at endpoint-page stage | Yes | `@Get('search')` under `@Controller('external/contacts')` |
| POST | /external/profile-matching/recommendations/events/paged | `src/modules/external-api/controllers/external-profile-matching.controller.ts` | Yes | TBD at endpoint-page stage | Yes | `@Post('recommendations/events/paged')` under `@Controller('external/profile-matching')` |
| GET | /external/profile-matching/recommendations/exhibitors | `src/modules/external-api/controllers/external-profile-matching.controller.ts` | Yes | TBD at endpoint-page stage | Yes | `@Get('recommendations/exhibitors')` under `@Controller('external/profile-matching')` |

## Shared runtime truths
- Authorization format enforced by middleware: `Authorization: Bearer uak_...`
- Bearer scheme stripping is case-insensitive at runtime via `/^Bearer\s+/i`
- Swagger currently documents `Use Authorization: Bearer sk_...` in `src/main.ts` and must not be copied into public docs without reconciliation
- External error responses are emitted as `{ code, message, errorKey, traceId }`
- `/external/*` errors do not expose internal `data` or `details` fields in the final HTTP body
- The external exception path uses real HTTP status codes for the final response status

## Verification notes
- Included exactly 15 implemented routes from the five live external controllers
- Confirmed no `job/start`, `job/status`, or `GET /external/profile-matching/recommendations/events` route exists in the inspected controllers
- Confirmed auth middleware rejects tokens that do not start with `uak_`
- Confirmed `/external/*` exceptions are replied with only `code`, `message`, `errorKey`, and `traceId`
