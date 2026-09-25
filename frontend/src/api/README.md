# api/

`client.ts` — the only module that calls `fetch`. Typed wrapper that reads the base
URL from `import.meta.env.VITE_API_BASE_URL`, attaches the in-memory bearer token,
retries once through `/auth/refresh` on a 401, and parses `application/problem+json`
into a typed `ApiError`.

`generated/` — output of `npm run gen:api` (openapi-typescript against the live
`/openapi.json`). Committed, but never hand-edited. Regenerate after any backend
schema change.
