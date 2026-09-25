# Decisions log

One entry per build phase. What was chosen, what was rejected, and why. When you come
back to this in six months — or hand it to someone else — this file is worth more than
the code comments.

Format:

```
## YYYY-MM-DD — Short title
**Context:** what problem forced a choice
**Decision:** what we did
**Rejected:** the alternative, and why not
**Consequence:** what this makes easy, and what it makes hard
```

---

## 2026-09-19 — Rewrite as two apps instead of refactoring the Flask monolith

**Context:** The legacy app had `admin.py` (1,109 lines) and `doctor.py` (876 lines)
that were near-identical, because routes were organised by *who* calls them rather than
*what resource* they act on. Server-rendered Jinja plus a 1,995-line unbuilt React file
loaded from a CDN meant no type safety across the boundary and no way to reuse the
logic for a future mobile client.

**Decision:** Separate `backend/` (FastAPI JSON API) and `frontend/` (Vite SPA), meeting
only at `/api/v1/*`, with the OpenAPI schema generating the frontend's TypeScript types.

**Rejected:** Refactoring in place. The duplication was structural, not incidental — the
route organisation itself was the bug, so fixing it meant rewriting both blueprints
anyway. Also rejected Next.js: server components would blur the boundary we are trying
to make explicit, and the team's strength is Python.

**Consequence:** Easy — one endpoint per action, typed contract, deployable pieces scale
independently, a mobile app can reuse the API unchanged. Hard — two deploys instead of
one, CORS and token refresh to get right, and no server-rendered HTML for SEO without
adding prerendering later.

---

## 2026-09-19 — Normalise the symptom checklist out of JSON

**Context:** `diseases.symptom_checklist_json` held the entire knowledge base as a text
blob. It could not answer "which diseases show this symptom", could not carry a
per-disease weight, and `_all_symptom_items()` loaded every disease on every request —
then `diagnose()` re-queried all of them once per candidate.

**Decision:** `symptoms` + `disease_symptoms(weight, is_required, is_pathognomonic)` as
real tables with foreign keys and a CHECK on the weight range.

**Rejected:** Keeping JSONB with a GIN index. Postgres could have queried it, but
referential integrity and a UI that edits individual weights both want rows, and the
weights are the thing the agronomist will spend the most time on.

**Consequence:** Easy — weighted scoring, negative evidence, symptom reuse across
diseases, analytics on symptom frequency, one query to load the whole rule set. Hard —
a real migration with deduplication (legacy data duplicated the same symptom per
disease), and every weight arrives at a placeholder 0.50 needing expert tuning.

---

## 2026-09-19 — One translations table instead of `_km` columns and three databases

**Context:** The legacy app ran three databases (main, `i18n_en`, `i18n_km`) with
messages keyed by `sha256(msg_key)`, while disease content used parallel `name`/`name_km`
columns. Cross-database joins were impossible and writes were not atomic.

**Decision:** One database. UI strings ship in the frontend bundle (`locales/*.json`);
content translations live in a single `translations(entity_type, entity_id, locale,
field, value)` table with per-field fallback to English.

**Rejected:** Per-locale columns. Adding Vietnamese would mean an `ALTER TABLE` plus
edits to every form, serializer, and template. Also rejected a separate table per
entity type — three near-identical tables with no benefit.

**Consequence:** Easy — a new locale is an insert, translation completeness is a
countable query, transactions are atomic. Hard — reads need a join or a prefetch, and
the fallback has to be per-field rather than per-record or a half-translated disease
renders as a mix nobody reviewed.

---

## 2026-09-19 — Step 1: Baseline skeleton setup and error handling

**Context:** The initial repository scaffold required setting up the backend (FastAPI, pydantic-settings, async SQLAlchemy session, structured logging, RFC 7807 problem details error handlers, Alembic async env) and frontend (React 19, Vite, Tailwind CSS v4, i18n, typed API fetch client) with strict typing.

