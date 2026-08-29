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

    # ========================================================
    # PRODUCT CODE
    # ========================================================
    #
    # کد اختصاصی کالا
    #
    # ادمین می‌تواند خودش وارد کند:
    #
    # WATCH-001
    # BAG-025
    # SHOE-100
    #
    # اگر خالی باشد، هنگام ذخیره به صورت خودکار
    # یک کد مثل SAAP-000001 ساخته می‌شود.
    #
    # null=True برای جلوگیری از مشکل migration
    # محصولات قدیمی است.
    # ========================================================

    product_code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        blank=True,
        null=True,
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

        if self.product_code:

            return (
                f"{self.name} "
                f"[{self.product_code}]"
            )

        return self.name

    # ========================================================
    # SAVE PRODUCT
    # ========================================================

    def save(self, *args, **kwargs):

        # ----------------------------------------------------
        # ساخت Slug
        # ----------------------------------------------------

        if not self.slug:

            base_slug = slugify(
                self.name,
                allow_unicode=True
            )

            self.slug = (
                f"{base_slug}-"
                f"{uuid.uuid4().hex[:6]}"
            )

        # ----------------------------------------------------
        # ساخت خودکار Product Code
        # ----------------------------------------------------

        if not self.product_code:

            self.product_code = self.generate_product_code()

        super().save(*args, **kwargs)

    # ========================================================
    # GENERATE PRODUCT CODE
    # ========================================================

    @classmethod
    def generate_product_code(cls):

        """
        ساخت کد یکتای کالا.

        مثال:

        SAAP-000001
        SAAP-000002
        SAAP-000003
        """

        last_product = (
            cls.objects
            .filter(
                product_code__startswith='SAAP-'
            )
            .order_by('-id')
            .first()
        )

        if last_product and last_product.product_code:

            try:

                last_number = int(
                    last_product.product_code.split('-')[-1]
                )

            except (
                ValueError,
                TypeError
            ):

                last_number = 0

        else:

            last_number = 0

        while True:

            next_number = last_number + 1

            code = (
                f"SAAP-{next_number:06d}"
            )

            if not cls.objects.filter(
                product_code=code
            ).exists():

                return code

            last_number = next_number

    # ========================================================
    # ABSOLUTE URL
    # ========================================================

    def get_absolute_url(self):

        return reverse(
            'store:product_detail',
            kwargs={
                'slug': self.slug
            }
        )

    # ========================================================
    # FINAL PRICE
    # ========================================================

    @property
    def final_price(self):

        return (
            self.discount_price
            if self.discount_price
            else self.price
        )

    # ========================================================
    # HAS DISCOUNT
    # ========================================================

    @property
    def has_discount(self):

        return (
            self.discount_price is not None
            and self.discount_price < self.price
        )

    # ========================================================
    # DISCOUNT PERCENT
    # ========================================================

    @property
    def discount_percent(self):

        if self.has_discount:

            return int(
                (
                    (
                        self.price
                        - self.discount_price
                    )
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

    # ========================================================
    # PRODUCT CODE SNAPSHOT
    # ========================================================
    #
    # کد کالا در زمان خرید داخل سفارش ذخیره می‌شود.
    #
    # بنابراین اگر بعدها کد محصول تغییر کند،
    # سفارش‌های قبلی همچنان کد زمان خرید را دارند.
    # ========================================================

    product_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Product Code'
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

        if self.product_code:

            return (
                f"{self.quantity} x "
                f"{self.product_name} "
                f"[{self.product_code}]"
            )

        return (
            f"{self.quantity} x "
            f"{self.product_name}"
        )

    @property
    def subtotal(self):

        return (
            self.price
            * self.quantity
        )
