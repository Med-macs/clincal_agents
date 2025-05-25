#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="gen-lang-client-0408541483" 
REGION="us-central1"
SERVICE_NAME="triage-api" 
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo -e "${BLUE}🚀 Deploying Clinical Agents to Google Cloud Run...${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Google Cloud SDK (gcloud) is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth print-identity-token &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not authenticated with Google Cloud. Please authenticate:${NC}"
    gcloud auth login
fi

# Set the project
echo -e "${BLUE}📍 Setting Google Cloud project...${NC}"
gcloud config set project ${PROJECT_ID}

# Build the container image
echo -e "${BLUE}🏗️  Building container image...${NC}"
gcloud builds submit --tag ${IMAGE_NAME}

# Deploy to Cloud Run
echo -e "${BLUE}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --port 8000 \
    --set-env-vars="ENVIRONMENT=production"

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format='value(status.url)')

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${BLUE}🌐 Service URL: ${SERVICE_URL}${NC}"
echo -e "${YELLOW}ℹ️  Note: Make sure to set up your environment variables in the Google Cloud Console${NC}" 