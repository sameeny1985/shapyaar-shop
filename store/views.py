from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.conf import settings
from django.urls import reverse
from django.db import transaction

import stripe
import requests

from .models import (
    Product,
    Category,
    Cart,
    CartItem,
    Order,
    OrderItem,
)


# ============================================================
# STRIPE CONFIGURATION
# ============================================================

stripe.api_key = settings.STRIPE_SECRET_KEY


# ============================================================
# TELEGRAM ORDER NOTIFICATION
# ============================================================

def send_telegram_order_notification(order):
    """
    ارسال اطلاعات سفارش به Telegram

    اطلاعات هر محصول شامل:
    - نام محصول
    - کد کالا
    - تعداد
    - قیمت
    """

    if (
        not settings.TELEGRAM_BOT_TOKEN
        or not settings.TELEGRAM_CHAT_ID
    ):
        return

    items_text = ""

    for item in order.items.all():

        # ----------------------------------------------------
        # دریافت کد کالا
        # ----------------------------------------------------

        product_code = getattr(
            item,
            'product_code',
            ''
        )

        # اگر OrderItem کد نداشت، از Product بگیر
        if not product_code and item.product:

            product_code = getattr(
                item.product,
                'product_code',
                ''
            )

        if not product_code:

            product_code = '---'

        # ----------------------------------------------------
        # ساخت اطلاعات محصول
        # ----------------------------------------------------

        items_text += (
            f"▫️ {item.product_name}\n"
            f"   🏷️ کد کالا: {product_code}\n"
            f"   🔢 تعداد: {item.quantity}\n"
            f"   💶 قیمت: {item.price}\n\n"
        )

    # ========================================================
    # MESSAGE
    # ========================================================

    message = (
        f"🚀 *سفارش موفق جدید در Sory Shop ثبت شد!*\n\n"

        f"🆔 *شماره سفارش:* {order.id}\n"

        f"👤 *نام خریدار:* {order.full_name}\n"

        f"📞 *تلفن:* {order.phone}\n"

        f"📍 *شهر:* {order.city}\n"

        f"🏠 *آدرس:* {order.address}\n"
    )

    if order.postal_code:

        message += (
            f"📮 *کد پستی:* "
            f"{order.postal_code}\n"
        )

    if order.note:

        message += (
            f"📝 *یادداشت:* "
            f"{order.note}\n"
        )

    message += (
        f"\n"
        f"📦 *اقلام خریداری شده:*\n\n"
        f"{items_text}"
        f"💰 *مبلغ کل:* {order.total_price}"
    )

    # ========================================================
    # TELEGRAM API
    # ========================================================

    url = (
        f"https://api.telegram.org/"
        f"bot{settings.TELEGRAM_BOT_TOKEN}/"
        f"sendMessage"
    )

    payload = {

        "chat_id": settings.TELEGRAM_CHAT_ID,

        "text": message,

        "parse_mode": "Markdown",

    }

    try:

        response = requests.post(
            url,
            json=payload,
            timeout=10
        )

        # بررسی خطای Telegram
        if not response.ok:

            print(
                "Telegram Error:",
                response.text
            )

    except Exception as e:

        print(
            "Telegram Error:",
            e
        )


# ============================================================
# GET OR CREATE CART
# ============================================================

def get_or_create_cart(request):

    if request.user.is_authenticated:

        cart, _ = Cart.objects.get_or_create(
            user=request.user
        )

    else:

        if not request.session.session_key:

            request.session.create()

        cart, _ = Cart.objects.get_or_create(
            session_key=request.session.session_key
        )

    return cart


# ============================================================
# HOME
# ============================================================

def home(request):

    featured = Product.objects.filter(
        is_active=True,
        is_featured=True
    )[:8]

    latest = Product.objects.filter(
        is_active=True
    )[:12]

    categories = Category.objects.all()[:6]

    return render(
        request,
        'store/home.html',
        {
            'featured_products': featured,
            'latest_products': latest,
            'categories': categories,
        }
    )


# ============================================================
# PRODUCT LIST + SEARCH
# ============================================================

