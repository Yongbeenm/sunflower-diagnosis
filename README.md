# Sunflower Expert System 🌻

An AI-powered bilingual (English/Khmer) expert system for diagnosing sunflower diseases with intelligent symptom analysis, multimodal photo analysis, offline-first PWA capabilities, side-by-side disease comparison, downloadable PDF reports, real-time Recharts visual analytics, and agronomist tooling.

---

## ✨ Features

### 👨‍🌾 For Growers & Field Officers
- 🔍 **Interactive Symptom Checker (`/checker`)**: Multi-step diagnostic wizard categorized by plant anatomy (leaves, stems, flower heads, roots, whole plant).
- 📶 **Offline-First Progressive Web App (PWA)**: Full offline support with Service Worker caching and IndexedDB queue with auto-sync when field internet connectivity is restored.
- 📄 **Downloadable & Shareable PDF Diagnostic Report (`/result`)**: Export clean branded diagnostic scorecards as PDF or share via Web Share API.
- 🔬 **Side-by-Side Disease Comparison Tool (`/diseases/compare`)**: Compare 2–3 diseases side-by-side to distinguish lookalike symptoms (e.g. Downy Mildew vs Powdery Mildew) and check fungicide compatibility.
- 💬 **Botanical AI Crop Advisor**: Conversational AI assistant with plant photo upload and interactive quick-prompt questions.
- 🌐 **Bilingual English & Khmer (ភាសាខ្មែរ)**: Complete localized agronomic terminology and bilingual disease knowledge base.
- 👤 **Grower Account & Diagnosis History**: Track past crop evaluations, confidence scores, and field diagnoses over time.

### 🔬 For Agronomists & Researchers
- 🦠 **Disease Knowledge Base**: Create, edit, and publish disease definitions, pathogens, cause descriptions, and treatments.
- 🧬 **Diagnostic Weight & Ruleset Configuration**: Fine-tune pathognomonic symptoms, required indicators, and Bayesian penalty weights.
- 📊 **Visual Analytics Dashboard (`/admin`)**: Interactive charts powered by **Recharts**:
  - **Disease Outbreak Trend**: 30-day activity Area Chart with 7d/14d/30d filters.
  - **Symptom Distribution**: Donut and ranked Horizontal Bar observation frequency charts.
  - **Diagnostic Confidence Distribution**: Statistical distribution across certainty tiers (High, Moderate, Low, Inconclusive).
  - **Quality & Accuracy Metric Gauges**: Match rate, feedback resolution, and active symptom coverage scorecards.
- 📬 **Grower Feedback Queue**: Review unclassified symptom patterns and crop feedback reports directly from farmers.

### 🛡️ For System Administrators
- 👥 **Role-Based Access Control (RBAC)**: Customizable permission matrix for `grower`, `agronomist`, and `admin`.
- 🗄️ **pgAdmin 4 Web Console**: Embedded database management tool at `http://localhost:5050`.
- 🔑 **Enterprise Security**: Argon2id password hashing, JWT access tokens, HttpOnly refresh token rotation, and robust CORS controls.

---

## 🏗️ Architecture & Technology Stack

```mermaid
graph TD
    A[React 19 Frontend + Vite 6 + Tailwind CSS 4] -->|REST API + HttpOnly Cookies| B[FastAPI Python 3.12 Backend]
    B -->|Asyncpg SQLAlchemy 2.0 / Alembic| C[(PostgreSQL 16 Database)]
    D[pgAdmin 4 Web Interface] -->|Port 5432| C
    A -->|Service Worker + IndexedDB| E[Offline PWA Storage & Auto-Sync]
    A -->|Recharts| F[Interactive Visual Analytics]
```

- **Frontend**: React 19, TypeScript (Strict), Vite 6, Tailwind CSS 4, TanStack Query v5, Recharts, `vite-plugin-pwa`, `jspdf`, `html2canvas`, `react-router` v7, `react-i18next`.
- **Backend**: FastAPI (Python 3.12), SQLAlchemy 2.0 (Asyncpg / Psycopg), Alembic, Pydantic v2, Argon2id, JWT.
- **Database**: PostgreSQL 16 Alpine + pgAdmin 4.

---

## 📋 Prerequisites

| Requirement | Minimum Version | Recommended | Notes |
|-------------|-----------------|-------------|-------|
| **Git** | `2.x+` | Latest | Version control |
| **Docker & Docker Compose** | `24+` | Docker Desktop | Recommended for easiest setup |
| **Node.js** | `20.x+` | `20.x` or `22.x LTS` | If running frontend locally |
| **Python** | `3.12+` | `3.12.x` | If running backend locally |
| **PostgreSQL** | `14+` | `16.x` | If running database without Docker |

---

## 🚀 Quick Start with Docker (Recommended)

Docker runs the PostgreSQL database, pgAdmin 4, the FastAPI backend, and the React frontend in synchronized containers.

