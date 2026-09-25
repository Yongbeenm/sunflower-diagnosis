# Project Cleanup Guide

Files and folders to delete before pushing to GitHub.

## ❌ Files to DELETE (Temporary/Testing)

### Root Directory - Testing/Debug Files:
```bash
# Delete these files:
rm -f check_feedback.py
rm -f simple_test.py
rm -f test_admin_chat.py
rm -f check-admin.sh
rm -f add-database-env.sh
rm -f fix-database.sh
rm -f fix-delete-permissions.sql
```

### Root Directory - Redundant Documentation:
```bash
# Delete old/duplicate docs (keep only essential ones):
rm -f AI_CHANGELOG.md
rm -f AI_COMPLETE_SUMMARY.md
rm -f AI_IMPLEMENTATION_SUMMARY.md
rm -f AI_QUICKSTART.md
rm -f AI_SLIDE_GENERATION_PROMPTS.md
rm -f AI_TESTING_GUIDE.md
rm -f CRITICAL_FIX_APPLIED.md
rm -f DELETE_FIX_SUMMARY.md
rm -f FEEDBACK_FIX_SUMMARY.md
rm -f FEEDBACK_SCHEMA_FIX.md
rm -f FRONTEND_REDESIGN_PROMPT.md
rm -f INTENT_DETECTION_FLOW.md
rm -f PRESENTATION_SLIDES_OUTLINE.md
rm -f QUICK_TEST_GUIDE.md
rm -f README_AI_ADMIN_FIX.md
rm -f REDESIGN_CHANGELOG.md
rm -f TROUBLESHOOTING_DELETE.md
rm -f VIDEO_RECORDING_CHECKLIST.md
rm -f VIDEO_SCRIPT.md
```

### Root Directory - Deployment Scripts (if not using):
```bash
# If you're not deploying to Vercel, delete these:
rm -f deploy-frontend-fresh.sh
rm -f deploy-frontend.sh
rm -f deploy-simple.sh
rm -f deploy-to-vercel.sh
rm -f seed-production.sh
rm -f set-frontend-env.sh
rm -f setup-vercel-env.sh
rm -f fix-vercel-env.sh
rm -f setup-ai.sh
```

### macOS System Files:
```bash
# Delete .DS_Store files (macOS only)
find . -name ".DS_Store" -type f -delete
```

### Root Level .env (should only be in backend/frontend):
```bash
# Delete if exists (keep only in backend/ and frontend/)
rm -f .env
```

---

## ✅ Files to KEEP

### Essential Documentation:
- ✅ **README.md** - Main project documentation
- ✅ **SETUP_INSTRUCTIONS.md** - Setup guide for new developers
- ✅ **AI_ADMIN_COMMANDS.md** - AI admin feature documentation
- ✅ **AI_INTEGRATION.md** - AI integration guide
- ✅ **AI_PERMISSIONS.md** - Permission system documentation
- ✅ **FEEDBACK_SYSTEM_OVERVIEW.md** - Feedback feature documentation
- ✅ **.gitignore** - Git ignore rules
- ✅ **Makefile** - Convenient commands
- ✅ **docker-compose.yml** - Docker setup (if using Docker)

