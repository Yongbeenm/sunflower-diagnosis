# Pre-Push Checklist ✅

Complete this checklist before pushing to GitHub.

## 1. Cleanup Project

### Run Cleanup Script:
```bash
chmod +x cleanup.sh
./cleanup.sh
```

### Manual Verification:
- [ ] Test files removed (check_feedback.py, test_admin_chat.py, etc.)
- [ ] Old documentation removed (AI_CHANGELOG.md, DELETE_FIX_SUMMARY.md, etc.)
- [ ] .DS_Store files deleted
- [ ] Root .env file removed (keep only backend/.env and frontend/.env)

---

## 2. Secure Secrets

### Check for Exposed Secrets:
```bash
# Search for passwords/keys
grep -r "password\|secret\|key\|token" --include="*.env" .

# Make sure .env files are in .gitignore
grep ".env" .gitignore
```

### Update .env Files:
- [ ] Backend `.env.example` has no real secrets
- [ ] Frontend `.env.example` has no real secrets
- [ ] Real `.env` files are NOT tracked by git
- [ ] JWT_SECRET is strong (not default value)
- [ ] Database password is secure
- [ ] ADMIN_PASSWORD is changed from default

---

## 3. Update Documentation

### README.md:
- [ ] Project description is clear
- [ ] Features list is accurate
- [ ] Quick start guide works
- [ ] Links to other docs are correct
- [ ] License is specified (if needed)
- [ ] Contact/support info added

### SETUP_INSTRUCTIONS.md:
- [ ] Prerequisites list is complete
- [ ] Installation steps are tested
- [ ] Default credentials documented
- [ ] Environment variables explained
- [ ] Common issues covered

---

## 4. Code Quality

### Backend:
```bash
cd backend
source .venv/bin/activate

# Run tests
pytest

# Check linting
ruff format . --check
ruff check .

# Type checking
mypy app
```

- [ ] All tests pass
- [ ] No linting errors
- [ ] No type errors
- [ ] No unused imports

### Frontend:
```bash
cd frontend

# Run tests
npm test

# Check linting
npm run lint

# Type checking
npm run typecheck

# Build succeeds
npm run build
```

- [ ] All tests pass
- [ ] No linting errors
- [ ] No type errors
- [ ] Build succeeds without warnings

---

## 5. Git Status

### Check Git:
```bash
# Check what's tracked
git status

# Check for large files
git ls-files | xargs ls -lh | sort -k5 -hr | head -20
```

### Update .gitignore:
```gitignore
# Environment
.env
.env.local

# Python
__pycache__/
*.pyc
.venv/
*.egg-info/

# Node
node_modules/
dist/
.vercel/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Test
.pytest_cache/
coverage/

# Deployment scripts (optional)
*.sh
!cleanup.sh

# Temp docs (optional)
*_FIX_*.md
*_SUMMARY.md
CRITICAL_*.md
```

- [ ] .gitignore is complete
- [ ] No .env files tracked
- [ ] No node_modules tracked
- [ ] No .venv tracked
- [ ] No large binary files
- [ ] No sensitive data

---

## 6. Database

### Migrations:
```bash
cd backend
source .venv/bin/activate

# Check migration status
alembic current

# Verify latest migration
alembic upgrade head

# Test downgrade/upgrade
alembic downgrade -1
alembic upgrade head
```

- [ ] All migrations work
- [ ] No pending migrations
- [ ] Seed script works
- [ ] No hardcoded data in migrations

---

## 7. Dependencies

### Backend:
```bash
cd backend

# Check outdated packages
pip list --outdated

# Update if needed
pip install --upgrade <package>
```

- [ ] No critical security vulnerabilities
- [ ] Dependencies are up to date (or pinned intentionally)
- [ ] requirements.txt matches pyproject.toml

### Frontend:
```bash
cd frontend

# Check outdated packages
npm outdated

# Check vulnerabilities
npm audit
```

- [ ] No high/critical vulnerabilities
- [ ] Dependencies are up to date
- [ ] package-lock.json is committed

---

## 8. Environment Files

### Backend .env.example:
```bash
# Should contain:
# - All required variables
# - Example values (not real secrets)
# - Comments explaining each variable
```

