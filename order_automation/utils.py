import os
from django.conf import settings
from accounts.utils import get_html_content
from accounts.tasks import send_email


def get_template(app_name: str, template_name: str) -> str:
    return os.path.join(
        settings.BASE_DIR, app_name, "templates", app_name, template_name
    )


def notify_critic_stock(admin_product_absolute_url: str):
  template_path = get_template("orders", "notify_critic_product.html")
  email_content = get_html_content(template_path, admin_product_absolute_url=admin_product_absolute_url)
  send_email.delay("Yeni emailinizi tesdiqləyin", os.getenv("ADMIN_EMAIL"), email_content)
