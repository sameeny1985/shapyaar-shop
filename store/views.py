from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product, Category, Cart, CartItem, Order, OrderItem


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


def home(request):
    featured = Product.objects.filter(is_active=True, is_featured=True)[:8]
    latest = Product.objects.filter(is_active=True)[:12]
    categories = Category.objects.all()[:6]
    return render(request, 'store/home.html', {
        'featured_products': featured,
        'latest_products': latest,
        'categories': categories,
    })


def product_list(request):
    products = Product.objects.filter(is_active=True)
    category_slug = request.GET.get('category')
    search = request.GET.get('q')
    sort = request.GET.get('sort', 'newest')

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if search:
        products = products.filter(Q(name__icontains=search) | Q(description__icontains=search))

    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')

    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    categories = Category.objects.all()
    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search or '',
        'sort': sort,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]
    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related,
    })


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    if product.stock < 1:
        messages.error(request, 'این محصول موجود نیست.')
        return redirect(product.get_absolute_url())

    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.warning(request, 'موجودی کافی نیست.')
            return redirect('store:cart')
    messages.success(request, f'«{product.name}» به سبد خرید اضافه شد.')
    return redirect('store:cart')


def cart_view(request):
    cart = get_or_create_cart(request)
    return render(request, 'store/cart.html', {'cart': cart})


def update_cart(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    action = request.POST.get('action')
    if action == 'increase':
        if item.quantity < item.product.stock:
            item.quantity += 1
            item.save()
    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
    elif action == 'remove':
        item.delete()
        messages.info(request, 'محصول از سبد حذف شد.')
    return redirect('store:cart')


@login_required
def checkout(request):
    cart = get_or_create_cart(request)
    if not cart.items.exists():
        messages.warning(request, 'سبد خرید شما خالی است.')
        return redirect('store:product_list')

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code', '')
        note = request.POST.get('note', '')

        if not all([full_name, phone, address, city]):
            messages.error(request, 'لطفاً تمام فیلدهای ضروری را پر کنید.')
            return render(request, 'store/checkout.html', {'cart': cart})

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
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                price=item.product.final_price,
                quantity=item.quantity,
            )
            # Reduce stock
            item.product.stock -= item.quantity
            item.product.save()
        cart.items.all().delete()
        messages.success(request, f'سفارش شما با شماره #{order.id} ثبت شد. به زودی با شما تماس می‌گیریم.')
        return redirect('store:order_success', order_id=order.id)

    return render(request, 'store/checkout.html', {'cart': cart})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_success.html', {'order': order})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/my_orders.html', {'orders': orders})
