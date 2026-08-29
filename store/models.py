from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
import uuid


# ============================================================
# CATEGORY
# ============================================================

class Category(models.Model):

    name = models.CharField(
        max_length=100,
        verbose_name='Name'
    )

    slug = models.SlugField(
        unique=True,
        allow_unicode=True
    )

    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        verbose_name='Image'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        verbose_name = 'Category'

        verbose_name_plural = 'Categories'

        ordering = ['name']

    def __str__(self):

        return self.name

    def save(self, *args, **kwargs):

        if not self.slug:

            self.slug = slugify(
                self.name,
                allow_unicode=True
            )

        super().save(*args, **kwargs)


# ============================================================
# PRODUCT
# ============================================================

class Product(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='دسته‌بندی'
    )

    name = models.CharField(
        max_length=200,
        verbose_name='Name'
    )
    product_code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name='Product Code'
    )
    slug = models.SlugField(
        unique=True,
        allow_unicode=True
    )

    description = models.TextField(
        verbose_name='Description'
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='Price (€)'
    )

    discount_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        blank=True,
        null=True,
        verbose_name='Discount Price'
    )

    image = models.ImageField(
        upload_to='products/',
        verbose_name='Main Image'
    )

    stock = models.PositiveIntegerField(
        default=0,
        verbose_name='Stock'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Active'
    )

    is_featured = models.BooleanField(
        default=False,
        verbose_name='Featured'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        verbose_name = 'Product'

        verbose_name_plural = 'Products'

        ordering = ['-created_at']

    def __str__(self):

        return self.name

    def save(self, *args, **kwargs):

        if not self.slug:

            base_slug = slugify(
                self.name,
                allow_unicode=True
            )

            self.slug = (
                f"{base_slug}-"
                f"{uuid.uuid4().hex[:6]}"
            )

        super().save(*args, **kwargs)

    def get_absolute_url(self):

        return reverse(
            'store:product_detail',
            kwargs={
                'slug': self.slug
            }
        )

    @property
    def final_price(self):

        return (
            self.discount_price
            if self.discount_price
            else self.price
        )

    @property
    def has_discount(self):

        return (
            self.discount_price is not None
            and self.discount_price < self.price
        )

    @property
    def discount_percent(self):

        if self.has_discount:

            return int(
                (
                    (self.price - self.discount_price)
                    / self.price
                ) * 100
            )

        return 0


# ============================================================
# PRODUCT IMAGE / GALLERY
# ============================================================

class ProductImage(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(
        upload_to='products/gallery/'
    )

    alt_text = models.CharField(
        max_length=200,
        blank=True
    )

    class Meta:

        verbose_name = 'Product Image'

        verbose_name_plural = 'Product Images'

    def __str__(self):

        return (
            f"{self.product.name} - "
            f"Image #{self.pk}"
        )


# ============================================================
# CART
# ============================================================

class Cart(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts'
    )

    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        verbose_name = 'Cart'

        verbose_name_plural = 'Carts'

    def __str__(self):

        return f"Cart {self.id}"

    @property
    def total_price(self):

        return sum(
            item.subtotal
            for item in self.items.all()
        )

    @property
    def total_items(self):

        return sum(
            item.quantity
            for item in self.items.all()
        )


# ============================================================
# CART ITEM
# ============================================================

class CartItem(models.Model):

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    class Meta:

        verbose_name = 'Cart Item'

        verbose_name_plural = 'Cart Items'

        unique_together = (
            'cart',
            'product'
        )

    def __str__(self):

        return (
            f"{self.quantity} x "
            f"{self.product.name}"
        )

    @property
    def subtotal(self):

        return (
            self.product.final_price
            * self.quantity
        )


# ============================================================
# ORDER
# ============================================================

class Order(models.Model):

    STATUS_CHOICES = [

        (
            'pending',
            'Pending'
        ),

        (
            'paid',
            'Paid'
        ),

        (
            'processing',
            'Processing'
        ),

        (
            'shipped',
            'Shipped'
        ),

        (
            'delivered',
            'Delivered'
        ),

        (
            'cancelled',
            'Cancelled'
        ),

    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    full_name = models.CharField(
        max_length=150,
        verbose_name='Full Name'
    )

    phone = models.CharField(
        max_length=15,
        verbose_name='Phone'
    )

    address = models.TextField(
        verbose_name='Address'
    )

    city = models.CharField(
        max_length=100,
        verbose_name='City'
    )

    postal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Postal Code'
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    note = models.TextField(
        blank=True,
        verbose_name='Note'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        verbose_name = 'Order'

        verbose_name_plural = 'Orders'

        ordering = ['-created_at']

    def __str__(self):

        return (
            f"Order #{self.id} - "
            f"{self.user.email}"
        )


# ============================================================
# ORDER ITEM
# ============================================================

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True
    )

    product_name = models.CharField(
        max_length=200
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=0
    )

    quantity = models.PositiveIntegerField()

    class Meta:

        verbose_name = 'Order Item'

        verbose_name_plural = 'Order Items'

    def __str__(self):

        return (
            f"{self.quantity} x "
            f"{self.product_name}"
        )

    @property
    def subtotal(self):

        return (
            self.price * self.quantity
        )
