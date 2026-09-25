# Build order — prompts for the AI coding agent

Paste one prompt per task, in order. After each one: read the agent's summary, run the
verification it names, and fix anything broken **before** moving on.

The folder structure and configuration files already exist. The agent's job is to fill
them in, not to redesign the layout.

**Before you start:** confirm the agent has read `AGENTS.md` and
`docs/ARCHITECTURE.md`. In Antigravity, `AGENTS.md` at the repo root is picked up
automatically on every task.

Steps 2, 4, and 8 are the expensive ones to get wrong. For those, prepend:

> First output a plan and wait for my approval. Do not write code yet.

---

## Step 1 — Make the skeleton run

```
The repository structure and config files already exist (see AGENTS.md, README.md,
docker-compose.yml, backend/pyproject.toml, frontend/package.json). Do not restructure
them. Your job is to make `docker compose up` bring all three services healthy.

Backend, fill in:
- app/core/config.py — pydantic-settings Settings reading every variable in
  .env.example. No default values for JWT_SECRET, ADMIN_PASSWORD, or DATABASE_URL.
  Fail loudly at startup if a required secret is missing.
- app/core/logging.py — structlog, JSON output in production and console renderer in
  development, plus a middleware that attaches a request id to every log line.
- app/core/errors.py — an AppError base plus NotFound, Conflict, Forbidden,
  Unauthorized, ValidationFailed. A FastAPI exception handler that renders each one as
  application/problem+json per docs/ARCHITECTURE.md, and a handler converting
  Pydantic RequestValidationError into the same shape with a populated `errors[]`.
- app/db/base.py — DeclarativeBase with a naming_convention so constraint names are
  stable across migrations (ix/uq/ck/fk/pk patterns).
- app/db/session.py — async engine, async_sessionmaker(expire_on_commit=False), and a
  get_db dependency that rolls back on exception.
- app/main.py — app factory: settings, logging, CORS from settings.CORS_ORIGINS,
  exception handlers, the request-id middleware, a GET /health returning
  {status, version, db: "up"|"down"} that actually pings the database, and an empty
  api/v1 router mounted at /api/v1.
- alembic/env.py — async-aware, reads ALEMBIC_DATABASE_URL from the environment,
  target_metadata from app.db.base, compare_type=True and compare_server_default=True.
  Then create one empty initial revision.
- tests/conftest.py — fixtures: an app instance, an httpx AsyncClient against it, and
  a transactional database session that rolls back after each test.

Frontend, fill in:
- src/main.tsx, src/App.tsx, src/router.tsx — React Router with one placeholder route.
- src/styles/index.css — @import "tailwindcss" plus design tokens as CSS custom
  properties on :root, redefined under [data-theme="dark"]. Include a :lang(km) rule
  with a larger line-height for Khmer.
- src/api/client.ts — typed fetch wrapper: base URL from
  import.meta.env.VITE_API_BASE_URL, attaches a bearer token from an injectable token
  getter, parses problem+json into a typed ApiError class with `.errors` and `.status`.
  Leave the refresh interceptor as a documented hook — Step 3 wires it up.
- src/i18n/index.ts — react-i18next with en and km resources from src/locales, locale
  persisted, and the active locale mirrored onto the `lang` attribute of <html>.
- TanStack Query provider with sensible defaults (retry 1, staleTime 30s).
- src/test-setup.ts for Vitest + @testing-library/jest-dom.
- eslint.config.js (flat config: typescript-eslint strict + react-hooks).

Verify the dependency versions in pyproject.toml and package.json actually install; if
one has to move, change it and say so.

Do NOT write any domain models, routes, or pages yet. Stop when `docker compose up`
brings up db, api, and web, GET /health returns 200 with db: "up", the frontend loads
at :5173, and `pytest`, `mypy app`, and `tsc --noEmit` are all clean.
```

---

## Step 2 — Data model and migrations

