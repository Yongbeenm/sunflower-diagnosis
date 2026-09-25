# Architecture

Two deployables, one contract. `frontend/` renders; `backend/` decides. They meet only
at `/api/v1/*`.

```
browser ──HTTPS──> frontend (Vite/React SPA)
                       │  fetch /api/v1/*  (bearer access token + httpOnly refresh cookie)
                       ▼
                   backend (FastAPI)
                   router → service → repository → model
                       │
                       ▼
                   PostgreSQL 16        media store (local disk → S3)
```

## Layering rules

| Layer | May import | Must never |
|---|---|---|
| `api/v1/routes` | schemas, services, core.deps | SQL, `select()`, models |
| `services` | repositories, schemas, core | FastAPI types, `Request`, `Depends` |
| `services/engine/scoring.py` | stdlib only | `app.db`, `app.models`, anything async |
| `repositories` | models, db.session | schemas, services |
| `models` | db.base, sqlalchemy | services, schemas |

`scoring.py` being pure is what makes the expert system testable. Ten golden test cases
run in milliseconds with no database, so weight tuning is cheap and regressions are loud.

## Data model

```
users(id, email UNIQUE, username UNIQUE, password_hash, role_id→roles,
      is_active, created_at, updated_at)
roles(id, name UNIQUE, description)
permissions(id, code UNIQUE, description)
role_permissions(role_id, permission_id)                       PK(role_id, permission_id)

symptom_categories(id, code UNIQUE, sort_order)
symptoms(id, code UNIQUE, category_id→symptom_categories,
         is_environmental, created_by_id, updated_by_id, created_at, updated_at)

diseases(id, slug UNIQUE,
         pathogen_type ENUM(fungal, bacterial, viral, abiotic, other),
         image_media_id→media NULL, is_published,
         created_by_id, updated_by_id, created_at, updated_at)

disease_symptoms(                          -- THE KNOWLEDGE BASE
  disease_id→diseases, symptom_id→symptoms,
  weight NUMERIC(3,2) CHECK (weight BETWEEN 0 AND 1),
  is_required BOOLEAN,                     -- absence argues strongly against
  is_pathognomonic BOOLEAN,                -- presence is near-conclusive
  PK(disease_id, symptom_id))

translations(                              -- ONE table, ONE database
  entity_type, entity_id, locale, field, value TEXT,
  PK(entity_type, entity_id, locale, field),
  INDEX(entity_type, entity_id, locale))
  -- entity_type: disease | symptom | category
  -- field:       name | description | cause | treatment | prevention | label

rulesets(id, version UNIQUE, algorithm, params JSONB, is_active,
         published_at, published_by_id)
         -- partial unique index: at most one is_active = true

diagnosis_sessions(id, user_id→users, ruleset_id→rulesets, locale,
                   symptom_count, top_disease_id→diseases NULL,
                   top_confidence NUMERIC(4,3) NULL,
                   outcome ENUM(matched, no_match), created_at,
                   INDEX(user_id, created_at DESC))
diagnosis_selected_symptoms(session_id, symptom_id,
                            answer ENUM(yes, no, unknown), PK(session_id, symptom_id))
diagnosis_results(id, session_id→diagnosis_sessions ON DELETE CASCADE, rank,
                  disease_id→diseases ON DELETE SET NULL,
                  disease_name_snapshot, score NUMERIC(4,3),
                  confidence NUMERIC(4,3), evidence JSONB)

feedback(id, user_id, diagnosis_session_id NULL, subject, message, media_id NULL,
         status ENUM(open, in_review, resolved), created_at)
media(id, storage_key UNIQUE, mime_type, bytes, width NULL, height NULL,
      uploaded_by_id, created_at)
audit_log(id, actor_id, action, entity_type, entity_id, diff JSONB, created_at)
```

### Why these four decisions

**Symptoms are rows, not a JSON blob.** The legacy app kept the checklist in
`diseases.symptom_checklist_json`, so it could not answer "which diseases show this
symptom", could not store a per-disease weight, and reloaded every disease on every
request to rebuild the symptom list. Normalising is what makes weighting, search, and
analytics possible at all.

**`answer` is tri-state.** "The grower says there is no head rot" is different
information from "the grower didn't mention head rot." The legacy schema could not tell
these apart, which is why it could never rule a disease *out*.

**Translations are rows, not `_km` columns.** Adding Vietnamese later means inserting
rows, not an `ALTER TABLE` plus a rewrite of every form, serializer, and template.

**`rulesets` makes diagnoses reproducible.** Each session records the ruleset that
produced it, so retuning weights doesn't retroactively invalidate history.

## The diagnosis engine

Weighted evidence with negative evidence. Parameters live in `rulesets.params`, never
in code.

```
For a candidate disease D with symptom weights w(s):

  present  = Σ w(s)  for s in D answered "yes"
  absent   = Σ w(s)  for s in D answered "no"
  possible = Σ w(s)  for all s in D

  raw   = (present − λ·absent) / possible         # possible == 0 → 0.0
  score = clamp(raw, 0, 1)

  if any pathognomonic symptom of D is "yes":  score = max(score, floor)
  if any required symptom of D is "no":        score = score × penalty
```

Default params (`algorithm = "weighted_evidence_v1"`):

```json
{
  "lambda_absent": 0.5,
  "min_confidence": 0.35,
  "pathognomonic_floor": 0.85,
  "required_missing_penalty": 0.25
}
```

Ranking drops anything below `min_confidence`, sorts by score descending then slug
ascending (deterministic ties), then normalises `confidence` as each score divided by
the sum of retained scores — so three equally plausible candidates read as genuinely
uncertain instead of three separate 90% answers.

