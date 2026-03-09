# Deploy ReachOut on Railway

Follow these steps to run ReachOut on [Railway](https://railway.app) with MySQL.

---

## 1. Prerequisites

- A [Railway](https://railway.app) account (GitHub login).
- Your project in a **GitHub** repo (Railway deploys from Git).

---

## 2. Create a new project on Railway

1. Go to [railway.app](https://railway.app) and log in.
2. Click **New Project**.
3. Choose **Deploy from GitHub repo**.
4. Select your **Email_sender** (or ReachOut) repository.
5. Railway will detect the app and add a **service** for it.

---

## 3. Add MySQL

1. In the same project, click **+ New** → **Database** → **Add MySQL**.
2. Wait for MySQL to be provisioned.
3. Click the **MySQL** service → **Variables** (or **Connect**). You’ll see something like **MYSQL_URL** or **DATABASE_URL**.
4. Click your **web service** (the app), then go to **Variables**.
5. Click **+ New Variable** and add:

   | Variable       | Value / source |
   |----------------|----------------|
   | `MYSQL_URL`    | Copy from the MySQL service (e.g. **Connect** → **Variable reference** and reference `MYSQL_URL` from the MySQL service, or paste the URL). |
   | `SECRET_KEY`   | A long random string (e.g. run `python -c "import secrets; print(secrets.token_hex(32))"` and paste the result). |

   If Railway gives you **DATABASE_URL** from the MySQL service, use that instead of **MYSQL_URL** (the app supports both).

6. **Link the MySQL service to the app** (if not already):
   - In the app service → **Variables** → **+ New Variable** → **Reference**.
   - Choose the MySQL service and add **MYSQL_URL** (or **DATABASE_URL**) so the app gets the connection string automatically.

---

## 4. Configure the web service

1. Open your **web/service** (the one that runs the repo).
2. Go to **Settings**.
3. Under **Build**:
   - **Build Command**: leave empty (Railway will run `pip install -r requirements.txt`).
   - **Root Directory**: leave empty unless the app is in a subfolder.
4. Under **Deploy**:
   - **Start Command**: leave empty so Railway uses the **Procfile** (`web: gunicorn --bind 0.0.0.0:$PORT app:app`).  
   - If you don’t use a Procfile, set **Start Command** to:
     ```bash
     gunicorn --bind 0.0.0.0:$PORT app:app
     ```
5. Under **Networking**:
   - Click **Generate Domain** so Railway gives you a public URL (e.g. `yourapp.up.railway.app`).

---

## 5. Deploy

1. Push your code to GitHub (if you haven’t already). Railway will build and deploy.
2. After the build finishes, open the **generated domain** (e.g. from the **Settings** → **Networking** section).
3. You should see the **ReachOut** login page. Sign up, complete setup, and send an inquiry.

---

## 6. Environment variables summary

| Variable      | Required | Description |
|---------------|----------|-------------|
| `SECRET_KEY`  | Yes      | Long random string for sessions and encryption. Generate with `python -c "import secrets; print(secrets.token_hex(32))"`. **Must not be the default in production.** |
| `MYSQL_URL` or `DATABASE_URL` | Yes (for MySQL) | MySQL connection URL from Railway’s MySQL service. The app uses this when you add the MySQL service and reference this variable. |
| `FLASK_ENV`   | No      | Set to `production` on Railway so the app enables secure cookies and session expiry (optional; app also detects production when `PORT` is set). |

You do **not** need to set `PORT`; Railway sets it automatically.

---

## 6b. Production behavior (automatic on Railway)

When the app runs in production (e.g. `PORT` is set or `FLASK_ENV=production`), it automatically:

- **Secure session cookies** – `Secure`, `HttpOnly`, `SameSite=Lax` so cookies are only sent over HTTPS and not to other sites.
- **Session lifetime** – Logged-in sessions expire after 7 days.
- **Security headers** – `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `X-XSS-Protection: 1; mode=block` on all responses.
- **Gunicorn** – Runs with 2 workers and 120s timeout (see Procfile).

---

## 7. Troubleshooting

| Issue | What to do |
|-------|------------|
| Build fails | Check **Deploy logs**. Ensure `requirements.txt` includes `gunicorn` and the repo has a **Procfile** (e.g. `web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app`). |
| “Application failed to respond” | Confirm the start command uses `$PORT` (e.g. Gunicorn bound to `0.0.0.0:$PORT`). |
| Database / login errors | Ensure the app service has **MYSQL_URL** or **DATABASE_URL** from the MySQL service (variable reference or copy-paste). Tables are created on first request (init_db runs at startup). |
| 502 Bad Gateway | Wait 1–2 minutes after deploy; cold start can be slow. If it persists, check **Deploy logs** for Python or Gunicorn errors. |

---

## 8. Optional: use SQLite on Railway

Railway’s filesystem is **ephemeral** (resets on redeploy), so SQLite is not recommended for production. For a quick test without MySQL you can:

1. Omit adding MySQL and don’t set `MYSQL_URL` / `DATABASE_URL`.
2. The app will use SQLite (`app.db`). Data will be lost on redeploy.

For real multi-user use, keep **MySQL** (or another persistent DB) and the variables above.
