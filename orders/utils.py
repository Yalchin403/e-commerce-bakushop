from order_automation.settings import EMAIL_HOST_USER
import os
from django.core.mail import EmailMessage
import logging


LOGGER = logging.getLogger(__name__)


def send_email_to_admin(name, surname, email, phone_number, order_url, notes):
    try:
        email_body = f"""
        	<h1>{name} {surname} terefinden yeni sifaris var</h1>

        	<ul>
        	<li>Email: {email}</li>
        	<li>Telefon: {phone_number}</li>
        	<li>Məhsulun Linki: {order_url}</li>
        	<li>Əlavə qeydlər: {notes}</li>
        	<ul>
        	"""
        reciever_email = os.getenv("RECIEVER_EMAIL")

        msg = EmailMessage(
            "Yeni Sifaris", email_body, EMAIL_HOST_USER, [reciever_email]
        )
        msg.content_subtype = "html"
        msg.send()

    except Exception as err:
        LOGGER(f"Couldn't send the email, {err}")


def send_status_update_to_user(name, email, status, order_url, notes):
    try:
        email_body = f"""
            <h1>Hörmətli, {name} sifarişinizin statusu '{status}' statusuna dəyişdirildi.</h1>

            <ul>
            <li>Məhsulun Linki: {order_url}</li>
            <li>Əlavə etdiyiniz qeydlər: {notes}</li>
            <ul>
            """

        msg = EmailMessage("Yeni Sifaris", email_body, EMAIL_HOST_USER, [email])
        msg.content_subtype = "html"
        msg.send()

    except Exception as err:
        LOGGER(f"Couldn't send the email, {err}")
