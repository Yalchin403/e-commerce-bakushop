from django.contrib import admin
from .models import (
    Employee,
    Product,
    ProductImage,
    Category,
    Color,
    Review,
    Size,
    ProductProperty,
    Tag,
    WishList,
    Cart,
    CartItem,
)


class BaseAdmin(admin.ModelAdmin):
    readonly_fields = [
        "created_at",
        "updated_at",
    ]


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["name", "surname", "image", "profession"]


class CartItemAdmin(admin.ModelAdmin):
    readonly_fields = [
        "created_at",
        "updated_at",
        "subtotal",
        "total",
        "date_purchased",
        "quantity",
        # "cart",
        # "product",
        "purchased",
    ]
    list_display = [
        "created_at",
        "updated_at",
        "subtotal",
        "total",
        "date_purchased",
        "quantity",
        "cart",
        "product",
        "purchased",
    ]
    search_fields = ("cart__user__email", "product__name")
    list_filter = ["purchased", "deleted"]


class CartAdmin(BaseAdmin):
    readonly_fields = [
        "created_at",
        "updated_at",
        "user",
    ]
    list_display = [
        "user",
        "is_active",
        "created_at",
        "updated_at",
    ]

    search_fields = ("user__email",)
    list_filter = [
        "is_active",
    ]


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Cart, CartAdmin)

admin.site.register(
    [
        Product,
        ProductImage,
        Category,
        Color,
        Size,
        ProductProperty,
        Review,
        Tag,
        WishList,
    ]
)
