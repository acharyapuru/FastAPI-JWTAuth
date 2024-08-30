from src.config import setting
from fastapi_mail import MessageSchema, FastMail, ConnectionConfig, MessageType

email_conf = ConnectionConfig(
    MAIL_USERNAME=setting.EMAIL_USERNAME,
    MAIL_PASSWORD=setting.EMAIL_PASSWORD,
    MAIL_FROM=setting.EMAIL_FROM,
    MAIL_PORT=setting.EMAIL_PORT,
    MAIL_SERVER=setting.EMAIL_SERVER,
    MAIL_STARTTLS=setting.EMAIL_TLS,
    MAIL_SSL_TLS=setting.EMAIL_SSL,
)

async def send_email(receiver: str, reset_token: str):
    link = f"{setting.APP_HOST}/{setting.RESET_PASSWORD_URL}/{reset_token}"
    msg_body = f"Click this link to reset your password:\n {link}"
    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[receiver],
        body= msg_body,
        subtype=MessageType.plain
    )

    fm = FastMail(email_conf)
    await fm.send_message(message)
    return {"message":"Email has been sent"}