```
Implement the complete data model in backend/app/models/ using SQLAlchemy 2.0 typed
Mapped[] declarative style, exactly as specified in docs/ARCHITECTURE.md § Data model.
Then generate ONE Alembic migration that creates all of it.

Requirements beyond the table listing:
- A TimestampMixin for created_at / updated_at (server_default=now(), onupdate).
- Set relationships to lazy="raise" by default, so an accidental N+1 load raises in
  tests instead of silently issuing queries. The repository layer loads explicitly
  with selectinload().
- Enums as native PostgreSQL enum types, created by the migration.
- The CHECK constraint on disease_symptoms.weight, and the partial unique index
  enforcing at most one rulesets row with is_active = true.
- diagnosis_results.disease_name_snapshot exists so history reads correctly after a
  rename; keep disease_id nullable with ON DELETE SET NULL.
- Indexes: diagnosis_sessions(user_id, created_at DESC),
  translations(entity_type, entity_id, locale), feedback(status, created_at DESC).

Then write backend/scripts/seed.py — idempotent, safe to run repeatedly, changing
nothing on a second run:
- All permission codes from docs/ARCHITECTURE.md § Permissions.
- The three roles (grower, agronomist, admin) with the permission sets in that table.
- The eight symptom categories with sort_order: leaf, leaf_head, whole_plant, stem,
  head, root, seedling, environment — plus their en and km translation rows.
- Ruleset version "2026.09.1", is_active=true, algorithm "weighted_evidence_v1", with
  the default params from docs/ARCHITECTURE.md.
- One admin user from ADMIN_EMAIL / ADMIN_USERNAME / ADMIN_PASSWORD. Refuse to run if
  ADMIN_PASSWORD is empty.

Verify: on an empty database run `alembic upgrade head`, then `alembic downgrade base`,
then upgrade again — all clean, no manual intervention. Then run the seed twice and
show that row counts are identical after both runs. Add a test asserting seed
idempotency.
```

---

## Step 3 — Auth and RBAC

```
Implement authentication and permission enforcement.

app/core/security.py — argon2 hash and verify; JWT encode/decode for an access token
(short TTL; claims sub, role, permissions[], exp, iat, jti) and a refresh token
(long TTL, its own jti).

app/core/deps.py:
- get_db
- get_current_user — parse the bearer token, load the user, 401 on missing/invalid/
  expired, 403 if is_active is false.
- require_permission(code: str) -> Callable — a dependency factory returning 403
  unless the code is among the current user's role permissions. It MUST fail closed:
  no exception path grants access. Write a test that makes the permission lookup raise
  a database error and asserts the response is 403, not 200. (The legacy app had
  `except OperationalError: return self.role == "admin"` — never reproduce that.)

app/api/v1/routes/auth.py:
  POST /auth/register   creates a grower; 409 on duplicate email or username
  POST /auth/login      { access_token, token_type, user }; sets the refresh token as
                        an httpOnly + Secure + SameSite=Lax cookie scoped to
                        /api/v1/auth. Identical response body AND comparable timing for
                        unknown-email and wrong-password, so the endpoint does not
                        enumerate accounts.
  POST /auth/refresh    rotates the refresh token (old jti is no longer accepted),
                        returns a fresh access token
  POST /auth/logout     clears the cookie and invalidates the refresh jti
  GET  /auth/me         current user with role and permission codes
app/api/v1/routes/users.py:
  PATCH /users/me       a username or email change requires current_password;
                        a password change requires current_password

Rate limit login to 10 attempts per 15 minutes per (IP, identifier). In-memory is fine
for now, but put it behind a small interface so Redis can replace it later.

Frontend, in src/features/auth/:
- Login and register pages with React Hook Form + Zod schemas that mirror the Pydantic
  models field for field.
- AuthProvider holding the access token in memory only — never localStorage or
  sessionStorage. On mount, attempt /auth/refresh once to restore a session.
- Wire the refresh interceptor left as a hook in Step 1: on a 401, attempt refresh
  once, replay the original request, and on a second failure clear auth and redirect
  to /login. Concurrent 401s must share one refresh, not trigger a stampede.
- A <RequirePermission code="…"> route guard and a usePermission() hook.

Tests: register, login, refresh rotation, logout, expired token, inactive user,
permission granted, permission denied, and the fail-closed case. Vitest for the auth
forms and the single-flight refresh behaviour.
```

---

## Step 4 — The expert system engine

**Do this before any CRUD UI.** Write the tests first, from the specification, and do
not touch the database in the first half of this task.

