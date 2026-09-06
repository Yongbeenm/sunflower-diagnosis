# Doctor Sunflower v2 - Deployment Guide

## 🌻 Sunflower Disease Diagnosis Expert System

A comprehensive web application for diagnosing sunflower plant diseases using an expert system approach.

---

## 📋 Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **ORM**: SQLAlchemy
- **Authentication**: JWT with bcrypt
- **API Documentation**: Automatic via FastAPI/Swagger

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Routing**: React Router v6

---

## 🚀 Deployment Options

This project supports multiple deployment strategies:

###  1. **Vercel (Recommended for Frontend)**
### 2. **Railway / Render (Recommended for Full Stack)**
### 3. **Docker** (Recommended for Self-Hosting)
### 4. **Traditional VPS** (DigitalOcean, AWS, etc.)

---

## 📦 Project Structure

```
sunflower-diagnosis-v2/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   ├── core/           # Config & security
│   │   └── db/             # Database setup
│   ├── requirements.txt    # Python dependencies
│   ├── Procfile           # For Railway/Render
│   └── railway.json       # Railway configuration
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── components/    # Reusable components
│   │   ├── stores/        # State management
│   │   └── lib/           # Utilities & API client
│   ├── package.json       # Node dependencies
│   ├── vercel.json        # Vercel configuration
│   └── vite.config.ts     # Vite configuration
├── docker-compose.yml      # Docker setup
└── README.md              # This file
```

---

## 🔧 Environment Variables

### Backend (.env)
```bash
# Required
DATABASE_URL=sqlite:///./sunflower.db  # Or PostgreSQL URL for production
SECRET_KEY=your-secret-key-min-32-characters

# Optional (have defaults)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.vercel.app
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000  # Backend API URL
```

---

## 🐳 Docker Deployment (Easiest)

### Prerequisites
- Docker & Docker Compose installed

### Steps
```bash
# 1. Clone/navigate to project
cd sunflower-diagnosis-v2

# 2. Create environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. Update backend/.env with your SECRET_KEY
# 4. Update frontend/.env with your backend URL

# 5. Build and start
docker-compose up -d

# 6. Initialize database
docker-compose exec backend python init_db.py
docker-compose exec backend python seed_data.py
docker-compose exec backend python seed_symptoms.py

# Access:
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## 🚂 Railway Deployment

Railway is perfect for full-stack deployment with database.

### Backend Deployment

1. **Create Railway Account**: https://railway.app
2. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

3. **Login and Initialize**:
   ```bash
   cd backend
   railway login
   railway init
   ```

4. **Add PostgreSQL Database**:
   ```bash
   railway add
   # Select "PostgreSQL"
   ```

5. **Set Environment Variables**:
   ```bash
   railway variables set SECRET_KEY="your-secret-key-min-32-characters"
   railway variables set ALGORITHM="HS256"
   railway variables set ACCESS_TOKEN_EXPIRE_MINUTES="30"
   railway variables set CORS_ORIGINS="https://your-frontend.vercel.app"
   ```

6. **Deploy**:
   ```bash
   railway up
   ```

7. **Initialize Database** (one-time):
   ```bash
   railway run python init_db.py
   railway run python seed_data.py
   railway run python seed_symptoms.py
   ```

8. **Get Backend URL**:
   ```bash
   railway domain
   ```

### Frontend Deployment (Vercel)

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Deploy**:
   ```bash
   cd frontend
   vercel
   ```

3. **Set Environment Variable**:
   ```bash
   vercel env add VITE_API_URL
   # Enter your Railway backend URL (e.g., https://your-backend.railway.app)
   ```

4. **Redeploy with Environment**:
   ```bash
   vercel --prod
   ```

---

## 🎨 Vercel Frontend Only

If you already have a backend deployed elsewhere:

```bash
cd frontend

# Create vercel.json (already included)
vercel

