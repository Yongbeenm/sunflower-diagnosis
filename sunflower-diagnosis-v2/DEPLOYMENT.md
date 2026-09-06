# 🚀 Deployment Guide - Doctor Sunflower v2

This guide provides step-by-step instructions for deploying the application to various platforms.

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure you have:

- [ ] Generated a strong `SECRET_KEY` (32+ characters)
- [ ] Updated `CORS_ORIGINS` with your frontend domain(s)
- [ ] Tested locally with `docker-compose` or manual setup
- [ ] Prepared your GitHub repository (if using Git-based deployment)
- [ ] Read through the deployment option that suits your needs

---

## 🎯 Deployment Options Comparison

| Platform | Best For | Cost | Difficulty | Database Included |
|----------|----------|------|------------|-------------------|
| **Railway** | Full-stack, beginners | Free tier available | ⭐ Easy | ✅ Yes (PostgreSQL) |
| **Render** | Full-stack, simple | Free tier available | ⭐ Easy | ✅ Yes (PostgreSQL) |
| **Vercel + Railway** | Separate frontend/backend | Free tiers | ⭐⭐ Medium | ✅ Railway has DB |
| **Docker (VPS)** | Self-hosted, control | VPS cost (~$5/mo) | ⭐⭐⭐ Advanced | ✅ Yes (PostgreSQL) |
| **DigitalOcean App Platform** | Managed, scalable | Starts at $5/mo | ⭐⭐ Medium | ✅ Yes (managed DB) |

---

## 1️⃣ Railway Deployment (Recommended for Beginners)

Railway provides the easiest full-stack deployment with automatic PostgreSQL database.

### Step 1: Prepare Your Repository

```bash
cd sunflower-diagnosis-v2
git init
git add .
git commit -m "Initial commit for deployment"

# Push to GitHub
gh repo create sunflower-diagnosis --public
git remote add origin https://github.com/YOUR_USERNAME/sunflower-diagnosis.git
git push -u origin main
```

### Step 2: Deploy Backend

1. **Go to** https://railway.app
2. **Sign up** with GitHub
3. **Create New Project** → **Deploy from GitHub repo**
4. **Select** your `sunflower-diagnosis` repository
5. **Select** `backend` directory as root
6. **Add PostgreSQL**:
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway automatically connects it via `DATABASE_URL`

7. **Set Environment Variables**:
   ```
   SECRET_KEY = generate-a-random-32-character-string-here
   ALGORITHM = HS256
   ACCESS_TOKEN_EXPIRE_MINUTES = 30
   REFRESH_TOKEN_EXPIRE_DAYS = 7
   CORS_ORIGINS = https://your-frontend-url.vercel.app,http://localhost:3000
   ```

8. **Generate Domain**:
   - Go to Settings → Generate Domain
   - Copy your backend URL (e.g., `https://sunflower-backend.up.railway.app`)

9. **Check Logs**:
   - View deployment logs
   - Wait for "Database setup complete!" message
   - Test: `curl https://your-backend-url.railway.app/health`

### Step 3: Deploy Frontend (Vercel)

1. **Go to** https://vercel.com
2. **Sign up** with GitHub
3. **Import Project** → Select your repository
4. **Configure**:
   - Framework Preset: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`

5. **Environment Variables**:
   ```
   VITE_API_URL = https://your-backend-url.railway.app
   ```

6. **Deploy**!
7. **Test**: Visit your Vercel URL

### Step 4: Update CORS

Go back to Railway → Backend → Variables:
```
CORS_ORIGINS = https://your-frontend.vercel.app
```

Redeploy backend if needed.

---

## 2️⃣ Render Deployment

Render is similar to Railway but with different pricing tiers.

### Backend on Render

1. **Go to** https://render.com
2. **New** → **Web Service**
3. **Connect GitHub** repository
4. **Configure**:
   - Name: `sunflower-backend`
   - Root Directory: `backend`
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python init_db.py && python seed_data.py && python seed_symptoms.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. **Add PostgreSQL**:
   - Dashboard → New → PostgreSQL
   - Connect to your web service

6. **Environment Variables**:
   ```
   SECRET_KEY = your-secret-key
   DATABASE_URL = (auto-filled by Render)
   CORS_ORIGINS = https://your-frontend-url.onrender.com
   ```

7. **Deploy** and note your backend URL

### Frontend on Render

1. **New** → **Static Site**
2. **Configure**:
   - Name: `sunflower-frontend`
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`

3. **Environment Variables**:
   ```
   VITE_API_URL = https://your-backend-url.onrender.com
   ```

4. **Deploy**!

---

## 3️⃣ Docker Deployment (VPS)

For DigitalOcean, AWS EC2, Linode, etc.

### Prerequisites
- VPS with Ubuntu 20.04+
- Domain name pointed to VPS IP (optional but recommended)
- SSH access

### Step 1: Prepare VPS

```bash
# SSH into your VPS
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install docker-compose -y

# Install Git
apt install git -y
```

### Step 2: Clone and Configure

```bash
# Clone repository
cd /opt
git clone https://github.com/YOUR_USERNAME/sunflower-diagnosis.git
cd sunflower-diagnosis/sunflower-diagnosis-v2

# Create environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit backend/.env
nano backend/.env
# Set: SECRET_KEY, DATABASE_URL=postgresql://sunflower:sunflower@db:5432/sunflower

# Edit frontend/.env
nano frontend/.env
# Set: VITE_API_URL=https://your-domain.com (or http://your-ip:8000)
```

