# 🚀 Deployment Checklist

Use this checklist to ensure a smooth deployment of Doctor Sunflower v2.

---

## Pre-Deployment

### Repository Setup
- [ ] Initialize git repository
  ```bash
  cd sunflower-diagnosis-v2
  git init
  git add .
  git commit -m "Initial commit"
  ```
- [ ] Create GitHub repository
- [ ] Push code to GitHub
  ```bash
  git remote add origin https://github.com/YOUR_USERNAME/sunflower-diagnosis.git
  git branch -M main
  git push -u origin main
  ```

### Environment Configuration
- [ ] Copy environment templates
  ```bash
  cp backend/.env.example backend/.env
  cp frontend/.env.example frontend/.env
  ```
- [ ] Generate strong SECRET_KEY (32+ characters)
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- [ ] Update `backend/.env` with real values
- [ ] Update `frontend/.env` with backend URL

### Local Testing
- [ ] Test with Docker Compose
  ```bash
  docker-compose up -d
  docker-compose logs -f
  ```
- [ ] Verify backend responds at http://localhost:8000
- [ ] Verify frontend loads at http://localhost:3000
- [ ] Test login functionality
- [ ] Test diagnosis feature
- [ ] Check API documentation at http://localhost:8000/docs

---

## Deployment (Choose One Platform)

### Option A: Railway (Recommended)

#### Backend
- [ ] Create Railway account at https://railway.app
- [ ] Install Railway CLI: `npm install -g @railway/cli`
- [ ] Login: `railway login`
- [ ] Create new project: `railway init`
- [ ] Add PostgreSQL: `railway add` → Select PostgreSQL
- [ ] Set environment variables:
  - [ ] `SECRET_KEY` (generated above)
  - [ ] `ALGORITHM=HS256`
  - [ ] `ACCESS_TOKEN_EXPIRE_MINUTES=30`
  - [ ] `CORS_ORIGINS` (add frontend URL when ready)
- [ ] Deploy: `railway up`
- [ ] Generate domain: Settings → Generate Domain
- [ ] Copy backend URL
- [ ] Test: `curl https://your-backend.railway.app/health`

#### Frontend (Vercel)
- [ ] Create Vercel account at https://vercel.com
- [ ] Install Vercel CLI: `npm install -g vercel`
- [ ] Navigate to frontend: `cd frontend`
- [ ] Deploy: `vercel`
- [ ] Set environment variable:
  ```bash
  vercel env add VITE_API_URL
  # Paste your Railway backend URL
  ```
- [ ] Deploy to production: `vercel --prod`
- [ ] Copy frontend URL

#### Update CORS
- [ ] Go back to Railway
- [ ] Update `CORS_ORIGINS` to include frontend URL
- [ ] Redeploy if needed

---

### Option B: Render

#### Backend
- [ ] Create Render account at https://render.com
- [ ] New → Web Service
- [ ] Connect GitHub repository
- [ ] Configure:
  - Name: `sunflower-backend`
  - Root Directory: `backend`
  - Runtime: Python 3
  - Build Command: `pip install -r requirements.txt`
  - Start Command: See Procfile
- [ ] Add PostgreSQL database
- [ ] Set environment variables (same as Railway)
- [ ] Deploy
- [ ] Copy backend URL

#### Frontend
- [ ] New → Static Site
- [ ] Connect GitHub repository
- [ ] Configure:
  - Name: `sunflower-frontend`
  - Root Directory: `frontend`
  - Build Command: `npm install && npm run build`
  - Publish Directory: `dist`
- [ ] Set `VITE_API_URL` environment variable
- [ ] Deploy
- [ ] Copy frontend URL

---

### Option C: Docker on VPS

- [ ] Provision VPS (DigitalOcean, Linode, AWS, etc.)
- [ ] SSH into server
- [ ] Install Docker and Docker Compose
- [ ] Clone repository
- [ ] Configure environment files
- [ ] Run: `docker-compose up -d`
- [ ] Initialize database:
  ```bash
  docker-compose exec backend python init_db.py
  docker-compose exec backend python seed_data.py
  docker-compose exec backend python seed_symptoms.py
  ```