### Directories:
- ✅ **backend/** - Backend application
- ✅ **frontend/** - Frontend application
- ✅ **docs/** - Additional documentation
- ✅ **.git/** - Git repository

---

## Automated Cleanup Script

Run this to clean up automatically:

```bash
#!/bin/bash
# cleanup.sh

echo "🧹 Cleaning up temporary and redundant files..."

# Test files
rm -f check_feedback.py
rm -f simple_test.py
rm -f test_admin_chat.py
rm -f check-admin.sh
rm -f add-database-env.sh
rm -f fix-database.sh
rm -f fix-delete-permissions.sql

# Old documentation
rm -f AI_CHANGELOG.md
rm -f AI_COMPLETE_SUMMARY.md
rm -f AI_IMPLEMENTATION_SUMMARY.md
rm -f AI_QUICKSTART.md
rm -f AI_SLIDE_GENERATION_PROMPTS.md
rm -f AI_TESTING_GUIDE.md
rm -f CRITICAL_FIX_APPLIED.md
rm -f DELETE_FIX_SUMMARY.md
rm -f FEEDBACK_FIX_SUMMARY.md
rm -f FEEDBACK_SCHEMA_FIX.md
rm -f FRONTEND_REDESIGN_PROMPT.md
rm -f INTENT_DETECTION_FLOW.md
rm -f PRESENTATION_SLIDES_OUTLINE.md
rm -f QUICK_TEST_GUIDE.md
rm -f README_AI_ADMIN_FIX.md
rm -f REDESIGN_CHANGELOG.md
rm -f TROUBLESHOOTING_DELETE.md
rm -f VIDEO_RECORDING_CHECKLIST.md
rm -f VIDEO_SCRIPT.md

# Deployment scripts (uncomment if not using)
# rm -f deploy-frontend-fresh.sh
# rm -f deploy-frontend.sh
# rm -f deploy-simple.sh
# rm -f deploy-to-vercel.sh
# rm -f seed-production.sh
# rm -f set-frontend-env.sh
# rm -f setup-vercel-env.sh
# rm -f fix-vercel-env.sh
# rm -f setup-ai.sh

# macOS files
find . -name ".DS_Store" -type f -delete

# Root .env (keep only in backend/ and frontend/)
rm -f .env

echo "✅ Cleanup complete!"
echo ""
echo "Files kept:"
echo "  ✅ README.md"
echo "  ✅ SETUP_INSTRUCTIONS.md"
echo "  ✅ AI_ADMIN_COMMANDS.md"
echo "  ✅ AI_INTEGRATION.md"
echo "  ✅ AI_PERMISSIONS.md"
echo "  ✅ FEEDBACK_SYSTEM_OVERVIEW.md"
echo "  ✅ backend/"
echo "  ✅ frontend/"
echo "  ✅ docs/"
echo ""
echo "📝 Don't forget to:"
echo "  1. Review .gitignore"
echo "  2. Update README.md if needed"
echo "  3. Test the project still works"
echo "  4. Commit changes: git add -A && git commit -m 'Clean up project'"
```

Save as `cleanup.sh` and run:
```bash
chmod +x cleanup.sh
./cleanup.sh
```

---

## Final Project Structure (After Cleanup)

```
sunflower-expert/
├── README.md                      # Main documentation
├── SETUP_INSTRUCTIONS.md          # Setup guide
├── AI_ADMIN_COMMANDS.md           # AI features
├── AI_INTEGRATION.md              # AI integration
├── AI_PERMISSIONS.md              # Permissions
├── FEEDBACK_SYSTEM_OVERVIEW.md    # Feedback docs
├── .gitignore                     # Git ignore
├── Makefile                       # Commands
├── docker-compose.yml             # Docker setup
│
├── backend/                       # Backend app
│   ├── .env.example              # Example env file
│   ├── app/                      # Application code
│   ├── ai/                       # AI services
│   ├── alembic/                  # Migrations
│   ├── scripts/                  # Utility scripts
│   └── tests/                    # Tests
│
├── frontend/                      # Frontend app
│   ├── .env.example              # Example env file
│   ├── src/                      # Source code
│   └── public/                   # Static files
│
└── docs/                          # Additional docs
    └── ARCHITECTURE.md
```

---

## Before Pushing to GitHub

### 1. Run Cleanup:
```bash
./cleanup.sh
```

### 2. Update .gitignore:
```bash
# Make sure these are in .gitignore:
.env
.DS_Store
*.pyc
__pycache__/
node_modules/
dist/
.venv/
*.log
.vercel/
```

### 3. Review Secrets:
```bash
# Check for exposed secrets
grep -r "password\|secret\|key" --include="*.env" .
```

### 4. Test Build:
```bash
# Backend
cd backend
source .venv/bin/activate
pytest

# Frontend
cd frontend
npm run build
```

### 5. Update README.md:
- Add project description
- Add features list
- Add link to SETUP_INSTRUCTIONS.md
- Add license
- Add screenshots (optional)

### 6. Commit and Push:
```bash
git add -A
git commit -m "Clean up project structure"
git push origin main
```

---

## Recommended .gitignore Additions

Add these to root `.gitignore`:

```gitignore
# Cleanup script
cleanup.sh

# Test files
check_feedback.py
simple_test.py
test_admin_chat.py
*.sh

# Temporary docs
*_FIX_*.md
*_SUMMARY.md
*_GUIDE.md
CRITICAL_*.md
DELETE_*.md
FEEDBACK_FIX*.md
TROUBLESHOOTING_*.md
VIDEO_*.md
PRESENTATION_*.md

# Keep these:
!SETUP_INSTRUCTIONS.md
!FEEDBACK_SYSTEM_OVERVIEW.md
!AI_ADMIN_COMMANDS.md
!AI_INTEGRATION.md
!AI_PERMISSIONS.md
```

---

## Final Checklist

Before pushing to GitHub:

- [ ] Run cleanup script
- [ ] Delete test files
- [ ] Remove old documentation
- [ ] Update .gitignore
- [ ] Remove .env files from git
- [ ] Update README.md
- [ ] Test backend: `pytest`
- [ ] Test frontend: `npm run build`
- [ ] Review commit history
- [ ] Push to GitHub

---

**After cleanup, your project will be clean, organized, and ready for collaboration!** 🎉
