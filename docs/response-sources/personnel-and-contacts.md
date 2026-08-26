# Personnel and Contacts response sources

## GET /external/personnel/list
- Method/path source: `src/modules/external-api/controllers/external-personnel.controller.ts`
- DTO/query source: `src/modules/external-api/dto/personnel/external-personnel-list-query.dto.ts`
- Success status source: Nest default for `@Get()` -> `200 OK`
- Response example source: `src/modules/external-api/services/external-personnel.service.ts#list` and `src/modules/external-api/mappers/external-contact-response.mapper.ts`
- Ambiguity note: Returned people use the contact-style public shape.
- Contract note: `sourceType` is a normalized string array. Supported labels are `exhibitor`, `social`, and `visitors`. The list query accepts one or more comma-separated or repeated `sourceType` values, normalized by `ExternalPersonnelListQueryDto` and passed into `QueryLeadDto.sourceTypes`.

## GET /external/personnel/profile
- Method/path source: `src/modules/external-api/controllers/external-personnel.controller.ts`
- DTO/query source: `src/modules/external-api/dto/personnel/external-personnel-profile-query.dto.ts`
- Success status source: Nest default for `@Get()` -> `200 OK`
- Response example source: `src/modules/external-api/services/external-personnel.service.ts#profile` and `src/modules/external-api/mappers/external-contact-response.mapper.ts`
- Contract note: The lightweight profile includes `email` and `contactUnlockStatus`; email is `null` until the API-key owner has access. It also includes `phone` only when phone unlock status is ready, plus `phoneUnlockStatus`.
- Contract note: `sourceType` uses the same normalized array shape as personnel list and contact search.

## GET /external/personnel/events
- Method/path source: `src/modules/external-api/controllers/external-personnel.controller.ts`
- DTO/query source: `src/modules/external-api/dto/personnel/external-personnel-events-query.dto.ts`
- Success status source: Nest default for `@Get()` -> `200 OK`
- Response example source: `src/modules/external-api/services/external-personnel.service.ts#listEvents` and `src/modules/external-api/mappers/external-event-response.mapper.ts`
- Ambiguity note: Event items follow the shared public event-item mapper shape.

## GET /external/contacts/search
- Method/path source: `src/modules/external-api/controllers/external-contacts.controller.ts`
- DTO/query source: `src/modules/external-api/dto/contacts/external-contact-search-query.dto.ts`
- Success status source: e2e in `test/e2e/external-contacts.e2e-spec.ts` asserts `200`
- Response example source: `src/modules/external-api/services/external-contacts.service.ts`, `src/modules/personnel/personnel.service.ts#searchExternalContacts`, and `src/modules/external-api/mappers/external-contact-response.mapper.ts`
- Contract note: `email` is returned when the API-key owner already has access and is `null` otherwise. `phone` is returned only when phone enrichment is ready; search itself does not unlock either field.
- Contract note: `sourceType` is an array and can combine multiple labels for the same person.