- [ ] Configure Nginx (optional, for custom domain)
- [ ] Set up SSL with Certbot
- [ ] Configure firewall (allow ports 80, 443, 22)
- [ ] Set up systemd service for auto-start

---

## Post-Deployment

### Testing
- [ ] Test backend health: `curl https://backend-url/health`
- [ ] Test API docs: Visit `https://backend-url/docs`
- [ ] Test frontend: Visit `https://frontend-url`
- [ ] Test login with default credentials
- [ ] Test disease library
- [ ] Test diagnosis feature
- [ ] Test in different browsers (Chrome, Firefox, Safari)
- [ ] Test on mobile devices
- [ ] Run deployment test script:
  ```bash
  chmod +x scripts/test-deployment.sh
  ./scripts/test-deployment.sh https://your-backend.com https://your-frontend.com
  ```

### Security
- [ ] Change all default user passwords
  - admin/admin123 → new password
  - doctor/doctor123 → new password
  - user/user123 → new password
- [ ] Verify CORS settings include only your domains
- [ ] Confirm HTTPS is enabled (check for 🔒 in browser)
- [ ] Review and update SECRET_KEY (if using default)
- [ ] Set up database backups
- [ ] Configure rate limiting (if not handled by platform)
- [ ] Review user permissions

### Monitoring
- [ ] Set up error monitoring (Sentry, etc.)
- [ ] Configure uptime monitoring (UptimeRobot, etc.)
- [ ] Set up log aggregation
- [ ] Configure alerts for errors/downtime
- [ ] Monitor database usage
- [ ] Check API response times

### Documentation
- [ ] Update README with deployment URLs
- [ ] Document any custom configuration
- [ ] Create admin guide for managing users
- [ ] Document backup/restore procedures
- [ ] Note any manual setup steps performed

---

## Maintenance

### Regular Tasks
- [ ] Weekly: Check logs for errors
- [ ] Weekly: Review database size
- [ ] Weekly: Check disk space (VPS)
- [ ] Monthly: Update dependencies
- [ ] Monthly: Review and rotate credentials
- [ ] Monthly: Test backup restoration
- [ ] Quarterly: Security audit
- [ ] Quarterly: Performance review

### Backup Strategy
- [ ] Set up automated daily backups
- [ ] Test backup restoration procedure
- [ ] Document backup location
- [ ] Set up off-site backup storage
- [ ] Define retention policy (e.g., keep 30 days)

### Update Procedure
1. [ ] Test updates locally
2. [ ] Create database backup
3. [ ] Deploy to staging (if available)
4. [ ] Run tests
5. [ ] Deploy to production
6. [ ] Verify functionality
7. [ ] Monitor for errors

---

## Rollback Plan

If deployment fails:

1. **Railway/Render**: Rollback to previous deployment
   - Railway: Deployments → Select previous → Rollback
   - Render: Deploys → Select previous → Redeploy

2. **Vercel**: Rollback deployment
   - Deployments → Previous → Promote to Production

3. **Docker**: Restore from backup
   ```bash
   docker-compose down
   git checkout previous-working-commit
   docker-compose up -d
   # Restore database if needed
   ```

---

## Support Contacts

- **Platform Support**:
  - Railway: https://railway.app/help
  - Render: https://render.com/docs/support
  - Vercel: https://vercel.com/support

- **Documentation**:
  - Project README: `README.md`
  - Deployment Guide: `DEPLOYMENT.md`
  - Features Guide: `FEATURES_WORKING.md`

---

## Success Criteria

Deployment is considered successful when:

- ✅ Backend responds to health checks
- ✅ Frontend loads without errors
- ✅ Login functionality works
- ✅ Disease library displays correctly
- ✅ Diagnosis feature returns results
- ✅ HTTPS is enabled
- ✅ All tests pass
- ✅ No critical errors in logs
- ✅ Response times are acceptable (<2s)
- ✅ Default credentials have been changed

---

**Date Deployed**: _______________

**Deployed By**: _______________

**Platform Used**: _______________

**Backend URL**: _______________

**Frontend URL**: _______________

**Notes**: 
