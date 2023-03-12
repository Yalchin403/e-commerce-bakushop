from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import (
    Employee,
    Product,
    Category,
    WishList,
    Cart,
)
from .utils import get_request_params, send_message_to_admin
from django.contrib import messages
from django.db.models import Q, ExpressionWrapper, BooleanField, Avg
from django.conf import settings
from django.core.paginator import Paginator


class HomeView(View):
    # request url format
    # http://localhost:8000/?sort_by=price_low_to_high&filter_by_price=0-26&filter_by_color=ag&filter_by_tags=Lifestyle
    def get(self, request):
        session_id = request.session.session_key
        sort_by, filter_by_price, filter_by_color, filter_by_tags = get_request_params(
            request
        )
        product_qs = Product.objects.filter(stock__gt=0)
        category_qs = Category.objects.all()

        if sort_by:
            if sort_by == "average_rating":
                product_qs = product_qs.annotate(
                    average_rating=Avg("reviews__stars")
                ).order_by("-average_rating")

            else:
                product_qs = product_qs.order_by(sort_by)

        if filter_by_price:
            try:
                gte, lte = filter_by_price.split("-")
                product_qs = product_qs.filter(price__lte=int(lte), price__gte=int(gte))

            except:
                if filter_by_price == "gte200":
                    product_qs = product_qs.filter(price__gte=int(200))

                else:
                    return redirect("https://http.cat/500")

        if filter_by_color:
            product_qs = product_qs.filter(
                product_size_and_color__color__name=filter_by_color
            )

        if filter_by_tags:
            product_qs = product_qs.filter(tags__name=filter_by_tags)

        if not sort_by:
            sort_by = "default"

        if not filter_by_price:
            filter_by_price = "all"

        # add is in wishlist property to each product
        if request.user.is_authenticated:
            product_qs = product_qs.annotate(
                is_in_my_wishlist=ExpressionWrapper(
                    Q(wish_list__user__id=request.user.id), output_field=BooleanField()
                )
            )

        if not request.user.is_authenticated:
            fav_products_list = request.session.get("fav_products", [])

            if len(fav_products_list) > 0:
                product_qs = product_qs.annotate(
                    is_in_my_wishlist=ExpressionWrapper(
                        Q(id__in=fav_products_list), output_field=BooleanField()
                    )
                )

        context = {
            "sort_by": sort_by,
            "filter_by_price": filter_by_price,
            "filter_by_color": filter_by_color,
            "filter_by_tags": filter_by_tags,
            "products": product_qs,
            "categories": category_qs,
            "session_id": session_id,
        }

        return render(request, "home/home.html", context)


class HomeDetailView(View):
    def get(self, request, category, slug):
        product_obj = get_object_or_404(Product, category__slug=category, slug=slug)
        context = {
            "product": product_obj,
            "base_url": settings.domain,
        }
        try:
            product_viewed_cookie = request.session[f"product_{product_obj.id}_viewed"]

        except:
            request.session[f"product_{product_obj.id}_viewed"] = 0
            product_obj.visit_counter += 1
            product_obj.save()

        return render(request, "home/detail.html", context)


class SearchView(View):
    def get(self, request):
        lookup = request.GET.get("lookup")

        product_qs = Product.objects.filter(
            Q(name__icontains=lookup)
            | Q(slug__icontains=lookup)
            | Q(description__icontains=lookup)
            | Q(price__icontains=lookup)
            | Q(category__name__icontains=lookup)
        )

        category_qs = Category.objects.all()
        context = {
            "products": product_qs,
            "categories": category_qs,
        }

        return render(request, "home/home.html", context)


class AboutView(View):
    def get(self, request):
        employee_qs = Employee.objects.all()
        context = {"employees": employee_qs, "title": "Haqqımızda"}

        return render(request, "home/about.html", context)


class ContactView(View):
    def get(self, request):
        context = {"title": "Əlaqə"}

        return render(request, "home/contact.html", context)

    def post(self, request):
        # Formdan gelen datalari gotur
        # try:
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        if (
            name is not None
            and subject is not None
            and email is not None
            and message is not None
        ):
            send_message_to_admin(name, email, subject, message)

            messages.success(request, "Your message has been sent successfully!")

        else:
            messages.error(request, "Error. Message not sent.")

        return render(request, "home/contact.html")


class LogView(View):
    def get(self, request):
        from django.http import HttpResponse
        import logging

        logger = logging.getLogger(__name__)
        logger.debug("DEBUG log")
        logger.info("INFO log")
        logger.warning("WARNING log")
        logger.critical("CRITICAL log")
        logger.error("ERROR log")

        return HttpResponse("Log is done")


class CartView(View):
    def get(self, request):
        if self.request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user, is_active=True)
            cart_items = cart.cart_items.all()
            paginator = Paginator(cart_items, 10)
            page_number = request.GET.get("page")
            page_obj = paginator.get_page(page_number)
            context = {"cart": cart, "cart_items": page_obj}

            return render(request, "home/shopping-cart.html", context=context)

        else:
            if request.session.get("cartitems"):
                cartitems_products = request.session.get("cartitems")
                # TODO: think how you will handle it

            return render(request, "home/shopping-cart.html", context={})


    def post(self, request):
        ...