### 1. Clone the Repository
```bash
git clone https://github.com/Bunvathana876/Expert_sunflower.git
cd Expert_sunflower-deploy
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
- **macOS / Linux**:
  ```bash
  cp .env.example .env
  ```
- **Windows (PowerShell)**:
  ```powershell
  Copy-Item .env.example .env
  ```

### 3. Start the Containers
```bash
docker compose up -d --build
```

### 4. Apply Migrations & Seed Sample Data
In your terminal, run:
```bash
# 1. Run database schema migrations
docker compose exec api alembic upgrade head

# 2. Seed roles, permissions, categories, and admin account
docker compose exec api python -m scripts.seed

# 3. Import 5 standard sunflower diseases and 20 symptoms
docker compose exec api python -m scripts.import_sample_diseases
```

### 5. Access Your Applications

| Service | URL | Default Credentials |
|---|---|---|
| 🌐 **Grower Web App** | [http://localhost:5173](http://localhost:5173) | Free registration or seed accounts |
| 🛡️ **Admin Dashboard** | [http://localhost:5173/admin](http://localhost:5173/admin) | `admin@example.com` / `leetaka!1234568` |
| 📄 **API Swagger Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | N/A |
| 🗄️ **pgAdmin 4 Console** | [http://localhost:5050](http://localhost:5050) | `admin@sunflower.local` / `AdminPassword123!` |

---

## 🗄️ Connecting pgAdmin 4 to the Database

1. Open **[http://localhost:5050](http://localhost:5050)** in your browser.
2. Log in with:
   - **Email**: `admin@sunflower.local`
   - **Password**: `AdminPassword123!`
3. **Register Server**:
   - Right-click **Servers** ➡️ **Register** ➡️ **Server...**
   - **General Tab**: Name = `Sunflower Local DB`
   - **Connection Tab**:
     - **Host name / address**: `db` *(Internal Docker network host)*
     - **Port**: `5432`
     - **Maintenance database**: `sunflower_db`
     - **Username**: `sunflower_admin`
     - **Password**: `SuperSecurePassword123!`
   - Click **Save**.

---

## 🌐 Sharing Database with Teammates (via Tailscale VPN)

1. Both you and your teammate install **[Tailscale](https://tailscale.com/)** and log in.
2. Copy your **Tailscale IP** (e.g. `100.85.120.45`).
3. Keep your Docker database running (`docker compose up -d`).
4. Your teammate updates their `.env` file to replace `localhost` with your Tailscale IP:
   ```dotenv
   DATABASE_URL=postgresql+asyncpg://sunflower_admin:SuperSecurePassword123!@YOUR_TAILSCALE_IP:5433/sunflower_db
   ```
5. Your teammate can now query your live database directly over the secure Tailscale VPN!

---

## 💾 Saving Your Database Data to GitHub

Database records in Docker volumes (`pgdata`) are not automatically tracked by Git. Whenever you add new diseases or symptoms in the website and want to commit them to GitHub:

### Step 1: Export Data to a SQL Seed File
```bash
docker exec expert_sunflower-deploy-db-1 pg_dump -U sunflower_admin -d sunflower_db --data-only --inserts > backend/database_seed.sql
```

### Step 2: Commit & Push to GitHub
```bash
git add backend/database_seed.sql
git commit -m "feat: update disease and symptom seed data"
git push origin main
```

### Step 3: Restore on Any New Computer
```bash
docker exec -i expert_sunflower-deploy-db-1 psql -U sunflower_admin -d sunflower_db < backend/database_seed.sql
```

---

## 💻 Local Development Without Docker

If you prefer running frontend and backend directly on your host machine:

### 🍏 macOS Setup

```bash
# 1. Start local PostgreSQL
brew services start postgresql@16

# 2. Setup backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
alembic upgrade head
python -m scripts.seed
python -m scripts.import_sample_diseases
uvicorn app.main:app --reload --port 8000

# 3. Setup frontend (in a second terminal)
cd frontend
npm install
npm run dev
```

### 🪟 Windows Setup (PowerShell)

```powershell
# 1. Setup backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
alembic upgrade head
python -m scripts.seed
python -m scripts.import_sample_diseases
uvicorn app.main:app --reload --port 8000

# 2. Setup frontend (in a second terminal)
cd frontend
npm install
npm run dev
```

---

## 🔑 Default Seed Accounts

| Role | Email / Username | Password | Capabilities |
|------|---|---|---|
| **Administrator** | `admin@example.com` (`admin`) | `leetaka!1234568` | Full access, user & role editor, analytics |
| **Agronomist** | `expert@example.com` | `expert123456` | Knowledge base, symptom weights, feedback queue |
| **Grower** | `vathana` (`vathanabun934@gmail.com`) | Registered password | Field diagnosis, PDF export, history |

---

## 🧪 Testing & Verification

### Backend Pytest Suite
```bash
cd backend
pytest -v
```

### Frontend Typecheck, Tests & Build
```bash
cd frontend

# Run unit and component test suites with Vitest
npm test -- --run

# TypeScript validation
npm run typecheck

# Production and PWA service worker build
npm run build
```

---

## 📄 License

Distributed under the MIT License. Built for agricultural health research and sunflower farming communities.
