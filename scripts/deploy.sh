#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"  # Default region
SERVICE_NAME="clinical-agents"
IMAGE_NAME="clinical-agents"

echo -e "${BLUE}🚀 Deploying $SERVICE_NAME to Google Cloud Run...${NC}"

# Build the Docker image
echo -e "${BLUE}📦 Building Docker image...${NC}"
docker build -t "$IMAGE_NAME" .

# Tag the image for Google Container Registry
echo -e "${BLUE}🏷️  Tagging image for GCR...${NC}"
docker tag "$IMAGE_NAME" "gcr.io/$PROJECT_ID/$IMAGE_NAME"

# Push the image to Google Container Registry
echo -e "${BLUE}⬆️  Pushing image to GCR...${NC}"
docker push "gcr.io/$PROJECT_ID/$IMAGE_NAME"

# Deploy to Cloud Run
echo -e "${BLUE}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy "$SERVICE_NAME" \
  --image "gcr.io/$PROJECT_ID/$IMAGE_NAME" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --set-env-vars "ENVIRONMENT=production" \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1

# Get the service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format 'value(status.url)')

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${BLUE}🌎 Service URL: ${NC}$SERVICE_URL" 