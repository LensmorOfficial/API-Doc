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
- Validation-contract note: `company_url` and `target_audience` must provide at least one value; malformed `company_url` is external `400`.
- No-match note: heuristic no-match is `201` with empty pagination, not `404`.
- Ambiguity note: `matched_event_ids` is currently empty for this endpoint.

## POST /external/exhibitors/search-by-company-name
- Method/path source: `src/modules/external-api/controllers/external-exhibitors.controller.ts`
- DTO/body source: `src/modules/external-api/dto/exhibitors/external-exhibitor-search-by-company-name.dto.ts`
- Success status source: e2e in `test/e2e/external-exhibitors.e2e-spec.ts` asserts `201`
- Matching-policy source: `src/modules/external-api/services/external-resource-resolver.service.ts#searchExhibitorsByCompanyNamePaged`
- Response example source: `src/modules/external-api/services/external-exhibitors.service.ts#searchByCompanyName` and `src/modules/external-api/mappers/external-exhibitor-response.mapper.ts`
- No-match note: strict company-name no-match is `201` with empty pagination, not `404`.
- Ambiguity note: this endpoint returns exhibitors, while `POST /external/exhibitors/search-events` returns events.

## POST /external/exhibitors/search-events
- Method/path source: `src/modules/external-api/controllers/external-exhibitors.controller.ts`
- DTO/body source: `src/modules/external-api/dto/exhibitors/external-exhibitor-search-events.dto.ts`
- Success status source: e2e in `test/e2e/external-exhibitors.e2e-spec.ts` asserts `201`
- Matching-policy source: `src/modules/external-api/services/external-resource-resolver.service.ts#searchExhibitorsByCompanyNameStrict`
- Response example source: `src/modules/external-api/services/external-exhibitors.service.ts#searchEvents` and `src/modules/external-api/mappers/external-event-response.mapper.ts`
- Ambiguity note: `matchedExhibitors` is the admitted-and-capped exhibitor subset that participates in each returned event, and no-match results are empty pagination rather than `404`.

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
