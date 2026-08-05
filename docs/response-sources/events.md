# Events response sources

## GET /external/events/list
- Method/path source: `src/modules/external-api/controllers/external-events.controller.ts`
- DTO/query source: `src/modules/external-api/dto/events/external-event-list-query.dto.ts`
- Success status source: Nest default for `@Get()` -> `200 OK`
- Response example source: `src/modules/external-api/services/external-events.service.ts#listEvents` and `src/modules/external-api/mappers/external-event-response.mapper.ts`
- Contract note: Public event items include `hasVisitors` from `ExternalEventResponseMapper.toEventItem`. The customer-facing docs expose this as a response field only; `has_visitors` is not documented as a public event-list filter yet.
- Ambiguity note: The public example uses only fields directly emitted by `ExternalEventResponseMapper.toEventItem` plus the shared pagination envelope.

## GET /external/events/:id
- Method/path source: `src/modules/external-api/controllers/external-events.controller.ts`
- Success status source: Nest default for `@Get()` -> `200 OK`
- Response example source: `src/modules/external-api/services/external-events.service.ts#getEventDetail` and `src/modules/external-api/mappers/external-event-response.mapper.ts#toEventDetail`
- Contract note: Event detail includes `hasVisitors` from `ExternalEventResponseMapper.toEventDetail`; client types consume this as `ApiEvent.hasVisitors`.

## POST /external/events/fit-score
- Method/path source: `src/modules/external-api/controllers/external-events.controller.ts`
- DTO/body source: `src/modules/external-api/dto/common/external-event-id-query.dto.ts`
- Success status source: e2e in `test/e2e/external-events.e2e-spec.ts` asserts `201`
- Response example source: `src/modules/external-api/services/external-events.service.ts#fitScore` and `src/modules/external-api/mappers/external-event-response.mapper.ts`
- Contract note: `score` and all three breakdown values use the `0`–`10` scale. The breakdown keys are exactly `profile_match`, `matched_exhibitor_density`, and `event_scale`.
- Ambiguity note: PM draft fields such as `breakdown_details` and `limitations` are not emitted by the current service and are excluded.

## POST /external/events/rank
- Method/path source: `src/modules/external-api/controllers/external-events.controller.ts`
- DTO/body source: `src/modules/external-api/dto/events/external-event-rank.dto.ts`
- Success status source: Nest default for `@Post()` with no `@HttpCode` override -> `201 Created`
- Response example source: `src/modules/external-api/services/external-events.service.ts#rankEvents`
- Ambiguity note: The service currently emits an empty `reasons` array for each item.

## GET /external/events/brief
- Method/path source: `src/modules/external-api/controllers/external-events.controller.ts`
- DTO/query source: `src/modules/external-api/dto/events/external-event-brief-query.dto.ts`
- Success status source: Nest default for `@Get()` -> `200 OK`
- Response example source: `src/modules/external-api/services/external-events.service.ts#getEventBrief` and `src/modules/external-api/mappers/external-event-response.mapper.ts`
- Ambiguity note: `topCategories` is currently an empty array in the service output.

## POST /external/events/:id/unlock
- Method/path source: `src/modules/external-api/controllers/external-events.controller.ts`
- Success status source: Nest default for `@Post()` with no `@HttpCode` override -> `201 Created`
- Response example source: `src/modules/external-api/services/external-events.service.ts#unlockEvent`
- Billing source: `CREDIT_PRICES[CreditBizType.EVENT_UNLOCK]` -> `2000`

## POST /external/events/:id/visitors/unlock
- Method/path source: `src/modules/external-api/controllers/external-events.controller.ts`
- Success status source: Nest default for `@Post()` with no `@HttpCode` override -> `201 Created`
- Response example source: `src/modules/external-api/services/external-events.service.ts#unlockVisitor` and `src/modules/unlock/unlock.service.ts#unlockVisitor`
- Billing source: `CREDIT_PRICES[CreditBizType.VISITOR_UNLOCK]` -> `3000`
- Contract note: Base event access, active subscription, and available visitor data are required for a first unlock. Repeated unlocks return `creditsSpent: 0`.

## POST /external/events/:id/full-access/unlock
- Method/path source: `src/modules/external-api/controllers/external-events.controller.ts`
- Success status source: Nest default for `@Post()` with no `@HttpCode` override -> `201 Created`
- Response example source: `src/modules/external-api/services/external-events.service.ts#unlockFullAccess` and `src/modules/unlock/unlock.service.ts#unlockFullAccess`
- Billing source: missing base event access costs `2000`; missing visitor access costs `3000`; both missing costs `5000`
- Contract note: The operation is atomic and reports `eventUnlocked`, `visitorUnlocked`, `visitorSkipped`, and `totalCreditsUsed`.