**Decision:**
- Kept `CORS_ORIGINS` in `.env` as comma-delimited strings with a computed property `cors_origins_list` to avoid Pydantic v2 JSON-parsing issues during env loading.
- Used RFC 7807 `application/problem+json` consistently across FastAPI exception handlers for custom `AppError` hierarchies and Pydantic `RequestValidationError`.
- Augmented Vite's `UserConfig` directly in `vite.config.ts` for Vitest configuration to avoid type collisions between top-level Vite 6 and Vitest's transitive Vite 5 types under `exactOptionalPropertyTypes: true`.

**Rejected:**
- Storing CORS origins as raw JSON arrays in `.env`.
- Separate or divergent error formats between validation and domain errors.

**Consequence:**
- Easy: Clean environment variable parsing, standard error shapes on all failure modes, strict type-checking across frontend and backend.
- Hard: Vitest configuration requires explicit type augmentation until Vitest 3+ is upgraded across dependencies.

---

## 2026-09-19 — Step 2: Complete relational data model, lazy="raise", and migrations

**Context:** The application requires a typed declarative domain schema for users, RBAC permissions, symptom categorization, disease rules, multi-attribute evidence tracking, translations, and diagnostic session history.

**Decision:**
- Used SQLAlchemy 2.0 typed `Mapped[]` declarative mappings across modular domain files (`auth.py`, `symptom.py`, `disease.py`, `ruleset.py`, `diagnosis.py`, `feedback.py`, `media.py`, `audit.py`).
- Enforced `lazy="raise"` on all model relationships to prevent silent N+1 queries in tests and production.
- Modelled 4 PostgreSQL native enum types (`pathogen_type`, `diagnosis_outcome`, `diagnosis_answer`, `feedback_status`) with Python `enum.StrEnum`.
- Added check constraint on `disease_symptoms.weight` (`BETWEEN 0 AND 1`) and partial unique index on `rulesets` (`is_active = true`).
- Created Alembic migration `0002_data_model.py` with full bidirectional DDL (clean upgrade and downgrade).
- Implemented idempotent async seeder `scripts/seed.py` and automated test `test_seed.py` asserting identical table counts on re-runs.

**Rejected:**
- Keeping JSON blobs for symptom checklists or weights.
- Allowing lazy relationship loading by default.
- Manual raw SQL migrations or `Base.metadata.create_all()` in production code.

**Consequence:**
---

## 2026-09-19 — Step 3: Authentication, RBAC, fail-closed enforcement, and in-memory auth

**Context:** The legacy app relied on session cookies, hardcoded admin bypasses (`role == "admin"`), and insecure fallback behavior (`except OperationalError: return self.role == "admin"`). It also duplicated routes across `admin.py` and `doctor.py`.

**Decision:**
- Token architecture: Short-lived JWT access tokens held strictly in memory in the frontend (never `localStorage` or `sessionStorage`). Long-lived refresh tokens stored as HttpOnly, SameSite=Lax cookies with unique JTIs tracked in a revocation store for token rotation.
- Server-side RBAC: Permissions resolved strictly from `role_permissions` join table on the authenticated user. Hard rule fail-closed semantics: any error (database disconnect, unhandled exceptions) during `require_permission()` resolution returns 403 Forbidden, never 200 or 500.
- Single endpoint per resource: Eliminated `/admin` vs `/doctor` blueprint duplication. A single endpoint with `Depends(require_permission("..."))` governs access.
- Frontend single-flight refresh: Implemented deduplicated in-flight refresh promise (`singleFlightRefresh`) so concurrent 401 API responses share a single `/auth/refresh` request rather than causing an avalanche of refresh token rotations.
- React Hook Form + Zod: Auth forms strictly mirror backend Pydantic schemas field for field with full bilingual i18n support (English and Khmer) and accessible alert messages.

**Rejected:**
- Storing access tokens in `localStorage` or `sessionStorage` (vulnerable to XSS).
- Legacy fallback to admin on error (`except OperationalError: return self.role == "admin"`).
- Token-only permissions on the backend: Client tokens reflect permissions for UI rendering, but the server always verifies permissions directly against current database state.

**Consequence:**
- Easy: Immune to XSS token theft, clean refresh rotation, guaranteed fail-closed security, no duplicate endpoints.
- Hard: Frontend reloads require an async mount-time refresh handshake to restore session, which needs proper loading state handling.

---

## 2026-09-20 — Step 4: Expert system engine, pure mathematical layer, and persistence

