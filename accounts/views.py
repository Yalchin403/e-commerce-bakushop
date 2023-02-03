from json import load
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.conf import settings
import os
import pyotp
from django.shortcuts import get_object_or_404
from accounts.tasks import send_email
from .utils import get_html_content
from .models import templates_directory, AccountDetail


User = get_user_model()


class SignInView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home:home")

        return render(request, "accounts/signin.html", {"title": "Giriş"})

    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            next_ = request.GET.get("next")
            if next_:
                return redirect(f"{settings.DOMAIN}{next_}")

            return redirect("home:home")

        else:
            messages.error(request, "Username or password invalid")

            return render(request, "accounts/signin.html")


class SignUpView(View):
    def get(self, request):
        if not self.request.user.is_authenticated:
            context = {
                "title": "Qeydiyyat",
            }

            return render(request, "accounts/signup.html", context)

        return redirect("home:home")

    def post(self, request):

        # TODO:
        # write some js for validation and checking if user accepted terms and conditions
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        is_agree = request.POST.get("agree-term")

        if username and email and password1 and password2 and is_agree == "on":
            user_qs_by_username = User.objects.filter(username=username)
            user_qs_by_email = User.objects.filter(email=email)

            if not user_qs_by_email and not user_qs_by_username:

                if password1 == password2:
                    user_obj = User.objects.create(username=username, email=email)
                    user_obj.set_password(password2)
                    user_obj.save()
                    messages.success(
                        request, f"Account has been successfully created for you"
                    )

                    return render(request, "accounts/signin.html", {"title": "Giriş"})

                else:
                    messages.error(request, "Parollar uyğun gəlmədi!!")

                    return render(
                        request, "accounts/signup.html", {"title": "Qeydiyyat"}
                    )

            else:

                if user_qs_by_email:
                    messages.error(request, "Email artıq istifadə olunub!")

                else:
                    messages.error(request, "Istifadəçi adı artıq istifadə olunub!")

        else:
            messages.error(request, "Bütün xanalar doldurulmalıdır!")

        return render(request, "accounts/signup.html", {"title": "Qeydiyyat"})


class VerifyAccountView(View):
    def get(self, request, id, otp):
        account_obj = get_object_or_404(User, id=id)
        if not account_obj.is_active:

            activation_key = account_obj.activation_key
            totp = pyotp.TOTP(activation_key, interval=600)

            _otp = account_obj.otp
            if otp != _otp:
                return render(request, "accounts/invalid_otp.html", status=406)

            else:
                verify = totp.verify(otp)

                if verify:
                    account_obj.is_active = True
                    email_subject = "Hesabınız təsdiqləndi"
                    receiver_email = account_obj.email
                    email_content = (
                        "Saytımıza xoş gəldiniz, hesabınız uğurla təsdiqləndi!"
                    )
                    send_email.delay(email_subject, receiver_email, email_content)
                    account_obj.save()

                    return render(request, "accounts/account_verified.html", status=200)

                else:
                    return render(request, "accounts/otp_expired.html", status=410)

        return render(request, "accounts/account_is_already_verified.html", status=409)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("accounts:signin-view")


class ResendOTP(View):
    def get(self, request, user_id):
        user_obj = get_object_or_404(User, id=user_id)
        user_obj.generate_otp()
        otp_absolute_url = user_obj.generate_otp_link(user_obj.id, user_obj.otp)
        email_subject = "Hesab Təsdiqlənməsi"
        template_path = os.path.join(templates_directory, "email_send_otp.html")
        email_content = get_html_content(
            template_path, otp_absolute_url=otp_absolute_url, domain=settings.domain
        )
        # rel_content = "Hesabınızı təsdiqləmək üçün aşağıdakı linkə klik edin: \n"
        # email_content = rel_content + absolute_url
        send_email.delay(email_subject, user_obj.email, email_content)

        return HttpResponse(
            "Emailinizə hesabınızı təsdiqləmək üçün link yenidən göndərildi!"
        )


class AccountView(View):
    def get(self, request):
        current_user_account = get_object_or_404(AccountDetail, user=request.user)
        context = {"account": current_user_account}
        return render(request, "accounts/account_detail.html", context=context)

    def post(self, request):
        current_user_account = get_object_or_404(AccountDetail, user=request.user)
        context = {"account": current_user_account}
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        mobile = request.POST.get("phone_number")
        city = request.POST.get("city")
        address = request.POST.get("address")
        postal_code = request.POST.get("postal_code")

        email_already_exists = User.objects.filter(email=email).exists()
        mobile_already_exists = AccountDetail.objects.filter(
            phone_number=mobile
        ).exists()

        if email_already_exists or mobile_already_exists:
            if email_already_exists:
                messages.add_message(
                    request, messages.ERROR, "User with this email already exists"
                )
            if mobile_already_exists:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "User with this phone number already exists",
                )

            return render(request, "accounts/account_detail.html", context=context)

        # TODO: check if email is valid
        # TODO: add url for confirming url with token -> /auth/change-email/:token
        # send verification email
        token = request.user.generate_token(
            {"id": self.request.user.id, "email": email}
        )
        absolute_url = f"{settings.DOMAIN}/auth/change-email/{token}/"
        template_path = os.path.join(templates_directory, "change_email.html")
        email_content = get_html_content(template_path, absolute_url=absolute_url)
        send_email.delay("Yeni emailinizi tesdiqləyin", email, email_content)

        current_user_account.first_name = first_name
        current_user_account.last_name = last_name
        current_user_account.phone_number = mobile
        current_user_account.city = city
        current_user_account.address = address
        current_user_account.postal_code = postal_code

        current_user_account.save()

        return render(request, "accounts/account_detail.html", context=context)