```
Implement the diagnosis engine per docs/ARCHITECTURE.md § The diagnosis engine.

PART A — the pure layer. app/services/engine/scoring.py imports nothing from app.db or
app.models. Plain frozen dataclasses in, plain dataclasses out.

  @dataclass(frozen=True) SymptomWeight: symptom_id, weight, is_required, is_pathognomonic
  @dataclass(frozen=True) DiseaseRule:   disease_id, slug, symptoms: tuple[SymptomWeight, ...]
  @dataclass(frozen=True) EngineParams:  lambda_absent, min_confidence,
                                         pathognomonic_floor, required_missing_penalty
  Answer = Literal["yes", "no", "unknown"]

  def score_disease(rule, answers: Mapping[int, Answer], params) -> DiseaseScore
  def rank(rules, answers, params) -> list[DiseaseScore]

Use the exact formula in the architecture doc. `possible == 0` yields 0.0, never a
division error. rank() drops scores below min_confidence, sorts by score desc then slug
asc for deterministic ties, and sets confidence as each score over the sum of retained
scores.

app/services/engine/explain.py — for each ranked disease build evidence:
  supporting  its symptoms answered "yes",     weight desc
  against     its symptoms answered "no",      weight desc
  missing_key its symptoms still "unknown" with weight >= 0.4, weight desc
Never return an empty explanation for a ranked result.

app/services/engine/next_question.py — next_best_questions(rules, answers, params, k=3).
For each unanswered symptom, compute the ranking twice (that symptom = yes, and = no),
measure the change in the confidence distribution's entropy, and return the top k by
expected gain. Ignore symptoms appearing in only one candidate rule — they cannot
discriminate. Never suggest an already-answered symptom.

tests/unit/test_scoring.py — at minimum these cases, each with a comment stating what
it protects:
 1.  No answers → empty ranking.
 2.  One "yes" of weight 0.55 on a disease whose weights total 1.00 → score 0.55.
 3.  A "no" on a weight-0.40 symptom reduces the score by lambda_absent × 0.40.
 4.  A pathognomonic "yes" lifts an otherwise weak score to pathognomonic_floor.
 5.  A required symptom answered "no" multiplies an otherwise strong score by the
     penalty.
 6.  A 3-symptom disease does NOT outrank a 12-symptom disease on a single shared
     match. (This is the exact bug in the legacy `matched / total` engine.)
 7.  Ties break deterministically by slug.
 8.  Scores stay within [0, 1] when many symptoms match.
 9.  All-"no" answers produce an empty ranking, never a negative score.
10.  Confidence values over a returned ranking sum to 1.0 (within float tolerance).
11.  next_best_questions never suggests an answered symptom, and prefers a symptom
     that discriminates between the top two candidates.

Get Part A green before starting Part B.

PART B — persistence. app/services/engine/runner.py is the only module in this package
allowed to touch the database. It loads the active ruleset and all published disease
rules through a repository, calls the pure layer, persists a diagnosis_session plus its
selected symptoms and ranked results (evidence into the JSONB column), and returns the
response DTO. Load every rule in ONE query with selectinload — not one query per
disease, which is what the legacy engine did.

On an empty ranking: persist outcome="no_match" with top_disease_id NULL, and return
HTTP 200 with results: [] plus a feedback_prompt. An empty result is a product signal,
not an error.

Endpoints in app/api/v1/routes/diagnosis.py:
  POST /diagnosis/sessions     diagnosis:run    persists, returns session_id
  POST /diagnosis/preview      diagnosis:run    stateless, zero writes, same response
                                                shape minus session_id
  GET  /diagnosis/sessions                      own history, paginated
  GET  /diagnosis/sessions/{id}                 own, or diagnosis:read_all

API tests: the persistence round-trip, the no-match path, that user A gets 404 (not
403 — do not leak existence) for user B's session, and that /preview writes nothing.
```

---

## Step 5 — Content CRUD, one surface only

```
Implement diseases, symptoms, categories, translations, and media as a single set of
resource endpoints, per hard rule 8 in AGENTS.md. There is exactly ONE disease-update
endpoint, gated by require_permission("disease:update"). No /admin and /doctor twins —
the legacy app had 1,985 lines of duplicated route code because of that mistake.

Repositories hold every query. Services hold the rules. Routers validate, delegate, and
shape the response.

Endpoints as listed in docs/ARCHITECTURE.md § API surface, plus these specifics:

GET /diseases — full-text search across translated name and description using a
Postgres tsvector column with a GIN index, added in a migration and kept current by a
trigger or a generated column. Filters: category, pathogen_type, published. Paginated.

GET /diseases/{slug} — full detail with per-field locale fallback to en, symptoms with
their weights grouped by category, and the image URL.

PUT /diseases/{id}/symptoms — bulk replace the whole weight set in ONE transaction.
Reject unknown symptom ids with 422 and a per-item errors[] naming the bad index.
Partial application is a bug: either all rows land or none do.

DELETE /symptoms/{id} — 409 when the symptom is referenced by any disease_symptoms row,
and the problem detail must name the blocking diseases so the agronomist knows what to
fix.

GET /symptoms — grouped by category, ordered by category.sort_order then translated
label. This single response feeds the symptom checker, so keep it to one query plus
translations and make it cacheable.

POST /media — multipart. Validate by magic bytes, not the file extension. Accept
png/jpeg/webp up to MEDIA_MAX_BYTES. Strip EXIF. Generate a thumbnail. Store through a
MediaBackend interface with a LocalDiskBackend implementation now and a documented seam
for S3. Return { id, url, width, height }.

Every mutation writes an audit_log row with the actor and a JSON diff, and sets
created_by_id / updated_by_id from the current user automatically.

Then generate the frontend types: run `npm run gen:api` against the live /openapi.json
into src/api/generated/ and commit the output. Never hand-edit it.

API tests: pagination boundaries, locale fallback per field, full-text search ranking,
the bulk-weights transaction rolling back cleanly on one bad item, the delete-in-use
409, and magic-byte rejection of a .png that is actually a script.
```

