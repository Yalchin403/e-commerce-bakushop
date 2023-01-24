from home.models import Product
from rest_framework import serializers


class ProductSerializer(serializers.ModelSerializer):
    is_in_my_wishlist = serializers.BooleanField(default=False)
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "price",
            "images",
            "stock",
            "category",
            "product_size_and_color",
            "visit_counter",
            "tags",
            "created_at",
            "updated_at",
            "is_in_my_wishlist",
        ]
        depth = 2
