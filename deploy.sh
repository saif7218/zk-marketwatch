#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting deployment process...${NC}"

# Push to GitHub
echo -e "${BLUE}Pushing to GitHub...${NC}"
git add .
git commit -m "Deploy: Update deployment configurations"
git push origin main

# Deploy to Render
echo -e "${BLUE}Deploying backend to Render...${NC}"
curl -X POST https://api.render.com/deploy/srv-XXXXX?key=$RENDER_API_KEY

# Deploy to Vercel
echo -e "${BLUE}Deploying frontend to Vercel...${NC}"
vercel --prod

echo -e "${GREEN}Deployment process completed!${NC}"
echo -e "${GREEN}Backend URL: https://mart-price-tracker-backend.onrender.com${NC}"
echo -e "${GREEN}Frontend URL: https://mart-price-tracker.vercel.app${NC}" 