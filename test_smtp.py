import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def test_smtp():
    server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", 587))
    user = os.getenv("SMTP_USER")
    pw = os.getenv("SMTP_PASSWORD")
    
    print(f"DEBUG: Attempting connection to {server}:{port}")
    print(f"DEBUG: User: {user}")
    
    if not user or not pw:
        print("ERROR: SMTP_USER or SMTP_PASSWORD missing from .env")
        return

    msg = MIMEText("This is a test email from CryptoShield setup.")
    msg['Subject'] = "CryptoShield SMTP Test"
    msg['From'] = user
    msg['To'] = user # Send to yourself

    try:
        print("Connecting to server...")
        if port == 465:
            with smtplib.SMTP_SSL(server, port, timeout=10) as s:
                print("Logging in...")
                s.login(user, pw)
                print("Sending test mail...")
                s.send_message(msg)
        else:
            with smtplib.SMTP(server, port, timeout=10) as s:
                s.starttls()
                print("Logging in...")
                s.login(user, pw)
                print("Sending test mail...")
                s.send_message(msg)
        print("SUCCESS: Email sent successfully!")
    except Exception as e:
        print(f"FAILED: {str(e)}")

if __name__ == "__main__":
    test_smtp()