def product_list(request):

    # --------------------------------------------------------
    # تمام محصولات فعال
    # --------------------------------------------------------

    products = Product.objects.filter(
        is_active=True
    )

    # --------------------------------------------------------
    # دریافت پارامترها
    # --------------------------------------------------------

    category_slug = request.GET.get(
        'category'
    )

    search = request.GET.get(
        'q',
        ''
    ).strip()

    sort = request.GET.get(
        'sort',
        'newest'
    )

    # --------------------------------------------------------
    # فیلتر دسته‌بندی
    # --------------------------------------------------------

    if category_slug:

        products = products.filter(
            category__slug=category_slug
        )

    # --------------------------------------------------------
    # جستجو
    #
    # جستجو بر اساس:
    # 1. نام محصول
    # 2. توضیحات
    # 3. کد کالا
    # --------------------------------------------------------

    if search:

        products = products.filter(

            Q(
                name__icontains=search
            )

            |

            Q(
                description__icontains=search
            )

            |

            Q(
                product_code__icontains=search
            )

        )

    # --------------------------------------------------------
    # مرتب‌سازی
    # --------------------------------------------------------

    if sort == 'price_low':

        products = products.order_by(
            'price'
        )

    elif sort == 'price_high':

        products = products.order_by(
            '-price'
        )

    elif sort == 'name':

        products = products.order_by(
            'name'
        )

    else:

        products = products.order_by(
            '-created_at'
        )

    # --------------------------------------------------------
    # Pagination
    # --------------------------------------------------------

    paginator = Paginator(
        products,
        12
    )

    page = request.GET.get(
        'page'
    )

    products = paginator.get_page(
        page
    )

    # --------------------------------------------------------
    # Categories
    # --------------------------------------------------------

    categories = Category.objects.all()

    # --------------------------------------------------------
    # Render
    # --------------------------------------------------------

    return render(

        request,

        'store/product_list.html',

        {

            'products': products,

            'categories': categories,

            'current_category': category_slug,

            'search_query': search,

            'sort': sort,

        }

    )


# ============================================================
# PRODUCT DETAIL
# ============================================================

def product_detail(request, slug):

    product = get_object_or_404(

        Product,

        slug=slug,

        is_active=True

    )

    related = (

        Product.objects

        .filter(

            category=product.category,

            is_active=True

        )

        .exclude(

            id=product.id

        )[:4]

    )

    return render(

        request,

        'store/product_detail.html',

        {

            'product': product,

            'related_products': related,

        }

    )


# ============================================================
# ADD TO CART
# ============================================================

def add_to_cart(request, product_id):

    product = get_object_or_404(

        Product,

        id=product_id,

        is_active=True

    )

    # --------------------------------------------------------
    # موجودی
    # --------------------------------------------------------

    if product.stock < 1:

        messages.error(
            request,
            'این محصول موجود نیست.'
        )

        return redirect(
            product.get_absolute_url()
        )

    # --------------------------------------------------------
    # Cart
    # --------------------------------------------------------

    cart = get_or_create_cart(
        request
    )

    cart_item, created = (
        CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )
    )

    # --------------------------------------------------------
    # افزایش تعداد
    # --------------------------------------------------------

    if not created:

        if cart_item.quantity < product.stock:

            cart_item.quantity += 1

            cart_item.save()

        else:

            messages.warning(
                request,
                'موجودی کافی نیست.'
            )

            return redirect(
                'store:cart'
            )

    # --------------------------------------------------------
    # پیام
    # --------------------------------------------------------

    messages.success(

        request,

        f'«{product.name}» '
        f'به سبد خرید اضافه شد.'

    )

    return redirect(
        'store:cart'
    )


# ============================================================
# CART
# ============================================================

def cart_view(request):

    cart = get_or_create_cart(
        request
    )

    return render(

        request,

        'store/cart.html',

        {
            'cart': cart
        }

    )


# ============================================================
# UPDATE CART
# ============================================================

def update_cart(request, item_id):

    cart = get_or_create_cart(
        request
    )

    item = get_object_or_404(

        CartItem,

        id=item_id,

        cart=cart

    )

    action = request.POST.get(
        'action'
    )

    # --------------------------------------------------------
    # Increase
    # --------------------------------------------------------

    if action == 'increase':

        if item.quantity < item.product.stock:

            item.quantity += 1

            item.save()

        else:

            messages.warning(
                request,
                'موجودی کافی نیست.'
            )

    # --------------------------------------------------------
    # Decrease
    # --------------------------------------------------------

    elif action == 'decrease':

        if item.quantity > 1:

            item.quantity -= 1

            item.save()

        else:

            item.delete()

    # --------------------------------------------------------
    # Remove
    # --------------------------------------------------------

    elif action == 'remove':

        item.delete()

        messages.info(
            request,
            'محصول از سبد حذف شد.'
        )

    return redirect(
        'store:cart'
    )


# ============================================================
# CHECKOUT
# ============================================================

