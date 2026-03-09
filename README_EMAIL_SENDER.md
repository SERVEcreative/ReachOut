# ReachOut

Send a professional job-inquiry email with your resume attached. **Multi-user**: each user signs up, logs in, completes one-time setup (name, experience, Gmail, resume), then sends from their own config.

## Project structure

`app.py` (entry) → `config.py`, `routes/` (auth, main, api), `services/`, `templates/`, `static/css/`. Data: `db.py`, `auth_utils.py`. Email: `send_job_inquiry.py`.

**Deploy on Railway:** see [RAILWAY.md](RAILWAY.md).

## Quick start (web app – recommended)

1. **Install dependencies:** `pip install -r requirements.txt`
2. **Run the app:** `python app.py`
3. Open **http://localhost:5000**. If you haven’t configured yet, you’ll see **Setup**: enter your name, Gmail address, [App Password](https://myaccount.google.com/apppasswords), and optionally your experience and resume (Google Drive link or path). Save.
4. On the main page, enter the recipient’s email and click **Send**. Use **Settings** to change your details later.

## Manual setup (.env)

Alternatively, configure via environment variables:

```bash
copy .env.example .env
```

Edit `.env` and set:

| Variable       | Description                                  |
|----------------|----------------------------------------------|
| `SENDER_EMAIL` | Your Gmail address                           |
| `APP_PASSWORD` | The 16-character Gmail App Password          |
| `YOUR_NAME`    | Your full name (used in the email signature) |
| `RESUME_PATH`  | Local path to your resume **or** a Google Drive share link |

You can use either:
- A **local path** (e.g. `C:\Users\You\Documents\resume.pdf` or a path in your Google Drive folder like `G:\My Drive\resume.pdf`).
- A **Google Drive share link** (e.g. `https://drive.google.com/file/d/.../view?usp=drive_link`). The file must be shared so that “Anyone with the link” can view it. The script will download it and attach it as `resume.pdf`.

Example:

```
SENDER_EMAIL=you@gmail.com
APP_PASSWORD=abcd efgh ijkl mnop
YOUR_NAME=Jane Doe
RESUME_PATH=C:\Users\You\Documents\resume.pdf
```

If `RESUME_PATH` is empty, the script looks for `resume.pdf` in the project folder. If that file doesn't exist, the email is sent without an attachment.

## Usage

### Web interface (multi-user)

Start the app with `python app.py`, then open **http://localhost:5000**. **Sign up** with email and password, **log in**, then complete **Setup** once (name, experience, technology, from date, Gmail, App Password, resume link). After that, use the main page to enter a recipient email and **Send**. **Change setup** and **Log out** are in the footer.

### Command line

**With email as argument:**

```bash
python send_job_inquiry.py hr@company.com
```

**Interactive (script will ask for email):**

```bash
python send_job_inquiry.py
```

The email subject is: **"Inquiry About Available Positions – Resume Attached"**, and the body asks about open roles and mentions the attached resume.

## Security

- Never commit `.env` (it's in `.gitignore`). Only commit `.env.example` as a template.
- Keep your App Password private and rotate it if you think it was exposed.

## Deploying for many users

The current app is single-user (one `.env`, one Gmail). To run it for **many or millions of users**, you need user accounts, a database, and a different way to store each user’s config and send limits. See **[DEPLOYMENT.md](DEPLOYMENT.md)** for architecture options, scaling, and migration steps.
