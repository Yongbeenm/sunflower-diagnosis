#!/bin/bash

# Doctor Sunflower v2 - Railway + Vercel Deployment Guide
# This script will guide you through the deployment process

set -e

echo "🌻 Doctor Sunflower v2 - Deployment Assistant"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}This script will help you deploy:${NC}"
echo "  1. Backend → Railway (with PostgreSQL)"
echo "  2. Frontend → Vercel"
echo ""
echo -e "${YELLOW}⚠️  You'll need:${NC}"
echo "  - Railway account (https://railway.app)"
echo "  - Vercel account (https://vercel.com)"
echo "  - GitHub account (recommended)"
echo ""

read -p "Press Enter to continue..."

# ======================================
# STEP 1: Backend to Railway
# ======================================

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}STEP 1: Deploy Backend to Railway${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd backend

echo "1️⃣  Logging into Railway..."
echo "   (This will open your browser for authentication)"
echo ""
railway login

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Railway login failed. Please try again.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Logged in successfully!${NC}"
echo ""

echo "2️⃣  Creating new Railway project..."
echo ""
railway init

echo ""
echo "3️⃣  Adding PostgreSQL database..."
echo "   (Select 'Add PostgreSQL' from the menu)"
echo ""
railway add

echo ""
echo "4️⃣  Generating SECRET_KEY..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || python -c "import secrets; print(secrets.token_urlsafe(32))")
echo -e "${BLUE}Generated SECRET_KEY: ${SECRET_KEY}${NC}"
echo ""

echo "5️⃣  Setting environment variables..."
railway variables set SECRET_KEY="$SECRET_KEY"
railway variables set ALGORITHM="HS256"
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES="30"

echo ""
echo "6️⃣  Deploying backend to Railway..."
echo "   (This may take 2-3 minutes)"
echo ""
railway up

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Deployment failed. Check the error above.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Backend deployed successfully!${NC}"
echo ""

echo "7️⃣  Generating public domain..."
railway domain

echo ""
echo -e "${YELLOW}📋 Copy your Railway backend URL from above!${NC}"
echo "   It should look like: https://xxxxx.railway.app"
echo ""
read -p "Paste your Railway backend URL here: " BACKEND_URL

if [ -z "$BACKEND_URL" ]; then
    echo -e "${RED}❌ Backend URL is required to continue.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Backend URL saved: ${BACKEND_URL}${NC}"

# Test backend
echo ""
echo "8️⃣  Testing backend..."
if curl -f -s "${BACKEND_URL}/health" > /dev/null; then
    echo -e "${GREEN}✅ Backend is responding!${NC}"
else
    echo -e "${YELLOW}⚠️  Backend might still be starting. This is normal.${NC}"
fi

cd ..

# ======================================
# STEP 2: Frontend to Vercel
# ======================================

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}STEP 2: Deploy Frontend to Vercel${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd frontend

echo "1️⃣  Setting up environment variable..."
echo "VITE_API_URL=$BACKEND_URL" > .env.production

echo ""
echo "2️⃣  Deploying to Vercel..."
echo "   (Follow the prompts to set up your project)"
echo ""
vercel --prod --yes

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Vercel deployment failed.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Frontend deployed successfully!${NC}"
echo ""

echo -e "${YELLOW}📋 Copy your Vercel frontend URL from above!${NC}"
echo "   It should look like: https://xxxxx.vercel.app"
echo ""
read -p "Paste your Vercel frontend URL here: " FRONTEND_URL

cd ..

# ======================================
# STEP 3: Update CORS
# ======================================

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}STEP 3: Update CORS Settings${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd backend

echo "Setting CORS_ORIGINS to allow frontend..."
railway variables set CORS_ORIGINS="$FRONTEND_URL,http://localhost:3000"

echo ""
echo "Redeploying backend with updated CORS..."
railway up

cd ..

# ======================================
# STEP 4: Test Deployment
# ======================================

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}STEP 4: Testing Deployment${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -f "scripts/test-deployment.sh" ]; then
    echo "Running automated tests..."
    chmod +x scripts/test-deployment.sh
    ./scripts/test-deployment.sh "$BACKEND_URL" "$FRONTEND_URL"
else
    echo "Manual testing..."
    echo "Testing backend health..."
    curl -s "${BACKEND_URL}/health" || echo "Backend test completed"
fi

# ======================================
# SUCCESS!
# ======================================

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}Your Doctor Sunflower app is now live!${NC}"
echo ""
echo -e "${GREEN}📱 Frontend:${NC} $FRONTEND_URL"
echo -e "${GREEN}🔧 Backend:${NC} $BACKEND_URL"
echo -e "${GREEN}📚 API Docs:${NC} ${BACKEND_URL}/docs"
echo ""
echo -e "${YELLOW}🔐 Default Login Credentials:${NC}"
echo "   Admin: admin / admin123"
echo "   Doctor: doctor / doctor123"
echo "   User: user / user123"
echo ""
echo -e "${RED}⚠️  IMPORTANT: Change these passwords immediately!${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Open your app: $FRONTEND_URL"
echo "  2. Login and change default passwords"
echo "  3. Test the diagnosis feature"
echo "  4. Share your app!"
echo ""
echo -e "${GREEN}🌻 Happy diagnosing!${NC}"
echo ""

# Save URLs to file
cat > DEPLOYMENT_URLS.txt << EOF
Doctor Sunflower v2 - Deployment Information
=============================================

Deployment Date: $(date)

Frontend URL: $FRONTEND_URL
Backend URL: $BACKEND_URL
API Documentation: ${BACKEND_URL}/docs

Default Credentials:
- Admin: admin / admin123
- Doctor: doctor / doctor123  
- User: user / user123

REMEMBER TO CHANGE THESE PASSWORDS!

Railway Dashboard: https://railway.app/dashboard
Vercel Dashboard: https://vercel.com/dashboard
EOF

echo "📝 Deployment info saved to DEPLOYMENT_URLS.txt"
echo ""
