from django.core.mail import EmailMessage
from order_automation.settings import EMAIL_HOST_USER
from django.template.loader import render_to_string
import logging
from email_validator import validate_email, EmailNotValidError


LOGGER = logging.getLogger(__name__)


def send_email(subject, reciever_email, content):
    try:
        msg = EmailMessage(
            subject,
            content,
            EMAIL_HOST_USER,
            [reciever_email],
        )
        msg.content_subtype = "html"
        msg.send()

    except Exception as err:
        LOGGER.error(f"Couldn't send the email, {err}")


def get_html_content(file_path: str, **kwargs):
    html_content = render_to_string(file_path, kwargs)

    return html_content


def is_email(email: str) -> bool:
    try:
        validation = validate_email(email, check_deliverability=True)
        email = validation.email

        return True

    except EmailNotValidError:
        return False
