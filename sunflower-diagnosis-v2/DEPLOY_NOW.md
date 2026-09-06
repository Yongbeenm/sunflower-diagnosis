# 🚀 Deploy Now - Railway + Vercel

## Quick Deployment Guide (10 minutes)

Follow these steps to deploy your Doctor Sunflower app!

---

## 📋 Prerequisites

Before starting, make sure you have:
- ✅ Railway CLI installed (done!)
- ✅ Vercel CLI installed (done!)
- [ ] Railway account → Sign up at https://railway.app
- [ ] Vercel account → Sign up at https://vercel.com

---

## 🎯 Deployment Steps

### PART 1: Deploy Backend to Railway (5 minutes)

#### Step 1: Open Terminal in Backend Directory
```bash
cd sunflower-diagnosis-v2/backend
```

#### Step 2: Login to Railway
```bash
railway login
```
*This will open your browser. Login or sign up for Railway.*

#### Step 3: Create New Project
```bash
railway init
```
*Choose "Create new project" and give it a name like "sunflower-backend"*

#### Step 4: Add PostgreSQL Database
```bash
railway add
```
*Select "PostgreSQL" from the list*

#### Step 5: Generate and Set SECRET_KEY
```bash
# Generate a secure secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Copy the output, then set it (replace YOUR_GENERATED_KEY with the output):
railway variables set SECRET_KEY="YOUR_GENERATED_KEY"
railway variables set ALGORITHM="HS256"
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES="30"
```

#### Step 6: Deploy Backend
```bash
railway up
```
*This will take 2-3 minutes. Wait for "Deployment successful"*

#### Step 7: Get Your Backend URL
```bash
railway domain
```
*Copy the URL that appears (looks like: https://xxxxx.railway.app)*

#### Step 8: Test Backend
```bash
# Replace with your actual Railway URL
curl https://your-backend-url.railway.app/health
```
*You should see: {"status":"healthy"}*

**✅ BACKEND DEPLOYED!** Copy your Railway URL - you'll need it for the frontend.

---

### PART 2: Deploy Frontend to Vercel (5 minutes)

#### Step 9: Open Terminal in Frontend Directory
```bash
cd ../frontend
# (or: cd sunflower-diagnosis-v2/frontend)
```

#### Step 10: Set Backend URL
Create a `.env.production` file:
```bash
echo "VITE_API_URL=https://your-backend-url.railway.app" > .env.production
```
*Replace with your actual Railway URL from Step 7*

#### Step 11: Deploy to Vercel
```bash
vercel --prod
```

**Follow the prompts:**
- "Set up and deploy?" → **Y**
- "Which scope?" → Choose your account
- "Link to existing project?" → **N**
- "What's your project's name?" → **sunflower-frontend**
- "In which directory is your code located?" → **./** (press Enter)
- "Want to override the settings?" → **N**

*This will take 2-3 minutes.*

#### Step 12: Copy Your Frontend URL
After deployment completes, copy the Production URL (looks like: https://sunflower-frontend.vercel.app)

**✅ FRONTEND DEPLOYED!**

---

### PART 3: Update CORS Settings (2 minutes)

#### Step 13: Update Backend CORS
```bash
cd ../backend
# (or: cd sunflower-diagnosis-v2/backend)

# Replace with your Vercel URL from Step 12
railway variables set CORS_ORIGINS="https://your-frontend.vercel.app,http://localhost:3000"

# Redeploy
railway up
```

---

### PART 4: Test Your App! (1 minute)

#### Step 14: Open Your App
```bash
# Open frontend in browser
open https://your-frontend.vercel.app
```

#### Step 15: Test Login
- Username: **admin**
- Password: **admin123**

#### Step 16: Explore
- View Disease Library
- Try the Diagnosis Feature
- Check different languages (EN/KM)

---

## 🎉 SUCCESS!

Your app is now live at:
- **Frontend**: https://your-frontend.vercel.app
- **Backend**: https://your-backend-url.railway.app
- **API Docs**: https://your-backend-url.railway.app/docs

---

## 🔐 IMPORTANT: Change Default Passwords!

1. Login to your app with **admin/admin123**
2. Go to your profile
3. Change the password
4. Create new admin accounts
5. Consider disabling/deleting default accounts

---

## 🧪 Test Your Deployment

Run the automated test:
```bash
cd sunflower-diagnosis-v2
./scripts/test-deployment.sh https://your-backend.railway.app https://your-frontend.vercel.app
```

---

## 📊 Managing Your Deployment

### View Logs

**Backend (Railway):**
```bash
cd backend
railway logs
```

**Frontend (Vercel):**
```bash
cd frontend
vercel logs
```

### Update Deployment

**Backend:**
```bash
cd backend
railway up
```

**Frontend:**
```bash
cd frontend
vercel --prod
```

### View Dashboards

**Railway:** https://railway.app/dashboard
**Vercel:** https://vercel.com/dashboard

---

## ❓ Troubleshooting

### "Backend won't start"
Check environment variables in Railway dashboard:
- `SECRET_KEY` should be set
- `DATABASE_URL` should be auto-set by PostgreSQL

### "Frontend can't connect to backend"
1. Check `.env.production` has correct Railway URL
2. Verify CORS_ORIGINS includes your Vercel URL
3. Test backend directly: `curl https://your-backend.railway.app/health`

### "CORS error in browser console"
Update CORS settings:
```bash
cd backend
railway variables set CORS_ORIGINS="https://your-frontend.vercel.app"
railway up
```

### "Database empty / no diseases"
The database should initialize automatically. If not:
```bash
railway run python init_db.py
railway run python seed_data.py
railway run python seed_symptoms.py
```

---

## 💰 Costs

**Railway:**
- Free tier: $5 credit per month
- Enough for small projects
- Upgrade: $5/month for more resources

**Vercel:**
- Free tier: Unlimited personal projects
- No credit card required
- Upgrade: $20/month for teams

---

## 🎓 What You Just Did

You've successfully:
1. ✅ Deployed a Python FastAPI backend to Railway
2. ✅ Set up a PostgreSQL database
3. ✅ Deployed a React TypeScript frontend to Vercel
4. ✅ Configured environment variables
5. ✅ Set up CORS for cross-origin requests
6. ✅ Created a production-ready application

---

## 📚 Next Steps

1. **Customize your app** - Add more diseases, update UI
2. **Set up monitoring** - Use Railway/Vercel built-in monitoring
3. **Add custom domain** - Configure in Railway/Vercel dashboards
4. **Share with users** - Send them your Vercel URL
5. **Keep it updated** - Redeploy when you make changes

---

## 🆘 Need Help?

- **Railway Docs**: https://docs.railway.app
- **Vercel Docs**: https://vercel.com/docs
- **Project Docs**: Check DEPLOYMENT.md for more details

---

**Congratulations on deploying your app! 🌻🎉**
