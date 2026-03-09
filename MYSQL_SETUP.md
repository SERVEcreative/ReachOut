# Set Up a New MySQL Server for ReachOut

Follow these steps to use MySQL instead of SQLite.

---

## Step 1: Log in to MySQL

Open a terminal and log in as the **root** user (or another admin account):

**Windows (Command Prompt or PowerShell):**
```bash
mysql -u root -p
```
Enter your MySQL root password when prompted.

**If MySQL is not in your PATH**, use the full path, for example:
```bash
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p
```

---

## Step 2: Create the database and user

**Option A – Run the SQL script**

From the project folder:
```bash
mysql -u root -p < setup_mysql.sql
```

Before running, **edit `setup_mysql.sql`** and replace `your_password` with a strong password for the `emailapp` user.

**Option B – Run commands manually**

In the MySQL shell (`mysql -u root -p`), run:

```sql
CREATE DATABASE IF NOT EXISTS email_sender
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'emailapp'@'localhost' IDENTIFIED BY 'YourStrongPassword123';

GRANT ALL PRIVILEGES ON email_sender.* TO 'emailapp'@'localhost';

FLUSH PRIVILEGES;

EXIT;
```

Replace `YourStrongPassword123` with your own password. The provided `setup_mysql.sql` uses `EmailApp@123` for easy testing—use the same in `.env` as `MYSQL_PASSWORD`.

---

## Step 3: Configure the app (.env)

In your project folder, create or edit `.env` and add:

```env
SECRET_KEY=your-long-random-secret-key-here

# MySQL (use the same password you set in Step 2)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=emailapp
MYSQL_PASSWORD=EmailApp@123
MYSQL_DATABASE=email_sender
```

- If you ran `setup_mysql.sql` as provided, the password is **EmailApp@123**. Otherwise use the password you set in Step 2.
- If MySQL is on another machine, set `MYSQL_HOST` to that machine’s IP or hostname.

---

## Step 4: Install driver and run the app

```bash
pip install PyMySQL
python app.py
```

On first run, the app will create the **users** and **user_settings** tables inside the `email_sender` database.

**Optional – test user:** To log in without signing up, run once:
```bash
python seed_test_user.py
```
Then log in at http://localhost:5000 with **rahul.nitjsr67@gmail.com** / **Test@123**.

---

## Troubleshooting

| Problem | What to do |
|--------|------------|
| `Access denied for user 'emailapp'@'localhost'` | Check `MYSQL_PASSWORD` in `.env` matches the password you set for `emailapp`. Run `FLUSH PRIVILEGES;` as root after creating the user. |
| `Can't connect to MySQL server` | Ensure MySQL service is running. On Windows: Services → MySQL; or `net start MySQL80` (name may vary). |
| `Unknown database 'email_sender'` | Run the `CREATE DATABASE email_sender;` command as root (Step 2). |
| App still uses SQLite | Make sure `.env` has `MYSQL_HOST=localhost` (or another host). The app uses MySQL only when `DATABASE_URL` starts with `mysql` or `MYSQL_HOST` is set. |

---

## Tables created by the app

The app creates these in the `email_sender` database (you do **not** create them by hand):

- **users** – id, email, password_hash, created_at  
- **user_settings** – user_id, sender_email, app_password_encrypted, your_name, total_experience, technology, experience_from_date, resume_path, updated_at  
