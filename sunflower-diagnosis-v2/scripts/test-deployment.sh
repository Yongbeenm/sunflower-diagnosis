#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🧪 Testing Doctor Sunflower v2 Deployment"
echo "=========================================="
echo ""

# Check if backend URL is provided
if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: Backend URL not provided${NC}"
    echo "Usage: ./test-deployment.sh <backend-url> [frontend-url]"
    echo "Example: ./test-deployment.sh https://api.example.com https://example.com"
    exit 1
fi

BACKEND_URL=$1
FRONTEND_URL=${2:-""}

echo "Backend URL: $BACKEND_URL"
if [ -n "$FRONTEND_URL" ]; then
    echo "Frontend URL: $FRONTEND_URL"
fi
echo ""

# Test 1: Backend Health Check
echo "1️⃣  Testing Backend Health..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health" 2>/dev/null)

if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${RED}❌ Backend health check failed (HTTP $HEALTH_RESPONSE)${NC}"
    exit 1
fi

# Test 2: API Root Endpoint
echo ""
echo "2️⃣  Testing API Root..."
API_RESPONSE=$(curl -s "$BACKEND_URL/" 2>/dev/null)

if echo "$API_RESPONSE" | grep -q "Doctor Sunflower"; then
    echo -e "${GREEN}✅ API root endpoint working${NC}"
else
    echo -e "${RED}❌ API root endpoint failed${NC}"
    echo "Response: $API_RESPONSE"
fi

# Test 3: API Documentation
echo ""
echo "3️⃣  Testing API Documentation..."
DOCS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/docs" 2>/dev/null)

if [ "$DOCS_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ API documentation accessible${NC}"
    echo "   Visit: $BACKEND_URL/docs"
else
    echo -e "${YELLOW}⚠️  API docs returned HTTP $DOCS_RESPONSE${NC}"
fi

# Test 4: Diseases Endpoint
echo ""
echo "4️⃣  Testing Diseases Endpoint..."
DISEASES_RESPONSE=$(curl -s "$BACKEND_URL/api/v1/diseases/" 2>/dev/null)

if echo "$DISEASES_RESPONSE" | grep -q "total"; then
    DISEASE_COUNT=$(echo "$DISEASES_RESPONSE" | grep -o '"total":[0-9]*' | grep -o '[0-9]*')
    echo -e "${GREEN}✅ Diseases endpoint working ($DISEASE_COUNT diseases)${NC}"
else
    echo -e "${RED}❌ Diseases endpoint failed${NC}"
    echo "Response: $DISEASES_RESPONSE"
fi

# Test 5: Login Endpoint
echo ""
echo "5️⃣  Testing Login Endpoint..."
LOGIN_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/v1/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=admin123" 2>/dev/null)

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✅ Login endpoint working${NC}"
    echo -e "${YELLOW}⚠️  Remember to change default credentials!${NC}"
else
    echo -e "${RED}❌ Login endpoint failed${NC}"
    echo "Response: $LOGIN_RESPONSE"
fi

# Test 6: Symptoms Endpoint
echo ""
echo "6️⃣  Testing Symptoms Endpoint..."
SYMPTOMS_RESPONSE=$(curl -s "$BACKEND_URL/api/v1/symptoms/categories" 2>/dev/null)

if echo "$SYMPTOMS_RESPONSE" | grep -q "categories"; then
    CATEGORY_COUNT=$(echo "$SYMPTOMS_RESPONSE" | grep -o '"category"' | wc -l)
    echo -e "${GREEN}✅ Symptoms endpoint working ($CATEGORY_COUNT categories)${NC}"
else
    echo -e "${RED}❌ Symptoms endpoint failed${NC}"
fi

# Test 7: Frontend (if URL provided)
if [ -n "$FRONTEND_URL" ]; then
    echo ""
    echo "7️⃣  Testing Frontend..."
    FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" 2>/dev/null)
    
    if [ "$FRONTEND_RESPONSE" = "200" ]; then
        echo -e "${GREEN}✅ Frontend is accessible${NC}"
    else
        echo -e "${RED}❌ Frontend returned HTTP $FRONTEND_RESPONSE${NC}"
    fi
fi

# Summary
echo ""
echo "=========================================="
echo "🎉 Deployment Test Complete!"
echo ""
echo "📋 Quick Links:"
echo "   • Frontend: ${FRONTEND_URL:-'Not provided'}"
echo "   • Backend: $BACKEND_URL"
echo "   • API Docs: $BACKEND_URL/docs"
echo ""
echo "🔐 Default Credentials (CHANGE IMMEDIATELY):"
echo "   • Admin: admin / admin123"
echo "   • Doctor: doctor / doctor123"
echo "   • User: user / user123"
echo ""
echo -e "${YELLOW}⚠️  Security Checklist:${NC}"
echo "   1. Change all default passwords"
echo "   2. Verify CORS settings"
echo "   3. Enable HTTPS"
echo "   4. Set up database backups"
echo "   5. Configure monitoring"
echo ""
