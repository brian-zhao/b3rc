from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import (
    Announcement,
    SiteMedia, CarouselImage,
    Post, PostComment, BlogImage,
    Product, ProductImage, ProductVariant,
    Order, OrderItem,
)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display  = ('message_preview', 'is_active', 'valid_from', 'valid_to', 'status_badge')
    list_filter   = ('is_active',)
    list_editable = ('is_active',)
    search_fields = ('message',)

    def message_preview(self, obj):
        return obj.message[:80] + ('…' if len(obj.message) > 80 else '')
    message_preview.short_description = 'Message'

    def status_badge(self, obj):
        from django.utils import timezone
        now = timezone.now()
        if not obj.is_active:
            label, color = 'Inactive', '#999'
        elif obj.valid_from > now:
            label, color = 'Scheduled', '#856404'
        elif obj.valid_to < now:
            label, color = 'Expired', '#842029'
        else:
            label, color = 'Live', '#1e7e34'
        return format_html('<span style="color:{};font-weight:700">{}</span>', color, label)
    status_badge.short_description = 'Status'


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


# ── Blog Admin ───────────────────────────────────────────────────────────────

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display  = ('title', 'category', 'status_badge', 'event_date', 'is_featured', 'published_at')
    list_filter   = ('status', 'category', 'is_featured')
    list_editable = ('is_featured',)
    search_fields = ('title', 'body', 'location')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'event_date'
    readonly_fields = ('created_at', 'updated_at', 'published_at', 'image_preview')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'status', 'is_featured', 'author'),
        }),
        ('Content', {
            'fields': ('body', 'featured_image', 'image_preview', 'video_url'),
        }),
        ('Event Details', {
            'fields': ('event_date', 'location', 'strava_url'),
        }),
        ('Timestamps', {
            'fields': ('published_at', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def status_badge(self, obj):
        colour = '#00A550' if obj.status == 'PUBLISHED' else '#999'
        return format_html(
            '<span style="color:{};font-weight:600;">{}</span>',
            colour, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def image_preview(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" style="max-height:120px;border-radius:6px;">', obj.featured_image.url)
        return '—'
    image_preview.short_description = 'Preview'

    def save_model(self, request, obj, form, change):
        # Auto-set author on first save
        if not obj.pk and not obj.author:
            obj.author = request.user
        # Auto-set published_at when first published
        if obj.status == 'PUBLISHED' and not obj.published_at:
            obj.published_at = timezone.now()
        elif obj.status == 'DRAFT':
            obj.published_at = None
        super().save_model(request, obj, form, change)


@admin.register(BlogImage)
class BlogImageAdmin(admin.ModelAdmin):
    list_display  = ('thumbnail', 'caption', 'uploaded_at', 'snippet')
    readonly_fields = ('uploaded_at', 'markdown_snippet', 'image_preview')
    fields = ('image', 'caption', 'uploaded_at', 'image_preview', 'markdown_snippet')
    search_fields = ('caption',)

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;border-radius:4px;">', obj.image.url)
        return '—'
    thumbnail.short_description = ''

    def snippet(self, obj):
        return format_html('<code style="font-size:11px;">{}</code>', obj.markdown)
    snippet.short_description = 'Markdown snippet'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:200px;border-radius:6px;">', obj.image.url)
        return '—'
    image_preview.short_description = 'Preview'

    def markdown_snippet(self, obj):
        if not obj.pk:
            return '— save first to generate snippet —'
        return format_html(
            '<input type="text" value="{}" readonly '
            'style="width:100%;font-family:monospace;font-size:12px;padding:6px 8px;'
            'border:1px solid #ccc;border-radius:4px;background:#f8f8f8;" '
            'onclick="this.select()">',
            obj.markdown,
        )
    markdown_snippet.short_description = 'Markdown snippet (click to select)'


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter  = ('post',)
    search_fields = ('user__email', 'body')
    readonly_fields = ('created_at',)


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
