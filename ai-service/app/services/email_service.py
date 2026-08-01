import smtplib
from email.message import EmailMessage
from app.core.config import settings

def send_verification_email(to_email: str, otp: str):
    """
    Sends an OTP verification email using Python's built-in smtplib.
    This replaces the mock console print with real email functionality.
    """
    # If the user hasn't configured SMTP, fallback to console (useful for dev)
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print(f"\n[WARNING] SMTP credentials not set in .env")
        print(f"[MOCK EMAIL] To: {to_email} | OTP: {otp}\n")
        return

    msg = EmailMessage()
    msg['Subject'] = 'Your AI SQL Verification Code'
    msg['From'] = settings.SMTP_USER
    msg['To'] = to_email
    
    # HTML Email Body
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Welcome to AI SQL!</h2>
        <p>Please use the following One-Time Password (OTP) to verify your email address:</p>
        <h3 style="background-color: #f4f4f4; padding: 10px; display: inline-block; border-radius: 5px;">{otp}</h3>
        <p>This code will expire in 10 minutes.</p>
        <p>If you did not request this, please ignore this email.</p>
      </body>
    </html>
    """
    msg.set_content("Your OTP is: " + otp) # Fallback plain text
    msg.add_alternative(html_content, subtype='html')

    try:
        # Connect to the SMTP server (e.g., smtp.gmail.com:587)
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls() # Secure the connection
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        print(f"[INFO] Verification email sent successfully to {to_email}")
    except Exception as e:
        print(f"[ERROR] Failed to send email to {to_email}: {str(e)}")
        # We don't raise an HTTPException here because we don't want to break 
        # the entire signup flow just because the email failed to send.
