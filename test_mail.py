import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Try to load environment variables
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

print(f"--- SMTP Diagnostic ---")
print(f"Server: {SMTP_SERVER}")
print(f"Port: {SMTP_PORT}")
print(f"User: {SMTP_USER}")
print(f"Password starts with: {SMTP_PASSWORD[:2] if SMTP_PASSWORD else 'None'}...")

if not SMTP_USER or not SMTP_PASSWORD:
    print("ERROR: SMTP_USER or SMTP_PASSWORD is not set in .env")
    exit(1)

msg = MIMEText("This is a test email from the CryptoShield diagnostic script.")
msg['Subject'] = "CryptoShield SMTP Test"
msg['From'] = SMTP_USER
msg['To'] = SMTP_USER  # Send to self

try:
    print("\nAttempting to connect to SMTP server...")
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.set_debuglevel(1)  # Enable detailed output
        print("Connected. Starting TLS...")
        server.starttls()
        print("TLS started. Attempting login...")
        server.login(SMTP_USER, SMTP_PASSWORD)
        print("Login successful! Sending test email...")
        server.send_message(msg)
        print("Email sent successfully!")
except Exception as e:
    print(f"\nCRITICAL ERROR: {str(e)}")
    print("\nTroubleshooting Tips:")
    print("1. Ensure your App Password is 16 characters (no spaces).")
    print("2. Check if your ISP or firewall blocks port 587.")
    print("3. Ensure 'Less secure app access' is NOT used; App Passwords are required for 2FA accounts.")
    print("4. Double check that SMTP_USER is your full Gmail address.")
