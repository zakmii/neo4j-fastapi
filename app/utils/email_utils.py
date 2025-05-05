import logging

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from app.models.user import (
    UserPublic,  # Assuming UserPublic contains non-sensitive info
)
from app.utils.environment import CONFIG

logger = logging.getLogger(__name__)

conf = ConnectionConfig(
    MAIL_USERNAME=CONFIG.MAIL.USERNAME,
    MAIL_PASSWORD=CONFIG.MAIL.PASSWORD,
    MAIL_FROM=CONFIG.MAIL.FROM,
    MAIL_PORT=CONFIG.MAIL.PORT,
    MAIL_SERVER=CONFIG.MAIL.SERVER,
    MAIL_FROM_NAME=CONFIG.MAIL.FROM_NAME,
    MAIL_STARTTLS=CONFIG.MAIL.STARTTLS,
    MAIL_SSL_TLS=CONFIG.MAIL.SSL_TLS,
    USE_CREDENTIALS=CONFIG.MAIL.USE_CREDENTIALS,
    VALIDATE_CERTS=CONFIG.MAIL.VALIDATE_CERTS,
)

fm = FastMail(conf)


async def send_new_user_notification(user: UserPublic):
    """Sends an email notification to the admin about a new user signup."""
    if not CONFIG.MAIL.ADMIN_EMAIL:
        logger.warning(
            "ADMIN_EMAIL not set in MAIL config. Skipping new user notification."
        )
        return

    subject = "New User Registration"
    body = f"""
    <p>A new user has registered:</p>
    <ul>
        <li>Username: {user.username}</li>
        <li>Email: {user.email}</li>
    </ul>
    """

    message = MessageSchema(
        subject=subject,
        recipients=[CONFIG.MAIL.ADMIN_EMAIL],  # Use nested ADMIN_EMAIL
        body=body,
        subtype="html",
    )

    try:
        await fm.send_message(message)
        logger.info(
            f"New user notification sent to {CONFIG.MAIL.ADMIN_EMAIL} for user {user.username}"
        )
    except Exception as e:
        logger.error(f"Failed to send new user notification email: {e}")
