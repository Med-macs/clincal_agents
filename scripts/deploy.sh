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
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"  # Default region
SERVICE_NAME="clinical-agents"
IMAGE_NAME="clinical-agents"

# Show usage information
usage() {
    echo -e "${BLUE}Usage: $0 [STAGE]${NC}"
    echo
    echo "Available stages:"
    echo "  check       - Run pre-deployment checks"
    echo "  build       - Build and tag Docker image"
    echo "  push        - Push image to Google Container Registry"
    echo "  deploy      - Deploy to Cloud Run"
    echo "  all         - Run all stages (default)"
    echo
    exit 1
}

# Pre-deployment checks
check_prerequisites() {
    echo -e "${BLUE}📋 Running pre-deployment checks...${NC}"
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLI is not installed. Please install it first.${NC}"
        exit 1
    fi

    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed. Please install it first.${NC}"
        exit 1
    fi

    # Check if user is authenticated with gcloud
    if ! gcloud auth print-identity-token &> /dev/null; then
        echo -e "${RED}❌ Not authenticated with Google Cloud. Please run:${NC}"
        echo "gcloud auth login"
        exit 1
    fi

    # Check if Docker is configured for GCR
    if ! grep -q "gcr.io" ~/.docker/config.json 2>/dev/null; then
        echo -e "${RED}❌ Docker is not configured for Google Container Registry. Please run:${NC}"
        echo "gcloud auth configure-docker"
        exit 1
    fi

    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}❌ No Google Cloud project selected. Please run:${NC}"
        echo "gcloud config set project PROJECT_ID"
        exit 1
    fi

    # Load environment variables from .env if it exists
    if [ -f .env ]; then
        echo -e "${BLUE}📝 Loading environment variables from .env${NC}"
        set -a
        source .env
        set +a
    fi

    # Check required environment variables
    for var in "SUPABASE_URL" "SUPABASE_KEY" "GOOGLE_API_KEY"; do
        if [ -z "${!var}" ]; then
            echo -e "${RED}❌ Error: $var is not set${NC}"
            exit 1
        fi
    done

    echo -e "${GREEN}✅ All pre-deployment checks passed${NC}"
}

# Build Docker image
build_image() {
    echo -e "${BLUE}📦 Building and tagging Docker image...${NC}"
    
    # Build the Docker image
    docker build -t "$IMAGE_NAME" \
        --build-arg SUPABASE_URL="${SUPABASE_URL}" \
        --build-arg SUPABASE_KEY="${SUPABASE_KEY}" \
        --build-arg GOOGLE_API_KEY="${GOOGLE_API_KEY}" \
        .

    # Tag the image for Google Container Registry
    docker tag "$IMAGE_NAME" "gcr.io/$PROJECT_ID/$IMAGE_NAME"
    
    echo -e "${GREEN}✅ Docker image built and tagged${NC}"
}

# Push to GCR
push_image() {
    echo -e "${BLUE}⬆️  Pushing image to Google Container Registry...${NC}"
    
    docker push "gcr.io/$PROJECT_ID/$IMAGE_NAME"
    
    echo -e "${GREEN}✅ Image pushed to GCR${NC}"
}

# Deploy to Cloud Run
deploy_service() {
    echo -e "${BLUE}🚀 Deploying to Cloud Run...${NC}"
    
    gcloud run deploy "$SERVICE_NAME" \
        --image "gcr.io/$PROJECT_ID/$IMAGE_NAME" \
        --platform managed \
        --region "$REGION" \
        --allow-unauthenticated \
        --set-env-vars "ENVIRONMENT=production,SUPABASE_URL=${SUPABASE_URL},SUPABASE_KEY=${SUPABASE_KEY},GOOGLE_API_KEY=${GOOGLE_API_KEY}" \
        --memory 2Gi \
        --cpu 2 \
        --min-instances 1 \
        --port 8000

    # Get the service URL
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format 'value(status.url)')
    
    echo -e "${GREEN}✅ Deployment complete!${NC}"
    echo -e "${BLUE}🌎 Service URL: ${NC}$SERVICE_URL"
}

# Main execution
case ${1:-all} in
    check)
        check_prerequisites
        ;;
    build)
        check_prerequisites
        build_image
        ;;
    push)
        check_prerequisites
        push_image
        ;;
    deploy)
        check_prerequisites
        deploy_service
        ;;
    all)
        check_prerequisites
        build_image
        push_image
        deploy_service
        ;;
    *)
        usage
        ;;
esac 