---

## Step 6 — The grower-facing frontend

```
Build the public and grower experience in frontend/src/features/. Mobile-first: the
real user is standing in a field on a mid-range Android phone on a slow connection.

If /mnt/skills/public/frontend-design/SKILL.md is available, read it. Treat design as a
deliverable — this should not look like a default template.

Routes:
  /                  landing: what this is, CTA into the checker, a few disease cards
  /diseases          searchable, filterable grid; debounced search; skeleton loaders
  /diseases/:slug    detail: image, symptoms grouped by plant part, cause, treatment,
                     prevention, language toggle, print stylesheet
  /check             the symptom checker (below)
  /check/:sessionId  result page with a shareable URL
  /history           the grower's own past checks, newest first, paginated
  /feedback          report a problem, optional photo, prefilled when arriving from a
                     no-match result

The symptom checker is the heart of the product. Build it as a guided flow, not a wall
of sixty checkboxes:
- Step 1: choose the affected plant part — the symptom categories as large tap targets.
- Step 2: yes / no / not-sure per symptom in that part. Tri-state, defaulting to
  not-sure. "No" is real evidence and the UI must make it easy to give.
- After each answer, debounced ~400ms, POST /diagnosis/preview and show a live ranked
  candidate list with confidence bars. Cancel in-flight requests on a new answer.
- Surface next_best_questions prominently as "answering this would help most", so the
  grower can finish in four taps instead of sixty.
- Progress reflects answered-vs-useful, not answered-vs-total.
- "Get result" posts to /diagnosis/sessions and routes to /check/:sessionId.
- The result view shows each candidate's confidence AND its evidence: what matched,
  what argues against, what is still unknown. Never a bare percentage.
- The no-match state is a designed screen, not an error toast: explain that this may be
  a disease not yet in the library, and offer the feedback form.

Requirements:
- TanStack Query for all server state; useState only for local UI state. Model the
  answer set with a reducer so it is unit-testable.
- Every user-facing string through t(), added to BOTH locales/en.json and
  locales/km.json, keys nested by feature. Khmer gets Noto Sans Khmer and a larger
  line-height, and no container may clip its diacritics.
- Loading, empty, and error states for every data view. No blank screens.
- Keyboard accessible, visible focus rings, aria-live on the live candidate list,
  labelled controls, WCAG AA contrast in both themes.
- Lazy-load routes. Keep the initial JS bundle under 200 KB gzipped and report the
  actual number.
- Vitest: the answer reducer, the debounce/cancel behaviour, and the checker flow.
```

---

## Step 7 — The admin and agronomist console

