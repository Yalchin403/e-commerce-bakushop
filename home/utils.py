from order_automation.settings import EMAIL_HOST_USER
import os
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from .models import WishList


User = get_user_model()


def send_message_to_admin(name, email, subject, message):
    email_body = f"""
        <h1>{name} tərəfindən yeni mesajınız var!</h1>

        <ul>
        <li>Email: {email}</li>
        <li>Mövzu: {subject}</li>
        <li>Mesaj: {message}</li>
        <ul>
        """
    reciever_email = os.getenv('ADMIN_EMAIL')

    msg = EmailMessage(
        f"Yeni Mesaj - Mövzu -> {subject}",
        email_body,
        EMAIL_HOST_USER,
        [reciever_email]
    )
    msg.content_subtype = "html"
    msg.send()


def get_request_params(request):
    sort_by = ""
    filter_by_price = ""
    filter_by_color = ""
    filter_by_tags = ""

    if "sort_by" in request.GET:
        sort_by = request.GET['sort_by']
        
        if sort_by == "popularity":
            sort_by = "-visit_counter"

        elif sort_by == "average_rating":
            sort_by = "average_rating"

        elif sort_by == "price_low_to_high":
            sort_by = "price"
        
        elif sort_by == "price_high_to_low":
            sort_by = "-price"

        else:
            sort_by = ""

    if "filter_by_price" in request.GET:
        filter_by_price = request.GET['filter_by_price']

        filter_by_price_options  = ["0-50", "50-100", "100-150", "150-200", "gte200"]
        
        if filter_by_price in filter_by_price_options:
            filter_by_price_index = filter_by_price_options.index(filter_by_price)
            filter_by_price = filter_by_price_options[filter_by_price_index]
        
    else:
        filter_by_price = ""

    if "filter_by_color" in request.GET:
        filter_by_color = request.GET['filter_by_color']
    
    if "filter_by_tags" in request.GET:
        filter_by_tags = request.GET['filter_by_tags']

    return sort_by, filter_by_price, filter_by_color, filter_by_tags
    

# custom contect processor for getting wish_list_items count
def get_wish_list_item_counts(request)-> int:
    wish_list_count = 0

    if request.user.is_authenticated:        
        wish_list = WishList.objects.filter(user=request.user).first()
        wish_list_count = wish_list.products.count()
    
    else:
        fav_products = request.session.get("fav_products", [])
        wish_list_count = len(fav_products)

    return {
        "user_fav_products_count": wish_list_count
    }