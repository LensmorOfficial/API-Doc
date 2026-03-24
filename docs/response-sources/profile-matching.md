# Profile Matching response sources

## POST /external/profile-matching/recommendations/events/paged
- Method/path source: `src/modules/external-api/controllers/external-profile-matching.controller.ts`
- DTO/body source: `src/modules/external-api/dto/external-apply-recommended-events.dto.ts`, inherited fields from `src/modules/profile/dto/apply-recommended-events.dto.ts` and `src/modules/profile/dto/onboarding.dto.ts`
- Success status source: Nest default for `@Post()` with no `@HttpCode` override -> `201 Created`
- Response example source: `src/modules/profile/profile.service.ts#applyAndGetRecommendedEventsSync`, `#getRecommendedEventsPaged`, and `src/modules/profile/dto/recommended-events-paged.dto.ts`
- Error-contract note: Shared external errors come from `/external/*` handling in `src/common/filters/all-exceptions.filter.ts`

## GET /external/profile-matching/recommendations/exhibitors
- Method/path source: `src/modules/external-api/controllers/external-profile-matching.controller.ts`
- DTO/query source: `src/modules/external-api/dto/external-recommended-exhibitors-query.dto.ts`, inherited fields from `src/modules/profile/dto/query-recommended-exhibitor.dto.ts`
- Success status source: Nest default for `@Get()` -> `200 OK`
- Response example source: `src/modules/profile/profile.service.ts#getRecommendedExhibitorsPaged` and `src/modules/profile/dto/recommended-exhibitors-paged.dto.ts`
- Error-contract note: Unknown `event_id` is normalized to external `404 EVENT_NOT_FOUND` in e2e `test/e2e/external-profile-matching.e2e-spec.ts`
