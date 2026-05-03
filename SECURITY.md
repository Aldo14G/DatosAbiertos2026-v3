# Security Policy & Hardening Checklist

This document is the source of truth for the security posture of Datos
Abiertos NL 2026. Every deployment to production must pass the checklist
below.

---

## Reporting a vulnerability

If you discover a security issue, **do not** open a public GitHub issue.
Email the maintainer at the address listed in the GitHub repository profile,
with subject `[SECURITY] <short title>`. We aim to respond within 72 hours.

---

## Threat model (what we defend against)

| Threat | Severity | Mitigation |
|---|---|---|
| Stolen API keys / service-account JSONs | Critical | Secret Manager + WIF; never in git |
| Account takeover (Google, Firebase, GitHub) | Critical | 2FA mandatory on every account |
| SSRF via CKAN fetcher | High | URL allow-list in `pipeline/fetcher.py` |
| XSS in dashboard HTML blocks | High | `html.escape` on all user/CKAN strings |
| Supply-chain (malicious pip dep) | Medium | Pinned versions, Dependabot, hash-checking |
| DDoS / cost abuse | Medium | Cloud Run `--max-instances`, GCP budget alert |
| Sensitive data leak via logs | Medium | Structured logging, no PII printed |
| Cross-site request forgery | Low | Streamlit `enableXsrfProtection=true` |

---

## Pre-deployment checklist

Run through every item before flipping public traffic on. Do not skip; each
one has caused real-world breaches at other organizations.

### A — Account hygiene

- [ ] **2FA enabled** on Google, Firebase, GitHub, npm, Anthropic console
- [ ] **No personal account** is used for production deploys — create a
      dedicated GCP service account with the minimum roles:
      `roles/run.developer`, `roles/secretmanager.secretAccessor`
- [ ] **Workload Identity Federation** configured for GitHub Actions
      (no JSON keys in GitHub secrets)
- [ ] Repository **collaborator list reviewed** — remove ex-contributors
- [ ] **GitHub branch protection** on `main`: require PR review, require
      status checks (ruff, pytest), no force-push

### B — Secret management

- [ ] No `.env`, `*-credentials*.json`, or `*service-account*.json` in
      git history. Verify with:
      ```bash
      git log --all --full-history -- .env *credentials*
      ```
      If anything is found: **rotate the leaked credential** (don't just
      delete the file — git history will preserve it).
- [ ] All production secrets stored in **Google Secret Manager**, not env
      files on disk
- [ ] `.gitignore` includes the patterns from this repo's
      [`.gitignore`](.gitignore) (verified)
- [ ] `.dockerignore` strips secrets before build (verified)
- [ ] Rotate API keys every **90 days** (calendar reminder)

### C — Application defenses

- [ ] **HTTPS only** — Cloud Run + Firebase Hosting handle this by default;
      verify no HTTP redirects are missing
- [ ] **Streamlit XSRF protection enabled**
      (`STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true` in `Dockerfile`)
- [ ] **CORS restricted** — `STREAMLIT_SERVER_ENABLE_CORS=false` unless a
      proxy is in front; set explicit allow-list otherwise
- [ ] **CSP header** added via Cloud Run / Hosting config (block inline
      `<script>` from non-self origins)
- [ ] **Rate limiting** at Cloud Run level (`--concurrency` capped) +
      Cloud Armor rule for per-IP throttling if exposed publicly
- [ ] **`html.escape`** applied to every CKAN-sourced string before
      rendering in `unsafe_allow_html=True` blocks
- [ ] **SSRF protection** in `pipeline/fetcher.py` is active and the
      allow-list contains only `catalogodatos.nl.gob.mx`

### D — Dependencies (supply chain)

- [ ] `requirements.txt` uses **pinned versions** (`pandas==2.2.3`,
      not `pandas>=2.0`)
- [ ] **Dependabot** enabled in GitHub settings → security alerts
- [ ] **`pip-audit`** runs in CI:
      ```bash
      pip install pip-audit && pip-audit -r requirements.txt
      ```
- [ ] Lock file (`requirements-lock.txt` via `pip-compile`) committed to
      catch transitive dependency drift

### E — Data handling

- [ ] CKAN data is **public by definition**, but verify nothing in
      pipeline outputs leaks PII or internal-only fields
- [ ] **Structured logging** (`logging` module, JSON in production); no
      `print()` in code paths reachable by users
- [ ] No PII in URLs, error messages, or telemetry
- [ ] Streamlit `usage_stats` disabled
      (`STREAMLIT_BROWSER_GATHER_USAGE_STATS=false` set in `Dockerfile`)

### F — Cost & abuse controls

- [ ] **GCP budget alert** at $X/month (start with $20)
      → if traffic spikes 10×, you'll know before the bill arrives
- [ ] Cloud Run `--max-instances` ≤ 5 for first 30 days; raise after
      traffic patterns are known
- [ ] Cloud Run `--timeout=60s` (kills runaway requests)
- [ ] **Uptime check** every 5 minutes, alert email configured

### G — Monitoring & response

- [ ] **Cloud Logging** retention set to ≥ 30 days
- [ ] **Error reporting** integration enabled (Sentry optional)
- [ ] **Audit logs** for IAM changes enabled in GCP
- [ ] Runbook documented: who responds if dashboard goes down at 3am

---

## Post-deployment verification

Run within **24 hours** of going live:

1. **External vulnerability scan**
   ```bash
   nmap -sV --script vuln <your-cloud-run-url>
   ```
2. **Headers audit**
   ```bash
   curl -I https://your-domain | grep -iE "strict-transport|x-frame|content-security"
   ```
   Expect: `Strict-Transport-Security`, `X-Frame-Options: DENY`,
   `Content-Security-Policy`.
3. **TLS audit:** test at <https://www.ssllabs.com/ssltest/> — target grade A.
4. **Verify `robots.txt`** matches your access-policy intent (public vs
   indexable).

---

## Incident response

If a credential or service-account leak is suspected:

1. **Rotate immediately** — don't wait for confirmation
   ```bash
   gcloud secrets versions add anthropic-api-key --data-file=-
   ```
2. **Revoke old version**
   ```bash
   gcloud secrets versions destroy <OLD_VERSION> --secret=anthropic-api-key
   ```
3. **Audit access logs** for the time window the leak might have been
   active:
   ```bash
   gcloud logging read 'resource.type="cloud_run_revision"' --limit 100
   ```
4. **Document the incident** in a private postmortem; update this checklist
   if a control was missing.

---

## See also

- [DEPLOYMENT.md](DEPLOYMENT.md) — deployment procedure
- [CLAUDE.md](CLAUDE.md) — non-negotiable repository rules (security
  rules already enforced there: SSRF protection, no inline styles, escape
  user strings)