**Context:** The legacy system used `score = matched / total`, where a 3-symptom disease outranked a 12-symptom disease on a single shared match, negative evidence was ignored, and re-querying all diseases was executed per candidate.

**Decision:**
- Pure mathematical layer (`scoring.py`, `explain.py`, `next_question.py`): Completely isolated from `app.db` and `app.models` (Hard Rule 9), receiving and returning plain frozen dataclasses.
- Weighted evidence with negative evidence: Clamped normalized scoring `(present - lambda * absent) / possible`, pathognomonic lift to floor, and required missing penalties.
- Entropy-based adaptive questioning (`next_question.py`): Calculated Shannon entropy over confidence distributions to rank unanswered symptoms by expected information gain.
- Single batch database loading (`runner.py` and `DiagnosisRepository`): Loaded active ruleset and all published candidate rules in ONE query with `selectinload` instead of N queries per candidate.
- Evidence snapshotting: Saved structured supporting, contradicting, and missing key evidence directly into `diagnosis_results.evidence` JSONB.
- Empty ranking handling: Empty ranking persisted as `outcome="no_match"` with `top_disease_id=NULL` returning HTTP 200 with an empty results list and bilingual `feedback_prompt`.
- Anti-leak authorization: Non-owners without `diagnosis:read_all` receive 404 Not Found (not 403 Forbidden) when requesting session details, preventing ID enumeration.

**Rejected:**
- `score = matched / total` legacy algorithm.
- Touching the database inside `scoring.py` or `explain.py`.
- Querying disease rules per candidate or issuing queries per symptom check.
- Returning 403 when a grower requests another grower's session ID (which leaks existence).

**Consequence:**
- Easy: Reproducible scoring, explainable diagnosis with structured evidence, deterministic ranking, fast batch database loading.
- Hard: Requires maintaining synchronization between pure dataclasses and ORM models in the runner layer.

---

## 2026-09-20 — Step 5: Content CRUD, single resource surfaces, full-text search GIN

**Context:** The legacy app duplicated route trees between `/admin` and `/doctor` (1,985 duplicated lines), missed full-text search across translated content, and had unvalidated bulk relationship updates.

**Decision:**
- Single resource surface per entity: Exactly one endpoint per action (e.g. `PUT /diseases/{id}/symptoms`) gated by `require_permission(...)`.
- PostgreSQL tsvector and GIN index for multilingual full-text disease search: Trigger updates `search_vector` across English and Khmer translations automatically.
- Atomic bulk updates: Replaced symptom weights inside a single transaction validating all IDs before mutating.
- Media upload pipeline: Magic-byte sniffing (`image/png`, `image/jpeg`), strict EXIF stripping, and thumbnail generation with pluggable storage backends (LocalDisk / S3).

**Rejected:**
- Duplicate `/admin/...` and `/doctor/...` controllers.
- In-memory Python filtering for text queries across translations.
- Client-trusted MIME types without magic-byte verification.

**Consequence:**
- Easy: Clean permission hierarchy, zero endpoint duplication, fast search over translations.
- Hard: Requires maintaining PostgreSQL-specific tsvector triggers in Alembic migrations.

---

## 2026-09-20 — Step 6: Grower-facing frontend, mobile-first guided diagnosis, and bilingual i18n

**Context:** The end users are Cambodian sunflower growers standing in fields with mid-range Android phones on slow connections, needing fast, intuitive symptom checking, clear evidence explanations, and seamless Khmer and English bilingual support.

**Decision:**
- Mobile-first layout with desktop header navbar and mobile sticky bottom navigation (`BottomNav`).
- Route-level code splitting via `React.lazy()` and `Suspense` for all pages to keep initial bundle sizes minimal.
- Guided plant-part category selector (`CategorySelector`) and pure answer state machine (`checkerReducer`) with tri-state toggles (Yes / No / Not Sure).
- Negative evidence prominently exposed: Answering "No" is treated as valuable diagnostic data that actively rules out diseases.
- Debounced live preview (400ms) with `AbortController` cancellation to eliminate in-flight network contention on low-bandwidth field connections.
- Explainable diagnosis results (`EvidenceBreakdown`): No bare percentages — each candidate displays supporting, conflicting, and missing symptoms.
- Designed "No-Match" experience offering pre-filled agronomist feedback referral rather than a dead-end error toast.
- Full bilingual i18n mirroring across `en.json` and `km.json`, dynamic `<html lang="...">` switching, and unconstrained container heights to preserve Khmer diacritics.
- Print stylesheet (`@media print`) on disease guides and diagnosis results for offline agronomist consultation.

