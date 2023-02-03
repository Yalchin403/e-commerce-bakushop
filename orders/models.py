from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .utils import send_status_update_to_user


class Order(models.Model):
    SE = "Sifariş Edilmeyib"
    SQ = "Sifariş Qəbul edildi"
    XAG = "Xarici Anbara Göndərilib"
    XA = "Xarici Anbardadır"
    XAGO = "Xarici Anbardan Göndərilib"
    GM = "Gömrük Məntəqəsindədir"
    DA = "Daxili Anbardadır"

    STATUSES = [
        ("SE", SE),
        ("SQ", SQ),
        ("XAG", XAG),
        ("XA", XA),
        ("XAGO", XAGO),
        ("GM", GM),
        ("DA", DA),
    ]

    name = models.CharField(max_length=55)
    surname = models.CharField(max_length=55)
    email = models.CharField(max_length=55)
    phone_number = models.CharField(max_length=55)
    order_url = models.TextField()
    notes = models.TextField()
    order_status = models.CharField(
        max_length=4,
        choices=STATUSES,
        default=SE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} {self.surname} - {self.phone_number}"


@receiver(pre_save, sender=Order)
def do_something_if_changed(sender, instance, **kwargs):
    try:
        previous_order_obj = Order.objects.get(id=instance.id)

        if (
            previous_order_obj.order_status != instance.order_status
        ):  # field will be updated
            # send email to the user about status change

            send_status_update_to_user(
                instance.name,
                instance.email,
                instance.order_status,
                instance.order_url,
                instance.notes,
            )

    except:
        pass  # that means this is new order not the status change
