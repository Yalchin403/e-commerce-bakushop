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
)


class EmployeeManager(admin.ModelAdmin):
    list_display = ["name", "surname", "image", "profession"]


admin.site.register(Employee, EmployeeManager)
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