**Rejected:**
- Monolithic single-page form dumping all plant symptoms simultaneously.
- Synchronous uncancelable network requests on every toggle tap.
- Bare confidence percentages without supporting or contradictory evidence.
- Fixed-height cards or overflow clipping that amputates Khmer vowels and sub-consonants.

**Consequence:**
- Easy: Smooth experience on slow connections, accessible UI, pure testable reducer logic, easy PDF/print generation.
- Hard: Requires keeping manual TypeScript API types aligned with backend schemas until live OpenAPI generation is automated.

---

## 2026-09-20 — Step 7: Unified Admin & Agronomist Console

**Context:**
The legacy Flask app had duplicated `/admin` and `/doctor` routes doing the same thing
with different templates — 1,985 lines of duplicated route code. We needed a single
admin portal dynamically shaped by server-side permissions (RBAC).

**Decision:**
- ONE route tree at `/admin` with `AdminLayout` that reads `user.permissions` from
  the auth context and filters sidebar navigation items accordingly. A grower with
  zero admin permissions is redirected to `/`.
- Backend: Three new route groups (`/analytics/overview`, `/feedback`, `/admin/*`)
  following router → service → repository → model. Rulesets, roles, and users are
  under `/admin/*`, analytics and feedback at top-level per the API surface spec.
- Frontend: Nine admin pages (`OverviewPage`, `DiseasesPage`, `DiseaseCreatePage`,
  `DiseaseEditorPage`, `SymptomsPage`, `FeedbackPage`, `UsersPage`, `RolesPage`,
  `RulesetsPage`) all lazy-loaded and code-split by Vite.
- Added `hasPermission()` method directly to `AuthContextType` so any component
  can check permissions without the separate `usePermission` hook.
- `ConfirmDialog` extended with an optional `variant` prop (`danger | warning | default`)
  while keeping backwards-compatible `isDanger` boolean for existing call sites.
- 141 admin translation keys added to both `en.json` and `km.json` locale files.
- Full admin CSS block added to `index.css`: layout, sidebar, table, tabs, matrix,
  form controls, mobile breakpoint, and button variants (`outline-danger`, `outline-primary`).

