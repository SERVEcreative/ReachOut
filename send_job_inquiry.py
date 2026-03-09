#!/usr/bin/env python3
"""
ReachOut – Send a job inquiry email with resume attachment.
Usage: python send_job_inquiry.py <recipient_email>
   or: python send_job_inquiry.py  (will prompt for email)
"""

import argparse
import os
import smtplib
import sys
import tempfile
from pathlib import Path

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Load .env only from same folder as this script (not from user home etc.)
try:
    from dotenv import load_dotenv
    _env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    load_dotenv(_env_path)
except ImportError:
    pass


def is_google_drive_url(path: str) -> bool:
    """Return True if path is a Google Drive file URL."""
    return path.startswith(("http://", "https://")) and "drive.google.com" in path


def download_resume_from_drive(url: str) -> tuple[str, str] | None:
    """
    Download file from Google Drive URL. Returns (local_path, attachment_filename) or None on failure.
    """
    try:
        import gdown
    except ImportError:
        print("Error: Install gdown for Google Drive support: pip install gdown")
        return None

    out_path = os.path.join(tempfile.gettempdir(), "email_sender_resume.pdf")
    try:
        gdown.download(url=url, output=out_path, quiet=False, fuzzy=True)
        if os.path.isfile(out_path) and os.path.getsize(out_path) > 0:
            return (out_path, "resume.pdf")
        if os.path.isfile(out_path):
            os.remove(out_path)
    except Exception as e:
        print(f"Error downloading from Google Drive: {e}")
    return None


def get_config():
    """Load configuration from environment variables. Returns None if credentials missing."""
    sender_email = os.getenv("SENDER_EMAIL")
    app_password = os.getenv("APP_PASSWORD")
    your_name = os.getenv("YOUR_NAME", "Candidate")
    resume_path = os.getenv("RESUME_PATH", "").strip()
    experience = os.getenv("EXPERIENCE", "").strip() or None
    custom_message = (os.getenv("CUSTOM_MESSAGE") or "").strip()
    total_experience = (os.getenv("TOTAL_EXPERIENCE") or "").strip() or None
    technology = (os.getenv("TECHNOLOGY") or "").strip() or None
    experience_from_date = (os.getenv("EXPERIENCE_FROM_DATE") or "").strip() or None

    if not sender_email or not app_password:
        return None

    return {
        "sender_email": sender_email,
        "app_password": app_password,
        "your_name": your_name,
        "resume_path": resume_path or None,
        "experience": experience,
        "custom_message": custom_message or None,
        "total_experience": total_experience,
        "technology": technology,
        "experience_from_date": experience_from_date,
    }


def build_email_body(
    your_name: str,
    experience: str | None = None,
    custom_message: str | None = None,
    total_experience: str | None = None,
    technology: str | None = None,
    experience_from_date: str | None = None,
) -> str:
    """Build email body from candidate experience (setup) or custom_message override."""
    if custom_message:
        return custom_message.rstrip() + "\n\nBest regards,\n" + your_name

    # Build experience line from one-time setup fields (total experience, technology, from date)
    experience_line = ""
    if total_experience and technology and experience_from_date:
        experience_line = (
            f"\nI have {total_experience} of experience in {technology}, since {experience_from_date}. "
            "I am keen to contribute to your team and would appreciate the chance to discuss how my skills might be a good fit.\n"
        )
    elif total_experience and technology:
        experience_line = (
            f"\nI have {total_experience} of experience in {technology} and would be glad to contribute where relevant.\n"
        )
    elif experience:
        experience_line = f"\nI have {experience} and would be glad to contribute where relevant.\n"

    return f"""Hello,

I hope this email finds you well.

I am writing to inquire about any available positions at your organization. I am interested in learning about current opportunities.{experience_line}

I have attached my resume for your review. I would be grateful for the opportunity to connect with you or the right person at your convenience.

Thank you for your time and consideration.

Best regards,
{your_name}
"""


def create_message(
    sender_email: str,
    recipient_email: str,
    your_name: str,
    resume_path: str | None,
    attachment_filename: str | None = None,
    experience: str | None = None,
    custom_message: str | None = None,
    total_experience: str | None = None,
    technology: str | None = None,
    experience_from_date: str | None = None,
) -> MIMEMultipart:
    """Create the email message with optional resume attachment."""
    msg = MIMEMultipart()
    msg["From"] = f"{your_name} <{sender_email}>"
    msg["To"] = recipient_email
    msg["Subject"] = "Inquiry About Available Positions – Resume Attached"

    body = build_email_body(
        your_name,
        experience,
        custom_message,
        total_experience,
        technology,
        experience_from_date,
    )
    msg.attach(MIMEText(body, "plain"))

    if resume_path and os.path.isfile(resume_path):
        with open(resume_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        filename = attachment_filename or os.path.basename(resume_path)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        msg.attach(part)

    return msg


def send_email(
    sender_email: str,
    app_password: str,
    recipient_email: str,
    msg: MIMEMultipart,
) -> None:
    """Send email via Gmail SMTP."""
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())


def send_inquiry_to(recipient_email: str, config: dict | None = None) -> dict:
    """
    Send job inquiry email to the given recipient (ReachOut web app or CLI).
    If config is provided (multi-user), use it; else use get_config() (single-user .env).
    Returns {"success": True} or {"success": False, "error": "message"}.
    """
    recipient_email = (recipient_email or "").strip()
    if not recipient_email or "@" not in recipient_email:
        return {"success": False, "error": "Please provide a valid email address."}

    if config is None:
        config = get_config()
    if not config:
        return {"success": False, "error": "Email not configured. Set SENDER_EMAIL and APP_PASSWORD in .env."}

    resume_path = config["resume_path"]
    attachment_filename = None

    if resume_path and is_google_drive_url(resume_path):
        result = download_resume_from_drive(resume_path)
        if result:
            resume_path, attachment_filename = result
        else:
            resume_path = None
    elif not resume_path:
        default_resume = Path(__file__).parent / "resume.pdf"
        if default_resume.exists():
            resume_path = str(default_resume)

    msg = create_message(
        config["sender_email"],
        recipient_email,
        config["your_name"],
        resume_path,
        attachment_filename=attachment_filename,
        experience=config["experience"],
        custom_message=config.get("custom_message"),
        total_experience=config.get("total_experience"),
        technology=config.get("technology"),
        experience_from_date=config.get("experience_from_date"),
    )

    try:
        send_email(
            config["sender_email"],
            config["app_password"],
            recipient_email,
            msg,
        )
        if resume_path and "email_sender_resume.pdf" in resume_path and os.path.isfile(resume_path):
            try:
                os.remove(resume_path)
            except OSError:
                pass
        return {"success": True}
    except smtplib.SMTPAuthenticationError:
        return {"success": False, "error": "Gmail authentication failed. Use an App Password, not your normal password."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="ReachOut – Send a job inquiry email with optional resume attachment."
    )
    parser.add_argument(
        "email",
        nargs="?",
        help="Recipient email address (e.g. hr@company.com)",
    )
    args = parser.parse_args()

    recipient = args.email or input("Enter recipient email address: ").strip()
    if not recipient or "@" not in recipient:
        print("Error: Please provide a valid email address.")
        sys.exit(1)

    result = send_inquiry_to(recipient)
    if result.get("success"):
        print("Email sent successfully.")
    else:
        print("Error:", result.get("error", "Failed to send email."))
        sys.exit(1)


if __name__ == "__main__":
    main()