```
Build ONE admin console at /admin, rendered from permissions — not two parallel
dashboards. A nav item appears if and only if the user holds the permission; the pages
and the endpoints behind them are shared.

  /admin                  overview: checks today and total, top symptoms, no-match
                          patterns, pending feedback                  analytics:read
  /admin/diseases         table: search, sort, published filter, bulk publish
                                                                      disease:read
  /admin/diseases/new                                                 disease:create
  /admin/diseases/:id     tabbed editor                               disease:update
        Content tab       EN and KM side by side, with a per-field "missing
                          translation" indicator and a completeness meter
        Symptoms tab      the knowledge-base editor (below)
        Media tab         image upload with crop preview
  /admin/symptoms         catalog CRUD, a "used by N diseases" column; deleting an
                          in-use symptom shows which diseases block it
  /admin/feedback         queue with status transitions, linked to the originating
                          diagnosis session                     feedback:read/resolve
  /admin/users            list, role assignment, activate/deactivate    user:manage
  /admin/roles            a role × permission checkbox matrix            rbac:manage
  /admin/rulesets         versions, params, diff against active, activate behind a
                          confirmation step                          ruleset:manage

Also implement GET /analytics/overview on the backend to serve the dashboard: counts,
checks per day for the last 30 days, the most-selected symptoms, and the symptom
patterns that produced no_match. Keep it to a handful of aggregate queries.

The Symptoms tab is the most important screen in the console — the agronomist's whole
job happens there, so make it fast:
- Attach symptoms through a searchable combobox over the catalog, with inline create.
- Each attached symptom gets a weight slider (0.00–1.00, two decimals) plus required
  and pathognomonic toggles, each with a one-line tooltip: required means absence
  argues strongly against; pathognomonic means presence is near-conclusive.
- Group rows by symptom category, matching the checker's own grouping.
- A live preview panel: "if a grower reported these symptoms, this disease would rank
  #N at X% confidence" — call POST /diagnosis/preview so a weight change is immediately
  legible.
- Save is ONE PUT of the whole weight set. Atomic, never per-row.
- Optimistic updates via TanStack Query with rollback and a readable error toast.

Plus: a global unsaved-changes guard, a confirm dialog on every destructive action, and
toasts that surface the problem+json `detail` so server errors are actually readable.
```

---

## Step 8 — Migrate the real data

```
Write backend/scripts/migrate_legacy.py to move the existing content into the new
schema. The 26 bilingual disease records and their images are the most valuable thing
in the legacy project — they must be migrated, never retyped or replaced with fake seed
data.

Inputs, as CLI arguments: the legacy SQLite files
(instance/doctor_sunflower.db, instance/i18n_en.db, instance/i18n_km.db) and the legacy
image directory (app/static/images/).

Mapping:
- users → users. Keep email, username, and the Werkzeug password_hash. Add a legacy
  verifier path so those hashes still authenticate, and transparently rehash to argon2
  on the user's next successful login. Map roles: user→grower, doctor→agronomist,
  admin→admin.
- diseases → diseases + translations. name / symptoms / cause / treatment / prevention
  become locale="en" rows; the *_km columns become locale="km" rows, skipped when empty
  or byte-identical to the English. Infer pathogen_type from the slug and name
  (bacterial-* → bacterial; *-virus, mosaic, yellows → viral; otherwise fungal) and
  print every inference for manual review — do not silently guess.
- diseases.symptom_checklist_json → symptoms + disease_symptoms. Deduplicate by
  normalised label across ALL diseases, so "Wilting or drooping" becomes ONE symptom
  row shared by every disease that lists it; the legacy schema duplicated these per
  disease. Map the old category strings through the canonical map in the legacy
  app/services/symptom_admin.py (_CATEGORY_CANONICAL). Seed every weight at 0.50 with
  is_required and is_pathognomonic false, and write weights_to_review.csv so the
  agronomist can tune them properly — flag in the report that no diagnosis is
  trustworthy until that happens.
- symptom_catalog → merge into symptoms, keeping label_km as a km translation. Report
  any catalog entry no disease references.
- symptom_checks / _symptoms / _results → diagnosis_sessions / selected symptoms /
  results. Legacy selections had no tri-state, so import them all as answer="yes".
  Attribute them to a ruleset row version "legacy-import" with is_active=false, so it
  is obvious these predate the new engine. Preserve created_at and the disease-name
  snapshots.
- feedback → feedback, copying photo files through the media pipeline.
- Copy every referenced image into the media store, create media rows with real
  dimensions, and point diseases.image_media_id at them. Report missing files rather
  than aborting the run.

Requirements:
- Idempotent. Match on natural keys (disease slug, symptom code, user email) and update
  rather than duplicate.
- --dry-run prints the full plan and changes nothing.
- One transaction per entity type, with progress logging.
- A final report: rows read, created, updated, skipped, plus every warning.
- Tests against a small fixture SQLite file committed under tests/fixtures/, asserting
  symptom deduplication and the EN/KM translation split specifically.

Then write docs/MIGRATION.md: how to run it, a verification checklist of counts to
compare between old and new, and how to roll back.
```

---

## After step 8

Worth doing before you call it finished:

- **A seeded demo dataset** so a fresh clone is usable without the legacy database.
- **CI**: a GitHub Actions workflow running ruff, mypy, pytest, tsc, eslint, and vitest
  on every push. Cheap to add now, painful to retrofit.
- **Weight tuning session** with the agronomist, against `weights_to_review.csv`. Until
  that happens, everything is at 0.50 and the ranking is only as good as the structure.
- **An E2E smoke test** (Playwright): register → run a check → see a result → submit
  feedback.