# Set backend URL
vercel env add VITE_API_URL
# production

# Redeploy
vercel --prod
```

---

## 🖥️ VPS Deployment (Ubuntu/Debian)

### Prerequisites
- Ubuntu 20.04+ or Debian 11+
- sudo access
- Domain name (optional but recommended)

### Setup Script
```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python 3.10+
sudo apt install python3 python3-pip python3-venv -y

# 3. Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 4. Install Nginx
sudo apt install nginx -y

# 5. Clone project
git clone https://github.com/yourusername/sunflower-diagnosis-v2.git
cd sunflower-diagnosis-v2

# 6. Setup Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your settings

# Initialize database
python init_db.py
python seed_data.py
python seed_symptoms.py

# 7. Setup Frontend
cd ../frontend
npm install
npm run build

# 8. Configure Nginx
sudo nano /etc/nginx/sites-available/sunflower
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /path/to/sunflower-diagnosis-v2/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /docs {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

### Systemd Service
```bash
sudo nano /etc/systemd/system/sunflower-backend.service
```

```ini
[Unit]
Description=Sunflower Diagnosis Backend
After=network.target

[Service]
User=your-username
WorkingDirectory=/path/to/sunflower-diagnosis-v2/backend
Environment="PATH=/path/to/sunflower-diagnosis-v2/backend/venv/bin"
ExecStart=/path/to/sunflower-diagnosis-v2/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable sunflower-backend
sudo systemctl start sunflower-backend
sudo systemctl enable nginx
sudo systemctl restart nginx
```

---

## 🔐 Security Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` to a strong random value (32+ characters)
- [ ] Update `CORS_ORIGINS` to only include your actual domains
- [ ] Use PostgreSQL instead of SQLite for production
- [ ] Enable HTTPS (use Let's Encrypt/Certbot)
- [ ] Set up database backups
- [ ] Configure rate limiting
- [ ] Review and update user permissions
- [ ] Set up monitoring (Sentry, LogRocket, etc.)
- [ ] Configure CDN for static assets (optional)

---

## 📊 Database Management

### Backup
```bash
# SQLite
cp backend/sunflower.db backend/sunflower.db.backup

# PostgreSQL
pg_dump $DATABASE_URL > backup.sql
```

### Restore
```bash
# SQLite
cp backend/sunflower.db.backup backend/sunflower.db

# PostgreSQL
psql $DATABASE_URL < backup.sql
```

---

## 🧪 Testing Deployment

After deployment, test these endpoints:

1. **Backend Health**:
   ```bash
   curl https://your-backend.com/health
   ```

2. **API Documentation**:
   ```
   https://your-backend.com/docs
   ```

3. **Login Test**:
   ```bash
   curl -X POST https://your-backend.com/api/v1/auth/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin123"
   ```

4. **Frontend**:
   - Open https://your-frontend.com
   - Login with admin/admin123
   - Browse diseases
   - Test diagnosis feature

---

## 📞 Support & Maintenance

### Logs
```bash
# Railway
railway logs

# Docker
docker-compose logs -f

# Systemd
sudo journalctl -u sunflower-backend -f
```

### Updates
```bash
# Pull latest code
git pull

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
# Restart service

# Update frontend
cd frontend
npm install
npm run build
```

---

## 📝 Default Credentials

**After deployment, change these immediately!**

- **Admin**: admin / admin123
- **Doctor**: doctor / doctor123
- **User**: user / user123

---

## 🎉 Features

- ✅ 11 comprehensive sunflower disease profiles
- ✅ 37 symptoms for accurate diagnosis
- ✅ Expert system with confidence scoring
- ✅ Bilingual support (English & Khmer)
- ✅ User authentication & authorization
- ✅ Admin dashboard
- ✅ Diagnosis history tracking
- ✅ RESTful API with documentation
- ✅ Responsive design

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

---

**Built with ❤️ for farmers and agricultural professionals** 🌻
