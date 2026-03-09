-- Run this as a MySQL admin (e.g. root) to set up the database for ReachOut.
-- Usage: mysql -u root -p < setup_mysql.sql
-- Or open MySQL Workbench / shell and paste these commands.

-- Create the database
CREATE DATABASE IF NOT EXISTS email_sender
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Create a dedicated user (password for testing; change in production)
CREATE USER IF NOT EXISTS 'emailapp'@'localhost' IDENTIFIED BY 'EmailApp@123';

-- Grant full access to the email_sender database
GRANT ALL PRIVILEGES ON email_sender.* TO 'emailapp'@'localhost';

-- If your app runs on another machine, use '%' instead of 'localhost':
-- CREATE USER IF NOT EXISTS 'emailapp'@'%' IDENTIFIED BY 'your_password';
-- GRANT ALL PRIVILEGES ON email_sender.* TO 'emailapp'@'%';

FLUSH PRIVILEGES;

-- Optional: verify
-- SELECT user, host FROM mysql.user WHERE user = 'emailapp';
-- SHOW DATABASES LIKE 'email_sender';
