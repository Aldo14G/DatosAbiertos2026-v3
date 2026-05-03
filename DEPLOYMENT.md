# Deployment Guide — Datos Abiertos NL 2026

Production deployment of the dashboard (Streamlit) and the marketing landing
page (Next.js) onto Firebase + Cloud Run.

---

## Architecture overview

```
                     ┌──────────────────────────────────┐
                     │  Firebase Hosting / App Hosting  │
                     │  (catalogo-nl.web.app)           │
   user ─────────────►  ↳ Next.js landing (static)      │
                     └────────────┬─────────────────────┘
                                  │  rewrite: /dashboard/**
                                  ▼
                     ┌──────────────────────────────────┐
                     │  Google Cloud Run                │
                     │  (dashboard-xxx-uc.a.run.app)    │
                     │  ↳ Streamlit + Python pipeline   │
                     └──────────────────────────────────┘
```

**Why two services?**
Firebase Hosting only serves static assets. Streamlit needs a Python runtime →
Cloud Run is the integrated path. Firebase Hosting routes a path (e.g.
`/dashboard`) to Cloud Run, giving you a single domain with HTTPS for free.

---

## Prerequisites

- **Google Cloud account** with billing enabled (Cloud Run free tier covers
  small projects).
- **Firebase CLI**: `npm install -g firebase-tools`
- **gcloud CLI**: see <https://cloud.google.com/sdk/docs/install>
- **Docker** (only if you want to test the image locally; not required for
  source-based deploy).
- **Node.js 20+** for the landing build.

Authenticate once:

```bash
gcloud auth login
gcloud auth application-default login
firebase login
```

---

## 1) Deploy the dashboard (Cloud Run)

### 1.1 — One-time project setup

```bash
# Create or select a GCP project (also acts as Firebase project)
gcloud projects create catalogo-nl-2026 --name="Catálogo NL 2026"
gcloud config set project catalogo-nl-2026

# Enable APIs
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com
```

### 1.2 — Push secrets to Secret Manager (DO NOT use .env in production)

```bash
# Example: store the Anthropic API key
echo -n "sk-ant-..." | gcloud secrets create anthropic-api-key --data-file=-

# Grant Cloud Run access (replace PROJECT_NUMBER)
gcloud secrets add-iam-policy-binding anthropic-api-key \
    --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### 1.3 — Deploy from source

```bash
gcloud run deploy catalogo-nl-dashboard \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 5 \
    --timeout 60s \
    --set-env-vars "APP_ENV=production,LOG_LEVEL=INFO" \
    --set-secrets "ANTHROPIC_API_KEY=anthropic-api-key:latest"
```

> **Cost note:** with `min-instances 0` (default), Cloud Run scales to zero
> when idle. Monthly cost for low traffic is typically < $5 USD. Set
> `--max-instances` to cap your bill ceiling.

### 1.4 — Verify

```bash
gcloud run services describe catalogo-nl-dashboard --region us-central1 \
    --format='value(status.url)'
# → https://catalogo-nl-dashboard-xxxxxx-uc.a.run.app
```

Open the URL. The dashboard should load. If it doesn't, check logs:

```bash
gcloud run logs tail catalogo-nl-dashboard --region us-central1
```

---

## 2) Deploy the landing (Firebase App Hosting)

### 2.1 — Initialize

```bash
cd landing
firebase init apphosting     # link to the same project: catalogo-nl-2026
```

### 2.2 — Configure environment

In `landing/.env.production` (NOT committed), set:

```
NEXT_PUBLIC_DASHBOARD_URL=https://catalogo-nl-dashboard-xxxxxx-uc.a.run.app
```

### 2.3 — Deploy

```bash
firebase deploy --only apphosting
```

App Hosting auto-detects Next.js, builds, and serves it. You'll get a URL like
`https://catalogo-nl-2026.web.app`.

---

## 3) Custom domain + Cloud Run rewrite (optional but recommended)

Routes `https://catalogo-nl.gob.mx/dashboard` → your Cloud Run service, so the
user only ever sees one domain.

`landing/firebase.json`:

```json
{
  "hosting": {
    "rewrites": [
      {
        "source": "/dashboard/**",
        "run": {
          "serviceId": "catalogo-nl-dashboard",
          "region": "us-central1"
        }
      }
    ]
  }
}
```

Then `firebase deploy --only hosting`.

To attach a custom domain:
1. Firebase Console → Hosting → "Add custom domain".
2. Add the DNS records they provide (TXT for verification, A/AAAA for traffic).
3. Wait for SSL provisioning (~15 min).

---

## 4) Continuous deployment (GitHub Actions)

Recommended workflow at `.github/workflows/deploy.yml`:

```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  dashboard:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write          # for keyless auth via Workload Identity
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.DEPLOY_SA }}
      - uses: google-github-actions/setup-gcloud@v2
      - run: |
          gcloud run deploy catalogo-nl-dashboard \
            --source . --region us-central1 \
            --quiet
```

> **Don't store JSON keys in GitHub secrets.** Use Workload Identity Federation
> instead — it's keyless and rotates automatically. See
> <https://github.com/google-github-actions/auth#setup>.

---

## Rollback

```bash
# List revisions
gcloud run revisions list --service catalogo-nl-dashboard --region us-central1

# Roll traffic back to a previous revision
gcloud run services update-traffic catalogo-nl-dashboard \
    --region us-central1 \
    --to-revisions catalogo-nl-dashboard-00012-abc=100
```

---

## Local Docker test (optional)

```bash
docker build -t catalogo-nl:local .
docker run --rm -p 8080:8080 \
    -e APP_ENV=development \
    catalogo-nl:local
# → http://localhost:8080
```

---

## Alternative: Streamlit Community Cloud (free, faster to set up)

If budget = $0 and the repository can be public:

1. Push to GitHub.
2. Sign in at <https://streamlit.io/cloud>.
3. "New app" → pick repo, branch, `dashboard_v3.py`.
4. Add secrets in the UI (Anthropic key, etc.).
5. Deploy. Done in ~3 minutes.

Trade-offs: public repo only on the free tier, less control over the runtime,
no integration with Firebase Hosting.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Cold start > 10s | Image too large or missing min-instances | `--min-instances 1` (paid) or trim image |
| 502 Bad Gateway | Streamlit didn't bind to `$PORT` | Verify `Dockerfile` `CMD` uses `${PORT}` |
| `Quality results not found` | Pipeline output not in image | Run pipeline before deploy, ship CSV, or fetch on cold start |
| Hosting → Run rewrite returns 403 | Missing `roles/run.invoker` for Hosting SA | `gcloud run services add-iam-policy-binding` |

---

See [SECURITY.md](SECURITY.md) for the security hardening checklist that MUST
be completed before opening the deployment to public traffic.
