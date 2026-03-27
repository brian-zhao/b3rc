from django.contrib import admin
from .models import (
    SiteMedia, CarouselImage,
    Product, ProductImage, ProductVariant,
    Order, OrderItem,
)


@admin.register(SiteMedia)
class SiteMediaAdmin(admin.ModelAdmin):
    list_display = ('slot', 'file', 'alt_text', 'updated_at')
    list_editable = ('file', 'alt_text')
    ordering = ('slot',)


@admin.register(CarouselImage)
class CarouselImageAdmin(admin.ModelAdmin):
    list_display = ('order', 'image', 'alt_text')
    list_display_links = None
    list_editable = ('order', 'image', 'alt_text')
    ordering = ('order',)


# ── Shop Admin ───────────────────────────────────────────────────────────────

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'order')


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('sku', 'size', 'color', 'stock', 'price_override')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'base_price', 'is_active', 'is_preorder', 'sort_order')
    list_filter = ('category', 'is_active', 'is_preorder')
    list_editable = ('is_active', 'sort_order')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'variant_sku', 'size', 'color', 'quantity', 'unit_price', 'line_total')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'email', 'status', 'shipping_method', 'total', 'created_at')
    list_filter = ('status', 'shipping_method')
    search_fields = ('order_number', 'email', 'shipping_name')
    readonly_fields = (
        'order_number', 'stripe_session_id', 'stripe_payment_intent',
        'subtotal', 'shipping_cost', 'total', 'created_at', 'paid_at',
    )
    inlines = [OrderItemInline]