### Step 3: Deploy with Docker Compose

```bash
# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Initialize database (one-time)
docker-compose exec backend python init_db.py
docker-compose exec backend python seed_data.py
docker-compose exec backend python seed_symptoms.py
```

### Step 4: Configure Nginx (Optional - for custom domain)

```bash
apt install nginx certbot python3-certbot-nginx -y

# Create nginx config
nano /etc/nginx/sites-available/sunflower
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /docs {
        proxy_pass http://localhost:8000;
    }
}
```

```bash
# Enable site
ln -s /etc/nginx/sites-available/sunflower /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Get SSL certificate (if using domain)
certbot --nginx -d your-domain.com
```

### Step 5: Set Up Auto-Start

```bash
# Create systemd service
nano /etc/systemd/system/sunflower.service
```

```ini
[Unit]
Description=Sunflower Diagnosis Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/sunflower-diagnosis/sunflower-diagnosis-v2
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down

[Install]
WantedBy=multi-user.target
```

```bash
systemctl enable sunflower
systemctl start sunflower
```

---

## 4️⃣ DigitalOcean App Platform

Easy managed deployment with automatic SSL.

### Steps:

1. **Go to** https://cloud.digitalocean.com
2. **Create** → **Apps**
3. **Connect GitHub** repository
4. **Configure Backend**:
   - Type: Web Service
   - Source Directory: `/backend`
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `python init_db.py && python seed_data.py && python seed_symptoms.py && uvicorn app.main:app --host 0.0.0.0 --port 8080`
   - HTTP Port: 8080

5. **Add PostgreSQL Database**:
   - Add Resource → Database → PostgreSQL
   - Will auto-inject `DATABASE_URL`

6. **Configure Frontend**:
   - Type: Static Site
   - Source Directory: `/frontend`
   - Build Command: `npm install && npm run build`
   - Output Directory: `dist`

7. **Environment Variables**:
   Backend:
   ```
   SECRET_KEY = your-secret-key
   CORS_ORIGINS = ${frontend._URL}
   ```
   Frontend:
   ```
   VITE_API_URL = ${backend._URL}
   ```

8. **Deploy**!

---

## 🔐 Post-Deployment Security

After deployment, immediately:

1. **Change Default Credentials**:
   - Login as admin (admin/admin123)
   - Go to Profile → Change Password
   - Create new admin account
   - Delete default accounts

2. **Verify CORS**:
   - Test login from your frontend domain
   - Check browser console for CORS errors

3. **Enable HTTPS**:
   - Vercel/Railway/Render: Automatic
   - VPS: Use Certbot (see Docker guide above)

4. **Set Up Backups**:
   ```bash
   # Add to crontab (VPS)
   0 2 * * * docker exec sunflower-db pg_dump -U sunflower sunflower > /backups/sunflower-$(date +\%Y\%m\%d).sql
   ```

5. **Monitor Logs**:
   - Railway: Built-in logs viewer
   - Render: Logs tab
   - VPS: `docker-compose logs -f`

---

## 🧪 Testing Your Deployment

### Backend API Test
```bash
# Health check
curl https://your-backend-url.com/health

# API docs (should load in browser)
https://your-backend-url.com/docs

# Login test
curl -X POST https://your-backend-url.com/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Diseases endpoint
curl https://your-backend-url.com/api/v1/diseases/
```

### Frontend Test
1. Open https://your-frontend-url.com
2. Try login with admin/admin123
3. Browse diseases
4. Test diagnosis feature
5. Check browser console for errors

---

## 🔄 Updating Your Deployment

### Railway/Render (Git-based)
```bash
# Make changes locally
git add .
git commit -m "Update features"
git push

# Railway/Render auto-deploys on push
```

### Docker (VPS)
```bash
ssh root@your-server-ip
cd /opt/sunflower-diagnosis/sunflower-diagnosis-v2

# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check logs
docker-compose logs -f
```

---

## ❓ Troubleshooting

### Backend won't start
- Check logs for errors
- Verify `DATABASE_URL` is set correctly
- Ensure SECRET_KEY is set
- Check if database is accessible

### Frontend can't connect to backend
- Verify `VITE_API_URL` is correct
- Check CORS_ORIGINS includes your frontend domain
- Test backend URL directly (https://backend-url.com/health)
- Check browser console for detailed errors

### Database connection issues
- Verify DATABASE_URL format
- Check database is running (Docker: `docker-compose ps`)
- Test connection: `psql $DATABASE_URL`

### 502/503 Errors
- Service might be starting (wait 30 seconds)
- Check if service crashed (view logs)
- Verify port bindings are correct

---

## 📞 Getting Help

- Check logs first (most issues are logged)
- Test each component separately (backend, frontend, database)
- Verify environment variables are set correctly
- Check platform-specific documentation:
  - Railway: https://docs.railway.app
  - Render: https://render.com/docs
  - Vercel: https://vercel.com/docs
  - DigitalOcean: https://docs.digitalocean.com

---

**You're now ready to deploy Doctor Sunflower v2!** 🌻🚀

Choose the deployment method that best fits your needs and follow the guide above.
