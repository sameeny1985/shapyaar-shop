from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام دسته‌بندی')
    slug = models.SlugField(unique=True, allow_unicode=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name='تصویر')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='دسته‌بندی')
    name = models.CharField(max_length=200, verbose_name='نام محصول')
    slug = models.SlugField(unique=True, allow_unicode=True)
    description = models.TextField(verbose_name='توضیحات')
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='قیمت (تومان)')
    discount_price = models.DecimalField(max_digits=12, decimal_places=0, blank=True, null=True, verbose_name='قیمت با تخفیف')
    image = models.ImageField(upload_to='products/', verbose_name='تصویر اصلی')
    stock = models.PositiveIntegerField(default=0, verbose_name='موجودی')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    is_featured = models.BooleanField(default=False, verbose_name='ویژه')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            self.slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:product_detail', kwargs={'slug': self.slug})

    @property
    def final_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def has_discount(self):
        return self.discount_price is not None and self.discount_price < self.price

    @property
    def discount_percent(self):
        if self.has_discount:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'تصویر محصول'
        verbose_name_plural = 'تصاویر محصول'


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبدهای خرید'

    def __str__(self):
        return f"Cart {self.id}"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'آیتم سبد'
        verbose_name_plural = 'آیتم‌های سبد'
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        return self.product.final_price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('processing', 'در حال آماده‌سازی'),
        ('shipped', 'ارسال شده'),
        ('delivered', 'تحویل داده شده'),
        ('cancelled', 'لغو شده'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    full_name = models.CharField(max_length=150, verbose_name='نام کامل')
    phone = models.CharField(max_length=15, verbose_name='شماره تماس')
    address = models.TextField(verbose_name='آدرس')
    city = models.CharField(max_length=100, verbose_name='شهر')
    postal_code = models.CharField(max_length=20, blank=True, verbose_name='کد پستی')
    total_price = models.DecimalField(max_digits=12, decimal_places=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    note = models.TextField(blank=True, verbose_name='یادداشت')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارش‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.user.email}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=12, decimal_places=0)
    quantity = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'آیتم سفارش'
        verbose_name_plural = 'آیتم‌های سفارش'

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"

    @property
    def subtotal(self):
        return self.price * self.quantity
