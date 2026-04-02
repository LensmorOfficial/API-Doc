# Events response sources

## GET /external/events/list
- Method/path source: `src/modules/external-api/controllers/external-events.controller.ts`
- DTO/query source: `src/modules/external-api/dto/events/external-event-list-query.dto.ts`
- Success status source: Nest default for `@Get()` -> `200 OK`
- Response example source: `src/modules/external-api/services/external-events.service.ts#listEvents` and `src/modules/external-api/mappers/external-event-response.mapper.ts`
- Ambiguity note: The public example uses only fields directly emitted by `ExternalEventResponseMapper.toEventItem` plus the shared pagination envelope.

## POST /external/events/fit-score
- Method/path source: `src/modules/external-api/controllers/external-events.controller.ts`
- DTO/body source: `src/modules/external-api/dto/common/external-event-id-query.dto.ts`
- Success status source: e2e in `test/e2e/external-events.e2e-spec.ts` asserts `201`
- Response example source: `src/modules/external-api/services/external-events.service.ts#fitScore` and `src/modules/external-api/mappers/external-event-response.mapper.ts`
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

## GET /external/events/:id
- Method/path source: `src/modules/external-api/controllers/external-events.controller.ts`
- Path parameter source: `src/modules/external-api/controllers/external-events.controller.ts#getEventDetail`
- Identifier resolution source: `src/modules/external-api/services/external-resource-resolver.service.ts#resolveEventDetailByIdOrEventIdOrThrow`
- Success status source: Nest default for `@Get()` -> `200 OK`
- Response example source: `src/modules/external-api/services/external-events.service.ts#getEventDetail` and `src/modules/external-api/mappers/external-event-response.mapper.ts#toEventDetail`
- Ambiguity note: The live resolver accepts either the database row `id` or the external `eventId` in the `:id` path segment.
