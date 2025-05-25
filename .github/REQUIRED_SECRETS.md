# Required GitHub Secrets for GCP Deployment

The following secrets need to be configured in your GitHub repository settings (Settings > Secrets and variables > Actions):

## GCP_PROJECT_ID
Your Google Cloud Project ID

## GCP_WORKLOAD_IDENTITY_PROVIDER
The Workload Identity Provider URL from GCP. You can get this by running:
```bash
gcloud iam workload-identity-pools providers describe "github" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="github-actions" \
  --format="value(name)"
```

## GCP_SA_EMAIL
The service account email address that will be used for deployment. You can get this by running:
```bash
gcloud iam service-accounts list \
  --project="${PROJECT_ID}" \
  --filter="email ~ ^github-actions" \
  --format="value(email)"
```

# Setup Instructions

1. Create a Workload Identity Pool:
```bash
gcloud iam workload-identity-pools create "github-actions" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --display-name="GitHub Actions Pool"
```

2. Create a Workload Identity Provider:
```bash
gcloud iam workload-identity-pools providers create-oidc "github" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="github-actions" \
  --display-name="GitHub provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"
```

3. Create a Service Account:
```bash
gcloud iam service-accounts create "github-actions" \
  --project="${PROJECT_ID}" \
  --display-name="GitHub Actions Service Account"
```

4. Grant necessary permissions:
```bash
# Allow deploying to Cloud Run
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/run.admin"

# Allow pushing to Container Registry
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Allow service account user
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

5. Configure Workload Identity Federation:
```bash
gcloud iam service-accounts add-iam-policy-binding "github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --project="${PROJECT_ID}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-actions/attribute.repository/${GITHUB_REPO}"
```

Replace:
- `${PROJECT_ID}` with your GCP project ID
- `${PROJECT_NUMBER}` with your GCP project number
- `${GITHUB_REPO}` with your GitHub repository (e.g., "username/repo-name") 