# Deploying for Millions of Users

The current app is **single-user**: one `.env` file, one Gmail account, one setup. To serve **millions of users**, you need a different architecture. This guide outlines what changes and how to get there.

---

## Current vs multi-user

| Aspect | Current (single-user) | Multi-user (millions) |
|--------|------------------------|------------------------|
| Config | One `.env` file on server | **Database** per user (profile, encrypted credentials) |
| Identity | None (whoever has the URL) | **Sign up / login** (email + password or OAuth) |
| Sending | Your Gmail only | **Each user’s own Gmail** (or your transactional email service) |
| Resume | One link/path or Drive URL | **Per-user** (upload or link), stored in DB or object storage |
| Scaling | One process, one server | **Stateless app** + load balancer + DB + optional queue |

---

## 1. What you need for scale

### User accounts and data
- **Sign up / login** (e.g. email + password, or Google/GitHub OAuth).
- **Database** (PostgreSQL, MySQL, or managed like RDS, PlanetScale, Supabase) to store:
  - Users (id, email, hashed password, created_at).
  - **Per-user “setup”**: name, total experience, technology, from date, resume URL/link.
  - **Encrypted** Gmail App Passwords (or tokens) — use a secrets manager or encrypt at rest with a key in env.

### Sending email at scale
- **Gmail SMTP limits** (e.g. 500/day for free, 2000/day for Workspace) are **per Gmail account**. With millions of users, each user uses their own Gmail, so you don’t hit one global limit, but each user is still limited by Gmail.
- For **you** sending on behalf of users (e.g. “notifications” or “system” emails), use a **transactional email** provider instead of Gmail:
  - **SendGrid**, **Mailgun**, **AWS SES**, **Postmark**, **Resend**.
- For **job-inquiry emails** (from the candidate’s own address), you have two patterns:
  - **Keep “user’s Gmail”**: each user connects their Gmail (OAuth or App Password); you send via their SMTP. No change to “who” the email is from; you just need to store their credentials securely and scale your app/workers.
  - **Send on behalf (e.g. SendGrid)**: you send from your domain with a “Reply-To” set to the user’s email. Simpler for you, but the “From” is not the user’s Gmail.

### Application layer
- **Stateless app**: no config in local files; everything from DB + env (e.g. `DATABASE_URL`, `SECRET_KEY`, `ENCRYPTION_KEY`).
- **Production WSGI/ASGI server**: e.g. **Gunicorn** (Flask) or **Uvicorn** (FastAPI), behind a reverse proxy (Nginx, Caddy).
- **HTTPS** (TLS) everywhere; **secure cookies** for sessions.

### Scaling the app
- **Horizontal scaling**: run many app instances behind a **load balancer** (e.g. ALB, Nginx).
- **Background jobs**: sending email can be done in a **queue** (Celery + Redis/RabbitMQ, or SQS, or Bull) so the HTTP request returns quickly and workers send in the background.
- **Caching** (e.g. Redis) for sessions and optional rate-limit counters.

### Resume files
- **Option A**: Users paste a **Google Drive (or similar) link**; you store the URL and fetch at send time (as now). No file storage on your side.
- **Option B**: **Upload resume** to object storage (S3, GCS, Cloudflare R2); store the key/URL in the DB; at send time download and attach. Needs quotas and virus scanning in production.

---

## 2. Architecture options

### A. PaaS (fastest to “deployed”)
- **Railway**, **Render**, **Fly.io**, **Heroku**: deploy the same Flask app; add a **Postgres** add-on and **Redis** if you use queues/cache.
- Add **user table** and **setup/settings table**; replace “read from `.env`” with “read from DB for current user”.
- Good for **hundreds to low thousands** of users; then tune DB and add workers/queues.

### B. Containers (Docker + Kubernetes or ECS)
- **Dockerfile** for the app; run with **Gunicorn**.
- **PostgreSQL** (RDS, Cloud SQL, or self-hosted); **Redis** for sessions/queue.
- **Kubernetes** or **AWS ECS** to scale app replicas; load balancer in front.
- Fits **tens of thousands to millions** with proper DB sizing and worker pools.

### C. Serverless (API + workers)
- **API**: AWS Lambda + API Gateway, or Google Cloud Run, or Vercel serverless.
- **DB**: managed Postgres (RDS, Supabase, Neon).
- **Queue**: SQS or Pub/Sub; **Lambda/Cloud Run** workers consume and send email.
- Scales with traffic; you pay per use; cold starts and time limits to consider for “send email” (e.g. 15 min timeout).

---

## 3. Gmail and “millions of users”

- **Each user** can use **their own Gmail** (App Password or OAuth). Your system never sends “from” one shared Gmail for all users; each user is limited by Gmail’s own limits (e.g. 500/day).
- So “millions of users” = millions of *accounts* and *setup profiles*; **sending volume** is spread across those users. Your job is to:
  - Scale **app + DB + queues** to handle signups and requests.
  - Store and use **each user’s credentials** securely (encrypted, least privilege).
- If you later want to send **system emails** (e.g. “Your account was created”) to millions, use **SendGrid/SES/Mailgun**, not Gmail.

---

## 4. High-level migration steps

1. **Add a database**  
   - Create `users` and `user_settings` (or `profiles`) tables.  
   - Move “setup” fields (name, experience, technology, from_date, resume_url, sender_email, encrypted_app_password) into `user_settings` keyed by `user_id`.

2. **Add authentication**  
   - Sign up / login (email + password with hashing, e.g. bcrypt; or OAuth).  
   - Use sessions or JWT; protect `/`, `/setup`, and `/api/send` so only the logged-in user’s data is used.

3. **Remove single `.env` for user data**  
   - App config (e.g. `DATABASE_URL`, `SECRET_KEY`) stays in env.  
   - Per-user config comes from DB; **encrypt** App Passwords (and any tokens) before storing.

4. **Optional: queue for sending**  
   - On “Send”, push a job (e.g. `user_id`, `recipient_email`) to a queue; return 202 Accepted.  
   - Workers load user’s settings from DB, send email (and optionally fetch resume from Drive or S3).  
   - Improves response time and lets you retry and rate-limit per user.

5. **Production checklist**  
   - HTTPS only.  
   - Secure cookies, CSRF, rate limiting (e.g. per user / per IP).  
   - Logging and monitoring (errors, queue depth, send success/failure).  
   - Backups and encryption at rest for DB and secrets.

---

## 5. Quick reference

- **Single server, few users**: keep current design; run with Gunicorn + Nginx + HTTPS.  
- **Hundreds–thousands**: PaaS + Postgres + user table + auth; optional Redis.  
- **Millions**: Stateless app + load balancer + DB (and replicas) + queue + workers; consider serverless or Kubernetes; use transactional email for system emails; keep user-specific sending via their Gmail or future “connect inbox” flow.

If you want, the next step can be a concrete **database schema** and **list of code changes** (e.g. “replace `get_config()` with `get_config_for_user(user_id)`”) for your current Flask app.
