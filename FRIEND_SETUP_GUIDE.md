# 🌻 Sunflower Expert System — Mac Setup & pgAdmin 4 Guide

Welcome! This guide will walk you through setting up the **Sunflower Expert System** on macOS using Docker, configuring **pgAdmin 4**, and easily inserting new diseases, symptoms, and scoring rules using ready-to-run SQL scripts.

---

## 📋 Prerequisites on Mac

1. **Docker Desktop for Mac**:
   - Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Apple Silicon / Intel).
   - Start Docker Desktop and make sure the engine is running (look for the whale icon in your Mac menu bar).
2. **Git** (preinstalled with macOS Xcode Command Line Tools).

---

## 🚀 1. Clone & Configure Environment

1. Open your Mac **Terminal** (`Cmd + Space` -> type `Terminal`).
2. Navigate into the cloned project folder:
   ```bash
   cd "path/to/Expert_sunflower-deploy"
   ```

3. Create or verify your `.env` file in the root directory:
   ```bash
   touch .env
   ```
   Open `.env` in any text editor and paste the following configuration:

   ```env
   # PostgreSQL Database Credentials
   POSTGRES_USER=sunflower_admin
   POSTGRES_PASSWORD=SuperSecurePassword123!
   POSTGRES_DB=sunflower_db

   # pgAdmin 4 Web Console Credentials
   PGADMIN_DEFAULT_EMAIL=admin@sunflower.local
   PGADMIN_DEFAULT_PASSWORD=AdminPassword123!

   # FastAPI Backend Database URL
   DATABASE_URL=postgresql+asyncpg://sunflower_admin:SuperSecurePassword123!@localhost:5433/sunflower_db
   ```

---

## 🐳 2. Start All Services with Docker

Run this single command in your Terminal:

```bash
docker compose up -d
```

This starts all 4 containers in the background:
- 🌐 **Frontend Web App**: `http://localhost:5173`
- ⚡ **FastAPI Backend API**: `http://localhost:8000/docs`
- 🐘 **PostgreSQL Database**: Port `5433` (Host) / `5432` (Docker Network)
- 🖥️ **pgAdmin 4 Console**: `http://localhost:5050`

To verify all containers are healthy:
```bash
docker compose ps
```

---

## 🐘 3. Set Up pgAdmin 4 in Your Browser