@login_required
def checkout(request):

    cart = get_or_create_cart(
        request
    )

    # --------------------------------------------------------
    # Empty cart
    # --------------------------------------------------------

    if not cart.items.exists():

        messages.warning(
            request,
            'سبد خرید شما خالی است.'
        )

        return redirect(
            'store:product_list'
        )

    # ========================================================
    # POST
    # ========================================================

    if request.method == 'POST':

        full_name = request.POST.get(
            'full_name'
        )

        phone = request.POST.get(
            'phone'
        )

        address = request.POST.get(
            'address'
        )

        city = request.POST.get(
            'city'
        )

        postal_code = request.POST.get(
            'postal_code',
            ''
        )

        note = request.POST.get(
            'note',
            ''
        )

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        if not all(
            [
                full_name,
                phone,
                address,
                city
            ]
        ):

            messages.error(
                request,
                'لطفاً تمام فیلدهای ضروری را پر کنید.'
            )

            return render(

                request,

                'store/checkout.html',

                {
                    'cart': cart
                }

            )

        # ====================================================
        # CREATE ORDER
        # ====================================================

        with transaction.atomic():

            order = Order.objects.create(

                user=request.user,

                full_name=full_name,

                phone=phone,

                address=address,

                city=city,

                postal_code=postal_code,

                note=note,

                total_price=cart.total_price,

                status='pending',

            )

            # ------------------------------------------------
            # CREATE ORDER ITEMS
            # ------------------------------------------------

            for item in cart.items.select_related(
                'product'
            ):

                product = item.product

                # --------------------------------------------
                # Product Code
                # --------------------------------------------

                product_code = getattr(
                    product,
                    'product_code',
                    ''
                )

                # --------------------------------------------
                # ذخیره کد کالا در OrderItem
                # --------------------------------------------

                OrderItem.objects.create(

                    order=order,

                    product=product,

                    product_name=product.name,

                    product_code=product_code,

                    price=product.final_price,

                    quantity=item.quantity,

                )

                # --------------------------------------------
                # Reduce Stock
                # --------------------------------------------

                product.stock -= item.quantity

                product.save(
                    update_fields=[
                        'stock'
                    ]
                )

            # ------------------------------------------------
            # پاکسازی سبد
            # ------------------------------------------------

            cart.items.all().delete()

        # ====================================================
        # STRIPE CHECKOUT
        # ====================================================

        domain = (
            request.build_absolute_uri('/')
            .rstrip('/')
        )

        line_items = []

        for item in order.items.all():

            line_items.append({

                'price_data': {

                    'currency': 'usd',

                    'product_data': {

                        'name':
                            item.product_name,

                    },

                    'unit_amount':
                        int(
                            float(item.price)
                            * 100
                        ),

                },

                'quantity':
                    item.quantity,

            })

        # ====================================================
        # CREATE STRIPE SESSION
        # ====================================================

        try:

            checkout_session = (
                stripe.checkout.Session.create(

                    payment_method_types=[
                        'card'
                    ],

                    line_items=line_items,

                    mode='payment',

                    success_url=(
                        domain
                        + reverse(
                            'store:payment_success'
                        )
                        + f'?order_id={order.id}'
                    ),

                    cancel_url=(
                        domain
                        + reverse(
                            'store:payment_cancel'
                        )
                    ),

                )
            )

            return redirect(
                checkout_session.url,
                code=303
            )

        except Exception as e:

            messages.error(

                request,

                f'خطا در اتصال به درگاه پرداخت: {e}'

            )

            return redirect(
                'store:cart'
            )

    # ========================================================
    # GET
    # ========================================================

    return render(

        request,

        'store/checkout.html',

        {
            'cart': cart
        }

    )


# ============================================================
# ORDER SUCCESS
# ============================================================

@login_required
def order_success(request, order_id):

    order = get_object_or_404(

        Order,

        id=order_id,

        user=request.user

    )

    return render(

        request,

        'store/order_success.html',

        {
            'order': order
        }

    )


# ============================================================
# MY ORDERS
# ============================================================

@login_required
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    )

    return render(

        request,

        'store/my_orders.html',

        {
            'orders': orders
        }

    )


# ============================================================
# PAYMENT SUCCESS
# ============================================================

def payment_success_view(request):

    order_id = request.GET.get(
        'order_id'
    )

    order = None

    if order_id:

        try:

            order = Order.objects.get(
                id=order_id
            )

            # ------------------------------------------------
            # پرداخت موفق
            # ------------------------------------------------

            order.status = 'paid'

            order.save(
                update_fields=[
                    'status'
                ]
            )

            # ------------------------------------------------
            # ارسال Telegram
            # ------------------------------------------------

            send_telegram_order_notification(
                order
            )

        except Order.DoesNotExist:

            pass

    return render(

        request,

        'store/order_success.html',

        {
            'order': order
        }

    )


# ============================================================
# PAYMENT CANCEL
# ============================================================

def payment_cancel_view(request):

    messages.warning(

        request,

        'عملیات پرداخت لغو شد.'

    )

    return redirect(
        'store:cart'
    )
