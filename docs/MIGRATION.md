# Legacy Data Migration Guide

This document describes how to migrate data from the legacy Flask monolith SQLite databases into the new PostgreSQL schema of the Sunflower Diagnosis Expert System.

---

## 1. Overview & Source Data

The legacy system stored all agronomic knowledge, user credentials, historical checks, and photos across several SQLite databases and local directories:

| Source Path | Contents | Destination in New Schema |
|---|---|---|
| `instance/doctor_sunflower.db` | Users (16), Diseases (26), Symptom Catalog (218), Checks (15), Feedback (2) | `users`, `diseases`, `symptoms`, `disease_symptoms`, `diagnosis_sessions`, `feedback` |
| `instance/i18n_en.db` | English strings and phrases keyed by SHA-256 | Translation fallbacks / verification |
| `instance/i18n_km.db` | Khmer strings and translations keyed by SHA-256 | Disease and symptom Khmer translations (`disease_translations`, `symptom_translations`) |
| `app/static/images/` | Disease reference images (JPEG/PNG) | `media_assets` + Local disk storage (`MEDIA_ROOT`) with thumbnail generation |
| `app/static/uploads/feedback/` | Grower-submitted feedback photos | `media_assets` linked to `feedback.photo_media_id` |

> [!IMPORTANT]
> The **26 bilingual disease records** and their curated field images are the core knowledge asset of the project. They must be migrated with complete fidelity—never retyped or replaced with mock data.

---

## 2. Prerequisites

1. **Active Python Environment**:
   Python 3.12+ with backend dependencies installed:
   ```bash
   cd backend
   pip install -e .
   ```
2. **Database Schema Up to Date**:
   PostgreSQL database running with Alembic migrations applied:
   ```bash
   alembic upgrade head
   ```
3. **Legacy Files Accessible**:
   Locate the legacy repository or copy the `instance/` folder and `app/static/images/` to a known path.

---

## 3. Migration CLI

The migration script is located at `backend/scripts/migrate_legacy.py`.

### Options & Arguments

| Argument | Required | Default | Description |
|---|---|---|---|
| `--db-path` | Yes | - | Path to legacy `doctor_sunflower.db` SQLite database |
| `--i18n-en-path` | No | None | Path to legacy `i18n_en.db` (optional fallback for English translations) |
| `--i18n-km-path` | No | None | Path to legacy `i18n_km.db` (Khmer translations) |
| `--images-dir` | No | None | Path to legacy disease images directory (`app/static/images/`) |
| `--feedback-photos-dir`| No | None | Path to legacy feedback uploads directory (`app/static/uploads/feedback/`) |
| `--review-csv` | No | `weights_to_review.csv` | Output path for the agronomist weight tuning CSV |
| `--dry-run` | No | `False` | Simulates the migration, validates data, and prints the plan without writing changes |

---

## 4. Running the Migration

### Step 1: Run a Dry Run

Always execute a dry run first to inspect the extraction counts, pathogen type inferences, unreferenced catalog entries, and validation checks:

```bash
python scripts/migrate_legacy.py \
  --db-path="/path/to/Sunflower-Diagnosis-ExpertSystem-main/instance/doctor_sunflower.db" \
  --i18n-km-path="/path/to/Sunflower-Diagnosis-ExpertSystem-main/instance/i18n_km.db" \
  --images-dir="/path/to/Sunflower-Diagnosis-ExpertSystem-main/app/static/images" \
  --dry-run
```

**Expected Output of Dry Run:**
- Confirms database connection and runs a read-only transaction simulation.
- Prints pathogen type inference audit table.
- Reports deduplicated symptoms vs unreferenced catalog items.
- Displays summary table with entity counts (all marked as read/planned).

### Step 2: Execute the Live Migration

When the dry-run output is verified, execute the live migration:

```bash
python scripts/migrate_legacy.py \
  --db-path="/path/to/Sunflower-Diagnosis-ExpertSystem-main/instance/doctor_sunflower.db" \
  --i18n-km-path="/path/to/Sunflower-Diagnosis-ExpertSystem-main/instance/i18n_km.db" \
  --images-dir="/path/to/Sunflower-Diagnosis-ExpertSystem-main/app/static/images" \
  --review-csv="weights_to_review.csv"
```

The migration runs one transaction per entity type in strict dependency order:
1. `rulesets`: Inactive ruleset `legacy-import` (`algorithm=legacy_ratio_v0`, `is_active=False`)
2. `users`: Maps roles (`user` → `grower`, `doctor` → `agronomist`, `admin` → `admin`) and preserves password hashes
3. `media_assets`: Validates dimensions with PIL, strips EXIF metadata, generates 300×300 thumbnails
4. `diseases`: Infers pathogen types (`bacterial`, `viral`, `fungal`), links media assets
5. `disease_translations`: Normalizes EN and KM texts, skipping identical or empty Khmer translations
6. `symptoms`: Deduplicates symptom checklists across all 26 diseases using normalized text keys
7. `disease_symptoms`: Creates associations with initial weight `0.50`, `is_required=False`, `is_pathognomonic=False`
8. `symptom_catalog`: Merges catalog items and labels
9. `diagnosis_sessions`: Imports historical checks attributed to `legacy-import`, mapping tri-state answer to `"yes"`
10. `feedback`: Migrates feedback entries and links uploaded photos

---

## 5. Verification Checklist

After running the migration against the full 26-disease legacy database, verify the record counts against the following baseline:

| Entity | Legacy Count | Target Schema Count | Notes |
|---|---|---|---|
| **Diseases** | 26 | 26 | Natural key: `slug` |
| **Disease Translations** | 26 EN + 26 KM | 52 (26 EN, 26 KM) | All 26 diseases have valid Khmer translations |
| **Media Assets** | 26 images | 26 | 26 disease reference images stored with thumbnails |
| **Unique Symptoms** | 218 catalog | 218 | 179 extracted and deduplicated from disease checklists + 39 catalog entries |
| **Disease-Symptom Associations** | ~260 checklist items | 260 | All seeded with weight `0.50` |
| **Users** | 16 | 16 | 1 admin, 1 agronomist (`doctor`), 14 growers (`user`) |
| **Diagnosis Sessions** | 15 | 15 | Attributed to inactive `legacy-import` ruleset |
| **Session Answers** | 60 | 60 | All answers mapped to `yes` |
| **Session Results** | 45 | 45 | Preserved rank and score snapshots |
| **Feedback** | 2 | 2 | Preserved comments and contact details |

You can verify counts using `psql`:
```sql
SELECT 'diseases' AS entity, COUNT(*) FROM diseases
UNION ALL
SELECT 'disease_translations', COUNT(*) FROM disease_translations
UNION ALL
SELECT 'symptoms', COUNT(*) FROM symptoms
UNION ALL
SELECT 'disease_symptoms', COUNT(*) FROM disease_symptoms
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'media_assets', COUNT(*) FROM media_assets
UNION ALL
SELECT 'diagnosis_sessions', COUNT(*) FROM diagnosis_sessions
UNION ALL
SELECT 'feedback', COUNT(*) FROM feedback;
```

---

## 6. Post-Migration Human Review

### 1. Agronomist Weight Tuning (`weights_to_review.csv`)

> [!WARNING]
> In the legacy system, all checklist symptoms were unweighted (scored as simple ratio of matching symptoms).
> The migration seeds every symptom association at weight **`0.50`** with `is_required=False` and `is_pathognomonic=False`.
> **No diagnosis is fully trustworthy until the agronomist tunes these weights.**

1. Open the exported `weights_to_review.csv`:
   - Columns: `disease_slug`, `disease_name`, `category`, `symptom_code`, `symptom_label_en`, `symptom_label_km`, `weight`, `is_required`, `is_pathognomonic`.
2. Agronomists review each symptom per disease:
   - Increase `weight` (up to `1.00`) for high-specificity symptoms.
   - Decrease `weight` (e.g., `0.10`–`0.30`) for generic symptoms like non-specific leaf yellowing.
   - Set `is_required=True` if the disease cannot be diagnosed without this symptom.
   - Set `is_pathognomonic=True` if this symptom alone conclusively confirms the disease.
3. Update weights through the Admin Console (`/admin/diseases/:slug`) or an import script.

### 2. Pathogen Type Inference Audit

The migration infers pathogen types from disease names and slugs using the following deterministic rules:
- `bacterial-*` or `crown-gall` → `PathogenType.BACTERIAL`
- `*-virus`, `mosaic`, or `yellows` (including `aster-yellows`) → `PathogenType.VIRAL`
- All others → `PathogenType.FUNGAL`

In the real 26-disease database, this correctly identifies:
- **Bacterial**: Bacterial Wilt (`bacterial-wilt`), Crown Gall (`crown-gall`)
- **Viral**: Sunflower Mosaic Virus (`sunflower-mosaic-virus`), Aster Yellows (`aster-yellows`)
- **Fungal**: 22 remaining fungal diseases (Rust, Downy Mildew, Phomopsis, Sclerotinia, etc.)

Check the printed report in the terminal or `pathogen_inferences` audit log to confirm all assignments.

### 3. Unreferenced Catalog Entries

39 symptoms in `symptom_catalog` were not referenced in any disease's checklist.
These are imported as standalone `symptoms` records so that agronomists can associate them with diseases in future knowledge base updates.

---

## 7. Authentication & Password Compatibility

Legacy users have passwords hashed with Werkzeug's `scrypt:` or `pbkdf2:sha256:` formats.

- **Zero-Dependency Verifier**: `app/core/security.py` includes a custom verification handler using Python's standard library `hashlib.scrypt` and `hashlib.pbkdf2_hmac`.
- **Transparent Rehash**: When a legacy user logs in via `POST /api/v1/auth/token`, the system:
  1. Detects the legacy hash format.
  2. Verifies the password against the legacy algorithm.
  3. Rehashes the password to **Argon2id** (`$argon2id$...`).
  4. Updates `users.password_hash` in the database immediately.
- Existing users do not need to reset their passwords.

---

## 8. Rollback Procedure

If a migration run needs to be rolled back or repeated from scratch:

### Option A: Reset Database Schema (Development / Staging)
```bash
cd backend
alembic downgrade base
alembic upgrade head
```

### Option B: Truncate Migrated Tables (Preserving Schema)
```sql
TRUNCATE TABLE
  feedback,
  diagnosis_session_results,
  diagnosis_session_answers,
  diagnosis_sessions,
  disease_symptoms,
  symptom_translations,
  symptoms,
  disease_translations,
  diseases,
  media_assets
CASCADE;

-- Optional: Delete imported users while preserving system admin
DELETE FROM users WHERE username != 'admin';

-- Delete legacy ruleset
DELETE FROM rulesets WHERE version = 'legacy-import';
```

### Option C: Clean Media Directory
If media files were copied into local storage:
```bash
rm -rf /var/lib/sunflower/media/* /tmp/sunflower_media/*
```

After cleaning, re-run `python scripts/migrate_legacy.py` with corrected parameters.
