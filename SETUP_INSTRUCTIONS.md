# Sunflower Expert System - Setup Instructions

Complete guide to run this project on a new laptop.

## Prerequisites

### Required Software:
1. **Python 3.12+** - [Download](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download](https://nodejs.org/)
3. **PostgreSQL 14+** - [Download](https://www.postgresql.org/download/)
4. **Git** - [Download](https://git-scm.com/downloads)
5. **Ollama** (for AI features) - [Download](https://ollama.com/)

### Optional but Recommended:
- **Docker Desktop** - For easier database setup
- **VS Code** - Recommended IDE

---

## Quick Start (30 minutes)

### Step 1: Clone the Repository

```bash
git clone <your-github-repo-url>
cd sunflower-expert
```

### Step 2: Database Setup

#### Option A: Using Docker (Recommended)
```bash
# Make sure Docker Desktop is running
docker run --name sunflower-postgres \
  -e POSTGRES_USER=sunflower \
  -e POSTGRES_PASSWORD=change-me-in-dev-too \
  -e POSTGRES_DB=sunflower \
  -p 5432:5432 \
  -d postgres:14
```

#### Option B: Using Local PostgreSQL
```bash
# Create database
createdb sunflower

# Create user
psql postgres -c "CREATE USER sunflower WITH PASSWORD 'change-me-in-dev-too';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE sunflower TO sunflower;"
```

### Step 3: Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -e .

# Copy environment file
cp .env.example .env

# Edit .env file if needed (optional)
# Update DATABASE_URL if you changed database credentials

# Run database migrations
alembic upgrade head

# Seed initial data (roles, permissions, admin user)
python -m scripts.seed

# Start backend server
uvicorn app.main:app --reload
```

Backend will run on: **http://localhost:8000**

### Step 4: Ollama Setup (AI Features)

```bash
# Install Ollama from https://ollama.com/

# Pull required models
ollama pull qwen2.5:7b      # Main AI model
ollama pull llava:7b         # Vision model (for image analysis)

# Ollama will run on http://localhost:11434
```

### Step 5: Frontend Setup

```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Edit .env if backend is not on localhost:8000

# Start development server
npm run dev
```

Frontend will run on: **http://localhost:5173**

---

## Default Login Credentials

After seeding, you'll have these users:

### Admin Account:
- **Email:** admin@example.com
- **Password:** change-me-before-production
- **Role:** Full system access

### Expert Account:
- **Email:** expert@example.com
- **Password:** change-me-before-production
- **Role:** Manage diseases, symptoms, view feedback

### Grower Account:
- **Email:** grower@example.com
- **Password:** change-me-before-production
- **Role:** Run diagnosis, submit feedback

---

## Project Structure

```
sunflower-expert/
├── backend/                # Python FastAPI backend
│   ├── app/               # Main application code
│   │   ├── api/           # API routes
│   │   ├── core/          # Core configurations
│   │   ├── models/        # Database models
│   │   ├── repositories/  # Database queries
│   │   ├── services/      # Business logic
│   │   └── schemas/       # Pydantic schemas
│   ├── ai/                # AI services (Ollama integration)
│   ├── alembic/           # Database migrations
│   ├── scripts/           # Utility scripts
│   └── tests/             # Backend tests
│
├── frontend/              # React + TypeScript frontend
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── features/      # Feature modules
│   │   ├── components/    # Shared components
│   │   └── styles/        # Global styles
│   └── public/            # Static assets
│
└── docs/                  # Documentation (optional)
```

---

## Running the Full System

### Development Mode:

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Ollama (if not running as service):**
```bash
ollama serve
```

### Access the Application:
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## Common Issues & Solutions

### 1. Database Connection Error
```
Error: could not connect to server
```
**Solution:**
- Check PostgreSQL is running: `pg_isready`
- Verify DATABASE_URL in `backend/.env`
- Try: `psql -U sunflower -d sunflower -h localhost`

### 2. Ollama Connection Error
```
AI features are currently disabled
```
**Solution:**
- Check Ollama is running: `curl http://localhost:11434/api/tags`
- Start Ollama: `ollama serve`
- Pull models: `ollama pull qwen2.5:7b`

### 3. Frontend Can't Connect to Backend
```
Network Error / CORS Error
```
**Solution:**
- Check `CORS_ORIGINS` in `backend/.env`
- Should include: `http://localhost:5173`
- Restart backend after changing .env

### 4. Port Already in Use
```
Error: Address already in use
```
**Solution:**
```bash
# Backend (port 8000)
lsof -ti:8000 | xargs kill -9

# Frontend (port 5173)
lsof -ti:5173 | xargs kill -9
```

### 5. Python Virtual Environment Issues
```
ModuleNotFoundError
```
**Solution:**
```bash
cd backend
deactivate  # if already activated
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## Testing

### Backend Tests:
```bash
cd backend
source .venv/bin/activate
pytest
```

### Frontend Tests:
```bash
cd frontend
npm test
```

### Linting:
```bash
# Backend
cd backend
ruff format .
ruff check --fix .

# Frontend
cd frontend
npm run lint
```

---

## Environment Variables

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql+asyncpg://sunflower:change-me-in-dev-too@localhost:5432/sunflower

# Auth
JWT_SECRET=your-secret-key-here
ACCESS_TTL_MIN=15
REFRESH_TTL_DAYS=30

# API
CORS_ORIGINS=http://localhost:5173

# AI / Ollama
AI_ENABLED=true
AI_VISION_ENABLED=true
OLLAMA_HOST=http://localhost:11434
AI_MODEL=qwen2.5:7b
AI_VISION_MODEL=llava:7b

# Admin User
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=change-me-before-production
ADMIN_USERNAME=admin
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## Production Deployment

### Backend (Vercel/Railway/Render):
1. Set environment variables
2. Configure DATABASE_URL to production database
3. Set `ENV=production`
4. Run migrations: `alembic upgrade head`
5. Deploy

### Frontend (Vercel/Netlify):
1. Set `VITE_API_BASE_URL` to production backend URL
2. Run: `npm run build`
3. Deploy `dist` folder

### Database (Neon/Supabase/Railway):
1. Create PostgreSQL database
2. Update DATABASE_URL
3. Run migrations
4. Run seed script

---

## Useful Commands

### Backend:
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Seed database
python -m scripts.seed

# Run server
uvicorn app.main:app --reload

# Run tests
pytest

# Format code
ruff format .
ruff check --fix .
```

### Frontend:
```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm test

# Lint
npm run lint

# Type check
npm run typecheck
```

### Database:
```bash
# Connect to database
psql -U sunflower -d sunflower -h localhost

# Backup database
pg_dump -U sunflower sunflower > backup.sql

# Restore database
psql -U sunflower sunflower < backup.sql

# Check tables
psql -U sunflower -d sunflower -c "\dt"
```

---

## Features

### For Growers:
- 🔍 Disease diagnosis system
- 📸 Image-based symptom detection
- 💬 AI assistant for plant health questions
- 📋 Diagnosis history
- 📝 Feedback submission

### For Experts (Agronomists):
- 🦠 Manage diseases and symptoms
- 🔄 Update disease information
- 📊 View analytics
- 💬 AI admin chat (create/update/delete data)
- 📬 Review feedback

### For Admins:
- 👥 User management
- 🔐 Role & permission management
- 📊 System analytics
- ⚙️ Ruleset configuration
- 💬 Full AI admin capabilities
- 📬 Feedback management

---

## Support

### Documentation:
- API Docs: http://localhost:8000/docs
- Architecture: `docs/ARCHITECTURE.md`
- AI Features: `AI_ADMIN_COMMANDS.md`

### Troubleshooting:
- Check backend logs in terminal
- Check frontend console (F12)
- Check database connection
- Verify Ollama is running

---

## Next Steps After Setup

1. ✅ Login as admin
2. ✅ Check `/admin/overview` - View system stats
3. ✅ Visit `/admin/diseases` - Manage diseases
4. ✅ Try AI admin chat - "list all diseases"
5. ✅ Test diagnosis - `/check` page
6. ✅ Submit feedback - `/feedback` page

---

## Quick Reference

| Service | URL | Default Port |
|---------|-----|--------------|
| Frontend | http://localhost:5173 | 5173 |
| Backend API | http://localhost:8000 | 8000 |
| API Docs | http://localhost:8000/docs | 8000 |
| PostgreSQL | localhost:5432 | 5432 |
| Ollama | http://localhost:11434 | 11434 |

---

**Ready to run! Follow the Quick Start guide above to get started in 30 minutes.** 🚀