- [ ] All variables documented
- [ ] No real secrets
- [ ] Comments are helpful
- [ ] Matches actual .env structure

### Frontend .env.example:
```bash
# Should contain:
# - VITE_API_BASE_URL
# - Other public config
```

- [ ] All variables documented
- [ ] No secrets
- [ ] Comments added

---

## 9. Testing

### Full System Test:
```bash
# 1. Fresh database
dropdb sunflower && createdb sunflower

# 2. Run migrations
cd backend
alembic upgrade head
python -m scripts.seed

# 3. Start backend
uvicorn app.main:app --reload

# 4. Start frontend (new terminal)
cd frontend
npm run dev

# 5. Start Ollama (new terminal)
ollama serve
```

**Manual Tests:**
- [ ] Login as admin works
- [ ] Login as expert works
- [ ] Login as grower works
- [ ] Run diagnosis works
- [ ] AI chat works
- [ ] AI admin chat works (admin only)
- [ ] Feedback submission works
- [ ] Feedback management works (admin)
- [ ] Disease management works
- [ ] Symptom management works
- [ ] Analytics page loads
- [ ] Language switching works

---

## 10. Commit History

### Review Commits:
```bash
git log --oneline -20
```

- [ ] Commit messages are clear
- [ ] No sensitive data in commits
- [ ] No "WIP" or "test" commits
- [ ] Logical commit structure

### Clean Up History (if needed):
```bash
# Interactive rebase (BE CAREFUL!)
git rebase -i HEAD~10

# Squash commits if needed
# Change "pick" to "squash" for commits to combine
```

---

## 11. Final Check

### Documentation:
- [ ] README.md is complete
- [ ] SETUP_INSTRUCTIONS.md is accurate
- [ ] API documentation is up to date
- [ ] Comments in code are helpful
- [ ] No TODO comments left

### Code:
- [ ] No console.log left in production code
- [ ] No print() statements for debugging
- [ ] No commented-out code blocks
- [ ] No hardcoded URLs or credentials
- [ ] Error handling is proper

### Files:
- [ ] Only necessary files included
- [ ] No temporary files
- [ ] No backup files (.bak, .old)
- [ ] No editor files (.swp, .swo)

---

## 12. Push to GitHub

### First Time:
```bash
# Add remote
git remote add origin <your-github-repo-url>

# Push
git push -u origin main
```

### Regular Push:
```bash
# Stage all changes
git add -A

# Commit
git commit -m "Clean up project and prepare for deployment"

# Push
git push origin main
```

### After Push:
- [ ] Check GitHub repository
- [ ] Verify all files uploaded
- [ ] Check .gitignore worked (no .env files)
- [ ] README renders correctly
- [ ] No secrets exposed

---

## 13. GitHub Repository Setup

### Settings:
- [ ] Add project description
- [ ] Add topics/tags
- [ ] Add website URL (if deployed)
- [ ] Add license
- [ ] Enable issues
- [ ] Set up branch protection (optional)

### README Badges (Optional):
```markdown
![Python](https://img.shields.io/badge/python-3.12-blue)
![Node](https://img.shields.io/badge/node-18-green)
![License](https://img.shields.io/badge/license-MIT-blue)
```

---

## 14. Post-Push

### Verify:
- [ ] Clone in fresh directory
- [ ] Follow SETUP_INSTRUCTIONS.md
- [ ] System runs successfully
- [ ] All features work

### Next Steps:
- [ ] Set up CI/CD (optional)
- [ ] Deploy to production (optional)
- [ ] Share with team
- [ ] Create first release/tag

---

## Summary

**Before pushing, make sure:**
1. ✅ Project is cleaned up
2. ✅ No secrets exposed
3. ✅ Documentation is complete
4. ✅ All tests pass
5. ✅ Code is clean
6. ✅ .gitignore works
7. ✅ Commit history is clean
8. ✅ Ready for collaboration

**Run this final command:**
```bash
# Full check
./cleanup.sh && \
cd backend && pytest && cd .. && \
cd frontend && npm run build && cd .. && \
git status
```

If everything is ✅, you're ready to push! 🚀

---

**Good luck with your project!** 🌻
