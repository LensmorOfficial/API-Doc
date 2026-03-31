# Personnel and Contacts response sources

## GET /external/personnel/list
- Method/path source: `src/modules/external-api/controllers/external-personnel.controller.ts`
- DTO/query source: `src/modules/external-api/dto/personnel/external-personnel-list-query.dto.ts`
- Success status source: Nest default for `@Get()` -> `200 OK`
- Response example source: `src/modules/external-api/services/external-personnel.service.ts#list` and `src/modules/external-api/mappers/external-contact-response.mapper.ts`
- Ambiguity note: Returned people use the contact-style public shape.

## GET /external/personnel/profile
- Method/path source: `src/modules/external-api/controllers/external-personnel.controller.ts`
- DTO/query source: `src/modules/external-api/dto/personnel/external-personnel-profile-query.dto.ts`
- Success status source: Nest default for `@Get()` -> `200 OK`
- Response example source: `src/modules/external-api/services/external-personnel.service.ts#profile` and `src/modules/external-api/mappers/external-contact-response.mapper.ts`
- Ambiguity note: The response is intentionally lightweight and does not expose email fields.

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
- Ambiguity note: Email is intentionally omitted from the external response contract.
