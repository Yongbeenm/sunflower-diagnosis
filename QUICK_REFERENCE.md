# Quick Reference Card 📋

Fast reference for common tasks and commands.

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repo-url> && cd sunflower-expert

# Backend
cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install -e . && alembic upgrade head && python -m scripts.seed
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend && npm install && npm run dev

# Ollama (new terminal)
ollama pull qwen2.5:7b && ollama pull llava:7b && ollama serve
```

## 🔑 Default Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@example.com | change-me-before-production |
| Expert | expert@example.com | change-me-before-production |
| Grower | grower@example.com | change-me-before-production |

## 📡 URLs

| Service | URL | Port |
|---------|-----|------|
| Frontend | http://localhost:5173 | 5173 |
| Backend | http://localhost:8000 | 8000 |
| API Docs | http://localhost:8000/docs | 8000 |
| PostgreSQL | localhost:5432 | 5432 |
| Ollama | http://localhost:11434 | 11434 |

## 🛠️ Common Commands

### Backend:
```bash
# Activate venv
source .venv/bin/activate

# Run server
uvicorn app.main:app --reload

# Run tests
pytest

# Migrations
alembic upgrade head              # Run all migrations
alembic downgrade -1              # Rollback one
alembic revision --autogenerate -m "msg"  # Create new

# Seed data
python -m scripts.seed

# Format & lint
ruff format .
ruff check --fix .

# Type check
mypy app
```

### Frontend:
```bash
# Install deps
npm install

# Dev server
npm run dev

# Build
npm run build

# Preview build
npm run preview

# Tests
npm test

# Lint
npm run lint

# Type check
npm run typecheck
```

### Database:
```bash
# Connect
psql -U sunflower -d sunflower -h localhost

# Backup
pg_dump -U sunflower sunflower > backup.sql

# Restore
psql -U sunflower sunflower < backup.sql

# Drop & recreate
dropdb sunflower && createdb sunflower
```

### Docker:
```bash
# Start
docker compose up --build

# Stop
docker compose down

# Logs
docker compose logs -f

# Execute command
docker compose exec api alembic upgrade head
```

### Git:
```bash
# Status
git status

# Add all
git add -A

# Commit
git commit -m "message"

# Push
git push origin main

# Pull
git pull origin main

# Cleanup
./cleanup.sh
```

## 🔍 Troubleshooting

### Backend won't start:
```bash
# Check port
lsof -ti:8000 | xargs kill -9

# Check database
pg_isready

# Reset database
dropdb sunflower && createdb sunflower
cd backend && alembic upgrade head && python -m scripts.seed
```

### Frontend won't start:
```bash
# Check port
lsof -ti:5173 | xargs kill -9

# Clear cache
rm -rf node_modules dist .vite
npm install
```

### Ollama not working:
```bash
# Check status
curl http://localhost:11434/api/tags

# Restart
pkill ollama && ollama serve

# Pull models
ollama pull qwen2.5:7b
ollama pull llava:7b
```

### Database errors:
```bash
# Reset
dropdb sunflower
createdb sunflower
cd backend
alembic upgrade head
python -m scripts.seed
```

## 📁 Important Files

| File | Purpose |
|------|---------|
| `backend/.env` | Backend configuration |
| `frontend/.env` | Frontend configuration |
| `backend/alembic.ini` | Migration config |
| `backend/app/main.py` | Backend entry point |
| `frontend/src/main.tsx` | Frontend entry point |
| `backend/scripts/seed.py` | Seed script |

## 🎯 AI Admin Commands

```bash
# In AI chat (admin only):
list all diseases
create disease TestDisease with pathogen fungal
update disease TestDisease description to "New description"
delete disease TestDisease
list all symptoms
help
```

## 📊 Key Features

### Endpoints:
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/diagnosis/run` - Run diagnosis
- `POST /api/v1/ai/chat` - Chat with AI
- `POST /api/v1/ai/admin/chat` - Admin AI chat
- `GET /api/v1/diseases` - List diseases
- `POST /api/v1/feedback` - Submit feedback

### Pages:
- `/` - Landing page
- `/login` - Login
- `/check` - Diagnosis
- `/diseases` - Disease library
- `/history` - Diagnosis history
- `/feedback` - Submit feedback
- `/admin` - Admin dashboard
- `/admin/diseases` - Manage diseases
- `/admin/symptoms` - Manage symptoms
- `/admin/feedback` - Manage feedback
- `/admin/users` - Manage users

## 🔐 Permissions

| Permission | Grower | Expert | Admin |
|------------|--------|--------|-------|
| Run diagnosis | ✅ | ✅ | ✅ |
| View diseases | ✅ | ✅ | ✅ |
| Create diseases | ❌ | ✅ | ✅ |
| Delete diseases | ❌ | ❌ | ✅ |
| Submit feedback | ✅ | ✅ | ✅ |
| Manage feedback | ❌ | ✅ | ✅ |
| Manage users | ❌ | ❌ | ✅ |
| AI admin chat | ❌ | ✅ | ✅ |

## 🧹 Before Push

```bash
# Run cleanup
./cleanup.sh

# Check tests
cd backend && pytest
cd ../frontend && npm test

# Check build
cd frontend && npm run build

# Check git
git status

# Push
git add -A
git commit -m "Ready for deployment"
git push origin main
```

## 📚 Documentation

- **README.md** - Main overview
- **SETUP_INSTRUCTIONS.md** - Full setup guide
- **AI_ADMIN_COMMANDS.md** - AI commands
- **CLEANUP_GUIDE.md** - Cleanup before push
- **PRE_PUSH_CHECKLIST.md** - Pre-push checklist
- **docs/ARCHITECTURE.md** - System architecture

## 🆘 Get Help

1. Check logs (backend terminal or browser console)
2. Review documentation
3. Check SETUP_INSTRUCTIONS.md
4. Review error messages
5. Search GitHub issues

---

**Quick access to everything you need!** ⚡