### Step 1: Log in
1. Open your web browser (Safari/Chrome) and visit: **[http://localhost:5050](http://localhost:5050)**
2. Log in using:
   - **Email Address**: `admin@sunflower.local`
   - **Password**: `AdminPassword123!`

### Step 2: Register the Database Server
1. In the left sidebar, right-click on **Servers** -> Select **Register** -> **Server...**
2. In the **General** tab:
   - **Name**: `Sunflower Local DB`
3. In the **Connection** tab:
   - **Host name/address**: `db` *(because pgAdmin connects inside the Docker network)*
   - **Port**: `5432`
   - **Maintenance database**: `sunflower_db`
   - **Username**: `sunflower_admin`
   - **Password**: `SuperSecurePassword123!`
   - Check the **Save password?** box.
4. Click **Save**.

You will now see:
```text
Servers
 └── Sunflower Local DB
       └── Databases
             └── sunflower_db
                   └── Schemas
                         └── public
                               └── Tables
```

---

## ✍️ 4. How to Insert Diseases & Symptoms using SQL

To add new knowledge data easily, use the **pgAdmin 4 Query Tool**:

1. In pgAdmin, right-click on **`sunflower_db`** (or go to top menu **Tools**).
2. Click **Query Tool**.
3. Copy and paste the template script below, customize the names and symptoms as you like, and press **F5** (or click the ▶ **Execute** button).

```sql
BEGIN;

-- ============================================================================
-- 1. ADD A NEW SYMPTOM
-- ============================================================================
-- Available categories: 'leaf', 'stem', 'head', 'whole_plant', 'root', 'seedling', 'environment'
INSERT INTO symptoms (code, category_id, is_environmental, created_at, updated_at)
VALUES (
    'stem_black_streak',
    (SELECT id FROM symptom_categories WHERE code = 'stem'),
    false,
    NOW(),
    NOW()
)
ON CONFLICT (code) DO NOTHING;

-- Insert English and Khmer translations for the symptom
INSERT INTO translations (entity_type, entity_id, locale, field, value)
VALUES 
    ('symptom', (SELECT id FROM symptoms WHERE code = 'stem_black_streak'), 'en', 'label', 'Black streaks along the stem'),
    ('symptom', (SELECT id FROM symptoms WHERE code = 'stem_black_streak'), 'km', 'label', 'ឆ្នូតខ្មៅតាមបណ្តោយដើម')
ON CONFLICT (entity_type, entity_id, locale, field) 
DO UPDATE SET value = EXCLUDED.value;


-- ============================================================================
-- 2. ADD A NEW DISEASE
-- ============================================================================
-- Pathogen types: 'fungal', 'bacterial', 'viral', 'abiotic', 'other'
INSERT INTO diseases (slug, pathogen_type, is_published, created_at, updated_at)
VALUES (
    'phoma-black-stem',
    'fungal',
    true,
    NOW(),
    NOW()
)
ON CONFLICT (slug) DO NOTHING;

-- Insert English & Khmer details (Name, Description, Treatment, Prevention)
INSERT INTO translations (entity_type, entity_id, locale, field, value)
VALUES 
    -- English Details
    ('disease', (SELECT id FROM diseases WHERE slug = 'phoma-black-stem'), 'en', 'name', 'Phoma Black Stem'),
    ('disease', (SELECT id FROM diseases WHERE slug = 'phoma-black-stem'), 'en', 'description', 'Fungal disease causing shiny black lesions on stems. Often occurs after flowering.'),
    ('disease', (SELECT id FROM diseases WHERE slug = 'phoma-black-stem'), 'en', 'treatment', 'Apply foliar fungicides during early flowering. Destroy crop residues after harvest.'),
    ('disease', (SELECT id FROM diseases WHERE slug = 'phoma-black-stem'), 'en', 'prevention', 'Practice 3-4 year crop rotation with non-host crops. Use certified seeds.'),

    -- Khmer Details
    ('disease', (SELECT id FROM diseases WHERE slug = 'phoma-black-stem'), 'km', 'name', 'ជំងឺដើមខ្មៅ Phoma'),
    ('disease', (SELECT id FROM diseases WHERE slug = 'phoma-black-stem'), 'km', 'description', 'ជំងឺផ្សិតដែលត្រូវបានកំណត់ដោយដំបៅខ្មៅភ្លឺចាំងនៅលើដើម។'),
    ('disease', (SELECT id FROM diseases WHERE slug = 'phoma-black-stem'), 'km', 'treatment', 'ប្រើប្រាស់ថ្នាំកម្ចាត់ផ្សិតលើស្លឹកអំឡុងពេលចេញផ្កា។ កម្ទេចកាកសំណល់ដំណាំក្រោយប្រមូលផល។'),
    ('disease', (SELECT id FROM diseases WHERE slug = 'phoma-black-stem'), 'km', 'prevention', 'អនុវត្តការបង្វិលដាំដំណាំ ៣-៤ ឆ្នាំជាមួយដំណាំមិនមែនជាម្ចាស់ផ្ទះ។')
ON CONFLICT (entity_type, entity_id, locale, field) 
DO UPDATE SET value = EXCLUDED.value;


-- ============================================================================
-- 3. LINK DISEASE TO SYMPTOMS WITH WEIGHTS (0.00 to 1.00)
-- ============================================================================
INSERT INTO disease_symptoms (disease_id, symptom_id, weight, is_required, is_pathognomonic)
VALUES 
    (
        (SELECT id FROM diseases WHERE slug = 'phoma-black-stem'),
        (SELECT id FROM symptoms WHERE code = 'stem_black_streak'),
        0.95,
        true,
        false
    ),
    (
        (SELECT id FROM diseases WHERE slug = 'phoma-black-stem'),
        (SELECT id FROM symptoms WHERE code = 'stem_discoloration'),
        0.80,
        false,
        false
    ),
    (
        (SELECT id FROM diseases WHERE slug = 'phoma-black-stem'),
        (SELECT id FROM symptoms WHERE code = 'plant_wilting'),
        0.60,
        false,
        false
    )
ON CONFLICT (disease_id, symptom_id)
DO UPDATE SET 
    weight = EXCLUDED.weight,
    is_required = EXCLUDED.is_required,
    is_pathognomonic = EXCLUDED.is_pathognomonic;

COMMIT;
```

---

## 🔎 5. Verify Your Data

Run this query in pgAdmin 4 Query Tool to check your database counts:

```sql
SELECT 'Total Diseases' as metric, count(*) as count FROM diseases
UNION ALL
SELECT 'Total Symptoms', count(*) FROM symptoms
UNION ALL
SELECT 'Disease-Symptom Rules', count(*) FROM disease_symptoms;
```

Now open **`http://localhost:5173`** or **`http://localhost:5173/admin`** in your browser — your new diseases, symptoms, and live counter badges will appear immediately!

---

## 🌐 6. Connecting Remotely via Tailscale (Optional)

If you are collaborating across two different Macs via **Tailscale**:
1. Both Macs install and log into [Tailscale](https://tailscale.com/).
2. Find the Host Mac's Tailscale IP address (e.g. `100.x.y.z`).
3. The guest Mac connects to the host's database or API using the Tailscale IP:
   - Database: `postgresql+asyncpg://sunflower_admin:SuperSecurePassword123!@100.x.y.z:5433/sunflower_db`
   - Frontend API target: `http://100.x.y.z:8000`

---

## 🛠️ Helpful Terminal Commands

| Action | Command |
| :--- | :--- |
| **Start containers** | `docker compose up -d` |
| **Stop containers** | `docker compose down` |
| **View real-time logs** | `docker compose logs -f` |
| **Restart services** | `docker compose restart` |
| **Check container health** | `docker compose ps` |

