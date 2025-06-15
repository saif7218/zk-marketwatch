#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting deployment process...${NC}"

# Backend deployment
echo -e "${BLUE}📦 Deploying backend to Render...${NC}"
cd backend
git add .
git commit -m "Deploy backend to Render"
git push origin main
echo -e "${GREEN}✅ Backend deployment initiated${NC}"

# Frontend deployment
echo -e "${BLUE}📦 Deploying frontend to Vercel...${NC}"
cd ../frontend
git add .
git commit -m "Deploy frontend to Vercel"
git push origin main
echo -e "${GREEN}✅ Frontend deployment initiated${NC}"

echo -e "${GREEN}🎉 Deployment process completed!${NC}"
echo -e "${BLUE}📝 Next steps:${NC}"
echo "1. Wait for Render to complete backend deployment"
echo "2. Update NEXT_PUBLIC_BACKEND_URL in Vercel with your Render URL"
echo "3. Wait for Vercel to complete frontend deployment" 