**Rejected:**
- Separate `/admin` and `/agronomist` route trees — violates hard rule 8 ("one endpoint
  per resource action"). Roles see different nav items, not different route trees.
- shadcn/ui data tables — too heavy for the initial build. Plain `<table>` with `.sf-table`
  CSS is sufficient and avoids an extra dependency.
- Full-blown permission matrix component library — premature. Simple checkbox grid
  with per-role save is adequate for 3 roles × ~15 permissions.
- Server-side rendering of admin pages — unnecessary since admin users are on desktop
  or tablet, not on slow field connections like growers.

**Consequence:**
- Easy: Adding a new admin section only needs a page component, a nav entry in
  `AdminLayout`, and a permission code. No route duplication possible.
- Hard: The `hasPermission` function checks against a flat permission string array
  carried in the JWT. If permission codes change shape (e.g., hierarchical), this
  needs revisiting.

---

## 2026-09-20 — Step 8: Legacy Data Migration and Password Compatibility

**Context:**
The legacy Flask monolith stored the 26 bilingual sunflower disease records, curated
field images, 218 symptom catalog items, historical diagnosis checks, user credentials,
and grower feedback across three SQLite databases (`doctor_sunflower.db`, `i18n_en.db`,
`i18n_km.db`) and static image directories. These 26 records are the core knowledge asset
of the expert system and could not be replaced with synthetic mock data. Furthermore,
legacy users used Werkzeug password hashes (`scrypt:32768:8:1$...` and `pbkdf2:sha256:...`)
that needed to remain functional without requiring forced password resets.

**Decision:**
- Built `backend/scripts/migrate_legacy.py` implementing a 10-step transactional migration
  pipeline matching on natural keys (disease slug, symptom code, user email) for idempotency.
- Implemented a zero-dependency legacy password verifier in `backend/app/core/security.py`
  using standard library `hashlib.scrypt` (with `maxmem=128*1024*1024` to handle Werkzeug's
  `n=32768` parameter) and `hashlib.pbkdf2_hmac`.
- Implemented transparent rehashing in `backend/app/services/auth.py`: upon successful login
  with a legacy hash, the password is transparently re-hashed to Argon2id and updated in the database.
- Deterministic symptom deduplication: normalized symptom labels across all 26 disease checklists
  into 179 unique symptoms plus 39 unreferenced catalog entries (218 total), mapped to canonical
  categories via legacy `_CATEGORY_CANONICAL`.
- Seeded initial disease-symptom association weights at `0.50` with `is_required=False` and
  `is_pathognomonic=False`. Exported `weights_to_review.csv` for agronomist tuning.
- Historical diagnosis checks imported as sessions attached to an inactive `legacy-import`
  ruleset (`algorithm=legacy_ratio_v0`, `is_active=False`) with answers mapped to `"yes"`.
- Media pipeline: validated image dimensions via PIL, stripped EXIF metadata, generated
  300×300 thumbnails, and linked to diseases and feedback entries.
- Created `backend/tests/fixtures/legacy_sample.db` and integration tests in
  `backend/tests/integration/test_migrate_legacy.py` verifying translation splits,
  deduplication, pathogen inference, idempotency, dry-run, and transparent login rehashing.

**Rejected:**
- Adding `werkzeug` as a runtime dependency just to verify passwords. Standard library
  `hashlib` is faster, eliminates an unnecessary third-party dependency, and avoids version
  conflicts.
- Forcing a password reset email campaign for all legacy users. Unnecessary friction for
  growers and agronomists.
- Importing legacy symptom checklist as raw JSON blobs. Would defeat the relational
  scoring engine and prevent individual symptom weight adjustments.
- Retaining duplicate symptoms per disease. Duplicating "Wilting or drooping" 12 times
  would break cross-disease comparison and question-ordering heuristics.

---

## 2026-09-20 — Step 9: Frontend-backend API connectivity and proxy configuration

**Context:**
The frontend was failing to communicate with the backend during user registration and API calls with a "Not Found" error. In development, `VITE_API_BASE_URL` was undefined in the browser context because `frontend/.env` did not exist and Vite's root was `frontend/`, causing `apiFetch` to target `http://localhost:5173/undefined/auth/...`. In addition, navigating directly to `http://localhost:8000/` returned FastAPI's default 404 response.

**Decision:**
- Defaulted `BASE_URL` in `frontend/src/api/client.ts` to `"/api/v1"` if `VITE_API_BASE_URL` is undefined or empty, and normalized URL path joining (`${BASE_URL}${cleanPath}`) to prevent double slashes or missing slashes.
- Added `frontend/.env` and `frontend/.env.example` defining `VITE_API_BASE_URL=/api/v1`, aligning with `vite.config.ts` proxy which forwards `/api` and `/media` to `http://localhost:8000`. This keeps dev cookies strictly same-origin (`localhost:5173`) and avoids cross-origin `SameSite=lax; Secure` cookie rejection on plain HTTP.
- Added a lightweight, developer-friendly root `GET /` endpoint on the FastAPI application that returns basic API metadata and links to `/docs` and `/health`, eliminating confusing 404s when navigating to `http://localhost:8000/`.

**Rejected:**
- Hardcoding `http://localhost:8000/api/v1` as the client base URL: this triggers cross-origin preflight requests and causes browsers (notably WebKit / Safari) to block HttpOnly cookies with `Secure` flags set over HTTP across different ports.
- Requiring developers to manually pass full `/api/v1` paths in every UI feature module.

**Consequence:**
- Easy: Out-of-the-box zero-config connectivity for both local development and containerized environments.
- All 26 vitest tests and 55 pytest tests pass with zero lint or type errors.




## 2026-09-20: Auto-Generate Symptom Code from Label

**Context**: Users were confused by the "code" field when creating symptoms. They asked "What is symptom code?" and "Can user not input code symptom?"

**Decision**: Hide the code input field completely and auto-generate it from the label using a slug-like transformation.

**What was rejected**:
- Keep manual code entry - too technical, users don't understand it
- Remove code field entirely - needed as database identifier and API key
- Show code as read-only - unnecessary clutter in UI

**What was chosen**: Auto-generate code client-side before API submission
- Function: `label.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '')`
- Examples: "Brown spots on leaves" → `brown_spots_on_leaves`
- Real-time preview shown below label input when creating new symptoms
- Code field hidden when editing existing symptoms (prevents accidental changes)

**Why**: 
- Reduces cognitive load - users only type what they see (the label)
- Prevents format errors - system ensures valid identifier format
- Faster workflow - one field instead of two
- Consistent naming - all codes follow same pattern
- User feedback: "can user dont input code syptom?" - they shouldn't need to

**Implementation**:
- Modified `SymptomsPage.tsx` - added `generateCode()` and `handleLabelChange()`
- Modified `DiseaseEditorPage.tsx` - added `generateSymptomCode()` and `handleNewSymptomLabelChange()`
- Added translations: `admin.auto_code` in en.json/km.json
- Code input field removed from both symptom creation modals
- Small gray text shows preview: "Auto-generated code: `example_code`"

**Files changed**:
- `frontend/src/features/admin/pages/SymptomsPage.tsx`
- `frontend/src/features/admin/pages/DiseaseEditorPage.tsx`
- `frontend/src/locales/en.json`
- `frontend/src/locales/km.json`

**Trade-offs**:
- Pro: Much simpler UX, fewer errors, faster data entry
- Pro: Users never need to understand technical identifiers
- Con: Less control over exact code format (acceptable - format is deterministic)
- Con: Potential for code collisions if labels are very similar (edge case, can be handled later)


## 2026-09-20: Bilingual Symptom Labels (EN/KM)

**Context**: User requested "for symptom and disease when add new or edit symptom i think i could in put for khmer like edit disease u alredy do". Diseases already supported bilingual content, but symptoms only had a single label field.

**Decision**: Add side-by-side English and Khmer input fields to symptom creation/editing forms, matching the disease editor pattern.

**What was rejected**:
- Single field with manual language switching - too cumbersome
- Language toggle to switch between EN/KM - harder to compare and ensure completeness
- Separate translation page - adds friction to workflow

**What was chosen**: Side-by-side bilingual input in the same modal
- English field (required) on the left with 🇬🇧 flag
- Khmer field (optional) on the right with 🇰🇭 flag
- Code auto-generated from English label (unchanged behavior)
- Khmer field includes `lang="km"` and Noto Sans Khmer font
- Backend already supported `label_en` / `label_km` in API schema

**Why**: 
- Consistent UX with disease editor (users already familiar with pattern)
- Easier to ensure translation completeness - both languages visible at once
- Khmer input immediately visible and accessible during creation
- No need to remember to translate later
- Falls back to English if Khmer missing (graceful degradation)

**Implementation**:
- Modified `SymptomsPage.tsx` - replaced single `formLabel` with `formLabelEn` and `formLabelKm`
- Modified `DiseaseEditorPage.tsx` - replaced `newSymptomLabel` with `newSymptomLabelEn` and `newSymptomLabelKm`
- Updated `admin/api.ts` interfaces: `CreateSymptomPayload` and `UpdateSymptomPayload` now use `label_en` / `label_km` instead of single `label`
- Both forms show grid layout with two columns (English | Khmer)
- Code auto-generation tied to English input only (consistent identifier)

**Files changed**:
- `frontend/src/features/admin/pages/SymptomsPage.tsx`
- `frontend/src/features/admin/pages/DiseaseEditorPage.tsx`
- `frontend/src/features/admin/api.ts`

**Trade-offs**:
- Pro: Consistent with disease editor, users already know the pattern
- Pro: Encourages translation at creation time rather than later
- Pro: Visual comparison makes it easy to check if translation is accurate
- Con: Modal is slightly wider (acceptable - most screens can fit it)
- Con: Khmer translation still optional (acceptable - English fallback works)
