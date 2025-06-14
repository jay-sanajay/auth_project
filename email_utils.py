from email.message import EmailMessage
import aiosmtplib

EMAIL_SENDER = "jaytakalgavankar@gmail.com"
EMAIL_PASSWORD = "psgi kdqa qppj opeu"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

async def send_reset_email(to_email: str, token: str):
    reset_link = f"https://auth-project-2-vlqj.onrender.com/reset-password?token={token}"

    message = EmailMessage()
    message["From"] = EMAIL_SENDER
    message["To"] = to_email
    message["Subject"] = "Password Reset Link"
    message.set_content(f"Click the link to reset your password:\n{reset_link}")

    await aiosmtplib.send(
        message,
        hostname=SMTP_SERVER,
        port=SMTP_PORT,
        start_tls=True,
        username=EMAIL_SENDER,
        password=EMAIL_PASSWORD
    )