**This replaces `score = matched / total`,** under which a 3-symptom disease outranked a
12-symptom disease on one shared match, every symptom counted equally, and a "no" carried
no weight at all.

### Every result carries its evidence

```json
{
  "session_id": "0193f2…",
  "ruleset_version": "2026.09.1",
  "outcome": "matched",
  "results": [
    {
      "rank": 1,
      "disease": { "slug": "white-mold", "name": "White Mold" },
      "score": 0.78,
      "confidence": 0.52,
      "evidence": {
        "supporting":  [{ "symptom": "white_fuzzy_mold", "weight": 0.55 }],
        "against":     [{ "symptom": "orange_pustules",  "weight": 0.20 }],
        "missing_key": [{ "symptom": "soft_stem_rot",    "weight": 0.35 }]
      }
    }
  ],
  "next_best_questions": [
    { "symptom": "cool_wet_conditions", "information_gain": 0.41 }
  ]
}
```

`next_best_questions` is what makes this an expert system rather than a scoring form:
pick the unanswered symptom whose answer would most shift the confidence distribution
(entropy reduction across candidates), and the grower finishes in four taps instead of
sixty. Skip symptoms that appear in only one candidate rule — they can't discriminate.

**An empty ranking is a product event, not an error.** Return HTTP 200 with
`results: []`, `outcome: "no_match"`, and a feedback prompt. Persist it. The admin
analytics page then shows which symptom patterns match nothing, which tells the
agronomist exactly which disease to add next.

## API surface (v1)

```
POST   /auth/register                       → creates a grower
POST   /auth/login                          → { access_token, user } + refresh cookie
POST   /auth/refresh                        → rotates refresh, returns new access
POST   /auth/logout
GET    /auth/me                             → user + role + permission codes
PATCH  /users/me

GET    /diseases            ?q=&category=&pathogen=&published=&page=&size=&locale=
GET    /diseases/{slug}
POST   /diseases                            disease:create
PATCH  /diseases/{id}                       disease:update
DELETE /diseases/{id}                       disease:delete   (soft, is_published=false)
PUT    /diseases/{id}/symptoms              disease:update   bulk weight set, one txn
PUT    /diseases/{id}/translations/{locale}

GET    /symptoms            ?category=&locale=   grouped, ordered — feeds the checker
POST   /symptoms | PATCH /symptoms/{id} | DELETE /symptoms/{id}
GET    /symptom-categories

POST   /diagnosis/sessions                  diagnosis:run    persists
POST   /diagnosis/preview                   diagnosis:run    stateless, no writes
GET    /diagnosis/sessions                  own history, paginated
GET    /diagnosis/sessions/{id}             own, or diagnosis:read_all

GET    /feedback                            feedback:read (all) else own
POST   /feedback
PATCH  /feedback/{id}                       feedback:resolve

GET    /admin/roles                         rbac:manage
PUT    /admin/roles/{id}/permissions        rbac:manage
GET    /admin/users | PATCH /admin/users/{id}       user:manage
GET    /admin/rulesets                      ruleset:manage
POST   /admin/rulesets/{id}/activate        ruleset:manage

GET    /analytics/overview                  analytics:read
POST   /media                               multipart → { id, url, width, height }
```

### Conventions

- **Pagination** on every list: `page` + `size`, response
  `{ items, total, page, size }`.
- **Errors** are `application/problem+json`:
  `{ type, title, status, detail, errors: [{ field, message }] }`.
- **Locale** from `Accept-Language`, overridden by `?locale=`. Per-field fallback to
  `en` when a translation row is missing — fall back field by field, not whole record.
- **Soft delete** for content (`is_published`), hard delete only for a user's own data.
- **`DELETE /symptoms/{id}` returns 409** when the symptom is in use, and the `detail`
  names the blocking diseases.

## Permissions

```
disease:read    disease:create   disease:update   disease:delete   disease:publish
symptom:read    symptom:create   symptom:update   symptom:delete
diagnosis:run   diagnosis:read_own   diagnosis:read_all
feedback:create feedback:read    feedback:resolve
user:manage     rbac:manage      ruleset:manage   analytics:read
```

Seeded roles — roles are data, the codes are the contract:

| Role | Was | Holds |
|---|---|---|
| `grower` | `user` | `disease:read`, `symptom:read`, `diagnosis:run`, `diagnosis:read_own`, `feedback:create` |
| `agronomist` | `doctor` / "Expert Sunflower" | grower + all `disease:*`, all `symptom:*`, `diagnosis:read_all`, `feedback:read`, `feedback:resolve`, `analytics:read` |
| `admin` | `admin` | everything |

`require_permission()` **fails closed**. The legacy `has_permission()` had
`except OperationalError: return self.role == "admin"` — an error path that *granted*
access. There is a test asserting a DB failure during the check yields 403, not 200.

## What this replaces

| Legacy | v2 |
|---|---|
| `admin.py` (1,109 lines) + `doctor.py` (876 lines), near-identical | one endpoint per action + a permission dependency |
| `users.role` string **and** `users.role_id` FK **and** hardcoded admin fast-path | `role_id` only, permissions resolved from `role_permissions` |
| `diseases.symptom_checklist_json` text blob | `symptoms` + `disease_symptoms(weight, …)` |
| two engines: dead `diagnosis.py` + live `diagnosis_db.py` | one engine, versioned rulesets |
| three databases (`main`, `i18n_en`, `i18n_km`) | one database, one `translations` table |
| `create_all()` + `schema_guard.ensure_schema_columns()` raw ALTERs on boot | Alembic migrations + an idempotent seed script |
| `session["last_diagnosis"]` | persisted `diagnosis_sessions` with shareable ids |
| 1,995-line `react-ui.js` from `esm.sh`, no build | Vite + TypeScript, feature slices, code splitting |
