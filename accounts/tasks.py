from django.core.mail import EmailMessage
from order_automation.settings import EMAIL_HOST_USER
from celery import shared_task
import logging

LOGGER = logging.getLogger(__name__)


@shared_task
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
