from django.contrib import admin
from .models import Category, Product, ProductImage, Cart, CartItem, Order, OrderItem


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_code', 'category', 'price', 'discount_price', 'stock', 'is_active', 'is_featured', 'created_at']
    list_filter = ['is_active', 'is_featured', 'category', 'created_at']
    search_fields = ['name', 'description', 'product_code']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'discount_price', 'stock', 'is_active', 'is_featured']
    inlines = [ProductImageInline]
    fieldsets = (
        ('Basic Info', {
            'fields': ('category', 'name', 'slug', 'product_code', 'description', 'image')
        }),
        ('Price & Stock', {
            'fields': ('price', 'discount_price', 'stock')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_code', 'price', 'quantity']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'full_name', 'phone', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['full_name', 'phone', 'user__email']
    list_editable = ['status']
    inlines = [OrderItemInline]
    readonly_fields = ['user', 'total_price', 'created_at']


admin.site.site_header = 'Shopyaar Admin'
admin.site.site_title = 'Shopyaar'
admin.site.index_title = 'Store Management'
