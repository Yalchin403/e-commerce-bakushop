from django.contrib.auth.signals import user_logged_in
from .models import Product, WishList
from .tasks import sync_session_fav_products_to_db_delayed
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from accounts.models import AccountDetail
from .models import WishList
from django.dispatch import receiver
import logging


logger = logging.getLogger(__name__)
User = get_user_model()


def sync_session_fav_products_to_db(sender, user, request, **kwargs) -> None:
    session_fav_products_ids = request.session.get("fav_products", [])

    if len(session_fav_products_ids) == 0:
        return

    # heavy lifting
    sync_session_fav_products_to_db_delayed.delay(
        session_fav_products_ids,
        user.id,
    )


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        WishList.objects.create(user=instance)
        logger.debug(f"Wishlist creater for {instance}")
        AccountDetail.objects.create(user=instance)
        logger.debug(f"Profile creater for {instance}")


user_logged_in.connect(sync_session_fav_products_to_db)
