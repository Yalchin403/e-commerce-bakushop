from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.dispatch import receiver
from django.urls import reverse
from django.conf import settings
import pyotp
import os
from .tasks import send_email
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import get_html_content
from datetime import datetime
import jwt
from order_automation.utils import get_template


class MyAccountManager(BaseUserManager):
    def create_user(self, username, email, password):
        if not email:
            raise ValueError("User must have an email address")

        if not username:
            raise ValueError("User must have an username")

        if not password:
            raise ValueError("User must have a password")

        user = self.model(
            email=self.normalize_email(email.lower()),
            username=username,
        )

        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_superuser(self, username, email, password):
        if not email:
            raise ValueError("User must have an email address")

        if not username:
            raise ValueError("User must have an username")

        if not password:
            raise ValueError("User must have a password")

        user = self.create_user(
            email=self.normalize_email(email.lower()),
            username=username,
            password=password,
        )

        user.is_active = True
        user.is_staff = True
        user.is_admin = True
        user.is_superadmin = True
        user.save(using=self.db)

        return user


class Account(AbstractBaseUser):
    username = models.CharField(max_length=55, unique=True)
    email = models.EmailField(max_length=55, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    otp = models.CharField(max_length=55)
    activation_key = models.CharField(max_length=55)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True

    def get_all_permissions(user=None):
        if user.is_superadmin:
            return set()

    objects = MyAccountManager()

    def generate_otp(self):
        OTP_EXPIRATION_TIME_IN_SECONDS = 600
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret, interval=OTP_EXPIRATION_TIME_IN_SECONDS)
        OTP = totp.now()
        self.otp = OTP
        self.activation_key = secret

    def generate_otp_link(self, id, otp):
        otp = self.otp
        rel_url = reverse("accounts:verify-account", args=(id, otp))
        absolute_url = settings.DOMAIN + rel_url

        return absolute_url

    def generate_token(self, payload):
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm="HS256",
        )

        return token

    @staticmethod
    def decode_token(token):
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])


@receiver(post_save, sender=Account)
def print_only_after_deal_created(sender, instance, created, **kwargs):
    if created:
        instance.generate_otp()
        otp_absolute_url = instance.generate_otp_link(instance.id, instance.otp)
        email_subject = "Hesab T??sdiql??nm??si"

        template_path = get_template("accounts", "email_send_otp.html")
        email_content = get_html_content(
            template_path, otp_absolute_url=otp_absolute_url, domain=settings.DOMAIN
        )
        # rel_content = "Hesab??n??z?? t??sdiql??m??k ??????n a??a????dak?? link?? klik edin: \n"
        # email_content = rel_content + absolute_url
        send_email.delay(email_subject, instance.email, email_content)


class AccountDetail(models.Model):
    user = models.OneToOneField(
        Account,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="account_detail",
    )
    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=30, null=True)
    phone_number = models.CharField(max_length=20, null=True)
    city = models.CharField(max_length=30, null=True)
    address = models.CharField(max_length=50, null=True)
    postal_code = models.CharField(max_length=10, null=True)

    def __str__(self) -> str:
        return self.user.email
