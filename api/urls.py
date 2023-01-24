from django.urls import path
from api.views import (
    AddRemoveWishlist,
    AddRemoveWishlistIUnauthenticated,
)
from .views import ProductDetail, ProductList


app_name = "api"
urlpatterns = [
    path(
        "add-remove-wishlist/<int:product_id>/",
        AddRemoveWishlist.as_view(),
        name="add-remove-wishlist",
    ),
    path(
        "add-remove-wishlist-unauthenticated/<int:product_id>/",
        AddRemoveWishlistIUnauthenticated.as_view(),
        name="add-remove-wishlist-unauthenticated",
    ),
    path("products/", ProductList.as_view(), name="products"),
    path("products/<int:id>/", ProductDetail.as_view(), name="product-detail"),
]
