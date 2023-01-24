from rest_framework.views import APIView
from rest_framework import authentication, permissions
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from home.models import (
    Product,
    WishList,
)
from rest_framework.response import Response
from .custom_api_exceptions import AutherizationError
from .serializers import ProductSerializer
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from home.utils import get_request_params
from django.db.models import Q, ExpressionWrapper, BooleanField, Avg
from rest_framework.pagination import PageNumberPagination
import logging


User = get_user_model()
LOGGER = logging.getLogger(__name__)


class AddRemoveWishlist(APIView):
    """
    ** add/remove product to/from wishlist
    """

    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, product_id: int) -> str:
        current_user = User.objects.get(id=request.user.id)
        product_obj = get_object_or_404(Product, pk=product_id)
        # ** add or remove the product to/from WishList
        is_product_in_wishList = WishList.objects.filter(
            products=product_obj, user=current_user
        ).exists()

        if is_product_in_wishList:
            wish_list = WishList.objects.get(user=current_user)
            # ** remove the item from wishlist
            wish_list.products.remove(product_obj)
            wish_list_items_count = wish_list.products.count()

            return Response(
                {
                    "action": "removed",
                    "productCounts": wish_list_items_count,
                }
            )

        has_wish_list = WishList.objects.filter(user=current_user).exists()

        if has_wish_list:
            wish_list = WishList.objects.get(user=current_user)
            # ** add product to wishlist
            wish_list.products.add(product_obj)
            wish_list_items_count = wish_list.products.count()

        else:
            wish_list = WishList.objects.create(
                user=current_user,
            )
            # ** add product to wishlist
            wish_list.products.add(product_obj)
            wish_list_items_count = wish_list.products.count()

        return Response(
            {
                "action": "added",
                "productCounts": wish_list_items_count,
            }
        )


class AddRemoveWishlistIUnauthenticated(APIView):
    """
    ** add/remove product to/from wishlist for unauthernticated users
    """

    def get(self, request, product_id):
        if request.user.is_authenticated:
            raise AutherizationError()

        is_product_exists = Product.objects.filter(stock__gt=1, id=product_id).exists()

        if is_product_exists:

            if request.session.get("fav_products"):

                if product_id in request.session["fav_products"]:
                    # ** remove product from local wishlist storage
                    current_fav_products = request.session["fav_products"]
                    current_fav_products.remove(product_id)
                    request.session["fav_products"] = current_fav_products

                    return Response(
                        {
                            "action": "removed",
                            "productCounts": len(current_fav_products),
                        }
                    )

                else:
                    # ** add this product to current user's local wishlist storage
                    request.session["fav_products"] += [
                        product_id,
                    ]

                    return Response(
                        {
                            "action": "added",
                            "productCounts": len(request.session["fav_products"]),
                        }
                    )

            else:
                request.session["fav_products"] = [product_id]
                return Response(
                    {
                        "action": "added",
                        "productCounts": len(request.session["fav_products"]),
                    }
                )


class ProductPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"


class ProductList(generics.ListAPIView):
    queryset = Product.objects.filter(stock__gt=0, is_deleted=False)
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "slug", "description", "category__name"]

    def get_queryset(self):
        sort_by, filter_by_price, filter_by_color, filter_by_tags = get_request_params(
            self.request
        )
        product_qs = Product.objects.filter(stock__gt=0, is_deleted=False)

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
                    return []

        if filter_by_color:
            product_qs = product_qs.filter(
                product_size_and_color__color__name__iexact=filter_by_color
            )

        if filter_by_tags:
            product_qs = product_qs.filter(tags__name_iexact=filter_by_tags)

        LOGGER.debug(f"{self.request.user.is_authenticated}")
        if self.request.user.is_authenticated:
            product_qs = product_qs.annotate(
                is_in_my_wishlist=ExpressionWrapper(
                    Q(wish_list__user__id=self.request.user.id),
                    output_field=BooleanField(),
                )
            )

        if not self.request.user.is_authenticated:
            fav_products_list = self.request.session.get("fav_products", [])

            if len(fav_products_list) > 0:
                product_qs = product_qs.annotate(
                    is_in_my_wishlist=ExpressionWrapper(
                        Q(id__in=fav_products_list), output_field=BooleanField()
                    )
                )

        return product_qs


class ProductDetail(generics.RetrieveAPIView):
    queryset = Product.objects.filter(stock__gt=0, is_deleted=False)
    serializer_class = ProductSerializer
    lookup_field = "id"
