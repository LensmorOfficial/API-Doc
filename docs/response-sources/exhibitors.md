# Exhibitors response sources

## GET /external/exhibitors/list
- Method/path source: `src/modules/external-api/controllers/external-exhibitors.controller.ts`
- DTO/query source: `src/modules/external-api/dto/exhibitors/external-exhibitor-list-query.dto.ts`
- Success status source: Nest default for `@Get()` -> `200 OK`
- Response example source: `src/modules/external-api/services/external-exhibitors.service.ts#list` and `src/modules/external-api/mappers/external-exhibitor-response.mapper.ts`
- Ambiguity note: `matched_event_ids` is set from the requested `event_id`.

## POST /external/exhibitors/search
- Method/path source: `src/modules/external-api/controllers/external-exhibitors.controller.ts`
- DTO/body source: `src/modules/external-api/dto/exhibitors/external-exhibitor-search.dto.ts`
- Success status source: e2e in `test/e2e/external-exhibitors.e2e-spec.ts` asserts `201`
- Response example source: `src/modules/external-api/services/external-exhibitors.service.ts#search` and `src/modules/external-api/mappers/external-exhibitor-response.mapper.ts`
- Ambiguity note: `matched_event_ids` is empty when no `event_id` filter is supplied.

## GET /external/exhibitors/profile
- Method/path source: `src/modules/external-api/controllers/external-exhibitors.controller.ts`
- DTO/query source: `src/modules/external-api/dto/exhibitors/external-exhibitor-profile-query.dto.ts`
- Success status source: e2e in `test/e2e/external-exhibitors.e2e-spec.ts` asserts `200`
- Response example source: `src/modules/external-api/services/external-exhibitors.service.ts#getProfile` and `src/modules/external-api/mappers/external-exhibitor-response.mapper.ts#toProfile`
- Ambiguity note: The current public query contract is `exhibitor_id` only.

## GET /external/exhibitors/events
- Method/path source: `src/modules/external-api/controllers/external-exhibitors.controller.ts`
- DTO/query source: `src/modules/external-api/dto/exhibitors/external-exhibitor-events-query.dto.ts`
- Success status source: Nest default for `@Get()` -> `200 OK`
- Response example source: `src/modules/external-api/services/external-exhibitors.service.ts#listEvents` and `src/modules/external-api/mappers/external-event-response.mapper.ts`
- Ambiguity note: Event items use the same shared event-item shape used by the events endpoints.
