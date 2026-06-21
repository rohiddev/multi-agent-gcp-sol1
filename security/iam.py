"""
IAM and identity patterns for enterprise agent deployment.

Production checklist:
  1. Each agent gets its own service account with minimum required permissions.
  2. Use Workload Identity Federation — no long-lived service account keys.
  3. Enable VPC Service Controls perimeter around Vertex AI + Agent Platform.
  4. Apply CMEK to corpora, indexes, and storage buckets.
  5. All agent-to-API calls use short-lived tokens via Application Default Credentials.

References:
  - cloud.google.com/iam/docs/workload-identity-federation
  - cloud.google.com/vpc-service-controls/docs/overview
  - cloud.google.com/kms/docs/cmek
"""

import google.auth
import google.auth.transport.requests


def get_credentials():
    """Returns Application Default Credentials for the running environment.

    In production: uses the service account attached to the Cloud Run / GKE workload.
    In development: uses gcloud auth application-default login.
    """
    credentials, project = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    return credentials, project


def get_access_token() -> str:
    """Returns a short-lived access token for authenticated API calls."""
    credentials, _ = get_credentials()
    credentials.refresh(google.auth.transport.requests.Request())
    return credentials.token
