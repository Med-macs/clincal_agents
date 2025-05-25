#!/bin/bash

# Build and push Docker image
docker build -t clinical-agents .
docker tag clinical-agents:latest your-registry/clinical-agents:latest
docker push your-registry/clinical-agents:latest

# Deploy to your cloud platform (example for kubernetes)
kubectl apply -f k8s/
kubectl rollout restart deployment clinical-agents 