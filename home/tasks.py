from celery import shared_task
from django.contrib.auth import get_user_model
from home.models import Product, WishList


@shared_task
def sync_session_fav_products_to_db_delayed(session_fav_products_ids: list, user_id: int)-> None:
    products = Product.objects.filter(id__in=session_fav_products_ids)    
    wish_list = WishList.objects.get_or_create(
        user__id=user_id
    )[0]


    wish_list.products.add(*products)