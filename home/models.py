from unittest.util import _MAX_LENGTH
from django.db import models
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.contrib.auth import get_user_model


User = get_user_model()


class Employee(models.Model):
    name = models.CharField(max_length=55)
    surname = models.CharField(max_length=55)
    profession = models.CharField(max_length=55)
    description = models.TextField()
    email = models.EmailField(max_length=55)
    image = models.ImageField(upload_to='employees/%Y/%m/%d')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self) -> str:
        return f"{self.name} {self.surname}"


class Category(models.Model):
    name = models.CharField(max_length=55, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/")

    def __str__(self) -> str:
        return self.name
    
    def get_absolute_url(self):
        return reverse("home:products_by_category", args=[self.slug])

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)

        return super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "Categories"


class ProductImage(models.Model):
    image = models.ImageField(upload_to="products/%Y/%m/%d/")

    def __str__(self) -> str:
        return self.image.name


class Color(models.Model):
    name = models.CharField(max_length=55, unique=True)

    def __str__(self) -> str:
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=55, unique=True)

    def __str__(self) -> str:
        return self.name


class ProductProperty(models.Model):
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.size.name} size - {self.color.name}'


class Tag(models.Model):
    name = models.CharField(max_length=15)
    
    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(null=True, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.FloatField()
    images = models.ManyToManyField('ProductImage', related_name="products")
    stock = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_size_and_color = models.ManyToManyField(ProductProperty, related_name="products")
    visit_counter = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag, related_name="products", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("home:product_detail", args=[self.category.slug, self.slug])

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)

        return super().save(*args, **kwargs)


class Review(models.Model):
    stars = models.IntegerField()
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")

    def __str__(self) -> str:
        return f"{self.stars} stars - {self.description[:20]}"

    def save(self, *args, **kwargs):
        if self.stars > 5:
            self.stars = 5
        
        if self.stars < 1:
            self.stars = 1

        return super().save(*args, **kwargs)


class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return "{self.cart_id} - {self.date_added}"


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return self.product


class WishList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name="wish_list")

    def __str__(self) -> str:
        return f"{self.user.username}'s wish list"
