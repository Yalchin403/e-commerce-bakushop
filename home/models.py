from unittest.util import _MAX_LENGTH
from django.db import models
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.contrib.auth import get_user_model
from order_automation.utils import notify_critic_stock
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator


User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Employee(BaseModel):
    name = models.CharField(max_length=55)
    surname = models.CharField(max_length=55)
    profession = models.CharField(max_length=55)
    description = models.TextField()
    email = models.EmailField(max_length=55)
    image = models.ImageField(upload_to="employees/%Y/%m/%d")

    def __str__(self) -> str:
        return f"{self.name} {self.surname}"


class Category(BaseModel):
    name = models.CharField(max_length=55, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("home:products_by_category", args=[self.slug])

    class Meta:
        verbose_name_plural = "Categories"


class ProductImage(BaseModel):
    image = models.ImageField(upload_to="products/%Y/%m/%d/")

    def __str__(self) -> str:
        return self.image.name


class Color(BaseModel):
    name = models.CharField(max_length=55, unique=True)

    def __str__(self) -> str:
        return self.name


class Size(BaseModel):
    name = models.CharField(max_length=55, unique=True)

    def __str__(self) -> str:
        return self.name


class ProductProperty(BaseModel):
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["color", "size"], name="unique_color_size")
        ]
        verbose_name_plural = "Product Properties"

    def __str__(self) -> str:
        return f"{self.size.name} size - {self.color.name}"


class Tag(BaseModel):
    name = models.CharField(max_length=15)

    def __str__(self) -> str:
        return self.name


class Product(BaseModel):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(null=True, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(
        null=True,
        blank=True,
        max_digits=5,
        decimal_places=2,
        default=Decimal(0.00),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    images = models.ManyToManyField("ProductImage", related_name="products")
    stock = models.IntegerField()
    critic_stock = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_size_and_color = models.ManyToManyField(
        ProductProperty, related_name="products"
    )
    visit_counter = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag, related_name="products", blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("home:product_detail", args=[self.category.slug, self.slug])

    def get_admin_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        relative_url = reverse(
            "admin:{}_{}_change".format(content_type.app_label, content_type.model),
            args=[self.id],
        )
        return f"{settings.DOMAIN}{relative_url}"

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)

        if self.stock < self.critic_stock:
            notify_critic_stock(self.get_admin_absolute_url())

        return super().save(*args, **kwargs)


class Review(BaseModel):
    stars = models.IntegerField()
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )

    def __str__(self) -> str:
        return f"{self.stars} stars - {self.description[:20]}"

    def save(self, *args, **kwargs):
        if self.stars > 5:
            self.stars = 5

        if self.stars < 1:
            self.stars = 1

        return super().save(*args, **kwargs)


class Cart(BaseModel):
    is_active = models.BooleanField(default=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def add_to_cart(self, product, quantity):
        cart_item, created = CartItem.objects.get_or_create(cart=self, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

    @property
    def get_subtotal(self):
        cart_items = CartItem.objects.filter(cart=self, cart__is_active=True)
        return sum([cart_item.subtotal for cart_item in cart_items])

    @property
    def get_total(self):
        cart_items = CartItem.objects.filter(cart=self, cart__is_active=True)
        return sum([cart_item.total for cart_item in cart_items])

    def __str__(self) -> str:
        return str(self.user)


class CartItem(BaseModel):
    status_choices = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("SHIPPED", "Shipped"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    ]
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    purchased = models.BooleanField(default=False)
    status = models.CharField(choices=status_choices, max_length=20, default="PENDING")
    date_purchased = models.DateTimeField(null=True, blank=True)
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0.00)
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0.00))
    deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.cart} - {self.quantity} - {self.product}"

    def save(self, *args, **kwargs) -> None:
        self.subtotal = self.product.price * self.quantity
        self.total = (
            self.subtotal
            - self.product.price
            * (self.product.discount_percentage / 100)
            * self.quantity
        )
        super(CartItem, self).save(*args, **kwargs)


class WishList(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name="wish_list")

    def __str__(self) -> str:
        return f"{self.user.username}'s wish list"
