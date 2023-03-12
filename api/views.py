from rest_framework.views import APIView
from rest_framework import authentication, permissions
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from home.models import Product, WishList, CartItem, Cart
from rest_framework.response import Response
from .custom_api_exceptions import AutherizationError
from .serializers import ProductSerializer, CartItemSerializer
from rest_framework import generics, status, filters
from home.utils import get_request_params
from django.db.models import Q, ExpressionWrapper, BooleanField, Avg
from rest_framework.pagination import PageNumberPagination
import logging
from home.choices import CartItemStatuses


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
                },
                status=status.HTTP_200_OK,
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
            },
            status=status.HTTP_201_CREATED,
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
                        },
                        status=status.HTTP_200_OK,
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
                        },
                        status=status.HTTP_201_CREATED,
                    )

            else:
                request.session["fav_products"] = [product_id]
                return Response(
                    {
                        "action": "added",
                        "productCounts": len(request.session["fav_products"]),
                    },
                    status=status.HTTP_201_CREATED,
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


class DeleteCartItem(generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    lookup_field = "id"
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(
            cart__user=self.request.user,
            deleted=False,
            status=CartItemStatuses.PENDING.value,
            cart__is_active=True,
        )

    def destroy(self, request, *args, **kwargs):
        object = self.get_object()
        object.deleted = True
        object.save()

        serializer = CartItemSerializer(object)
        return Response(serializer.data)


class DeleteCartItemUnauthenticated(APIView):
    def delete(self, request, product_id):
        if request.session.get("cartitems"):
            if product_id in request.session["cartitems"]:
                # ** remove product from local wishlist storage
                current_cartitems_products = request.session["cartitems"]
                current_cartitems_products.remove(product_id)
                request.session["cartitems"] = current_cartitems_products

            return Response(
                {
                    "action": "removed",
                    "cartItemCounts": len(current_cartitems_products),
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"message": "cart is empty"}, status=status.HTTP_409_CONFLICT
        )


class AddCartItem(APIView):
    """API endpoint to add/remove cart items for authenticated users"""

    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, product_id: int) -> str:
        current_user = User.objects.get(id=request.user.id)
        product_obj = get_object_or_404(Product, pk=product_id)
        # ** add or remove the product to/from WishList
        is_product_in_cart = CartItem.objects.filter(
            product=product_obj, cart__user=current_user, cart__is_active=True
        ).exists()

        if not is_product_in_cart:
            cart = Cart.objects.get_or_create(is_active=True, user=current_user)[0]
            print(cart)
            CartItem.objects.create(
                cart=cart,
                product=product_obj,
            )
        cartitem = CartItem.objects.get(product=product_obj, cart__user=current_user)
        cartitem.deleted = False
        cartitem.save()

        cart_items_count = CartItem.objects.filter(cart__user=current_user).count()

        return Response(
            {
                "action": "added",
                "productCounts": cart_items_count,
            },
            status=status.HTTP_201_CREATED,
        )


class AddCartItemUnauthenticated(APIView):
    """API endpoint to add/remove cart items for unauthenticated users"""

    def post(self, request, product_id):
        if request.user.is_authenticated:
            raise AutherizationError()

        is_product_exists = Product.objects.filter(stock__gt=1, id=product_id).exists()

        if is_product_exists:
            if request.session.get("cartitems"):
                if product_id not in request.session["cartitems"]:
                    request.session["cartitems"] += [
                        product_id,
                    ]

                return Response(
                    {
                        "action": "added",
                        "cartItemCounts": len(request.session["cartitems"]),
                    },
                    status=status.HTTP_201_CREATED,
                )

            else:
                request.session["cartitems"] = [product_id]
                return Response(
                    {
                        "action": "added",
                        "cartItemCounts": len(request.session["cartitems"]),
                    },
                    status=status.HTTP_201_CREATED,
                )
