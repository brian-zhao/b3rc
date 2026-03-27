from decimal import Decimal
from django.db import models
from django.utils import timezone


class SiteMedia(models.Model):
    SLOT_CHOICES = [
        ('hero_bg', 'Home — Hero Background'),
        ('about_image', 'Home — About Section Image'),
        ('tagline_bg', 'Home — Tagline Background'),
    ]

    slot = models.CharField(max_length=30, choices=SLOT_CHOICES, unique=True)
    file = models.FileField(upload_to='site_media/')
    alt_text = models.CharField(max_length=200, blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Media'
        verbose_name_plural = 'Site Media'

    def __str__(self):
        return self.get_slot_display()

    @property
    def is_video(self):
        return self.file.name.lower().endswith(('.mp4', '.webm', '.mov'))


class CarouselImage(models.Model):
    image = models.ImageField(upload_to='carousel/')
    alt_text = models.CharField(max_length=200, blank=True, default='')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Carousel Image'
        verbose_name_plural = 'Carousel Images'
        ordering = ['order']

    def __str__(self):
        return f'Carousel #{self.order} — {self.alt_text or self.image.name}'


# ── Shop Models ──────────────────────────────────────────────────────────────

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('APPAREL', 'Apparel'),
        ('ACCESSORIES', 'Accessories'),
        ('RACE_KIT', 'Race Kit'),
    ]

    slug = models.SlugField(max_length=200, unique=True)
    name = models.CharField(max_length=200)
    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True, help_text='Markdown supported')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)
    is_preorder = models.BooleanField(default=False)
    preorder_eta = models.CharField(max_length=100, blank=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.name

    @property
    def primary_image(self):
        return self.images.first()

    @property
    def in_stock(self):
        return self.variants.filter(stock__gt=0).exists()

    @property
    def price_display(self):
        return f'${self.base_price:.2f}'


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.product.name} — image #{self.order}'


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    size = models.CharField(max_length=10)
    color = models.CharField(max_length=50, blank=True)
    sku = models.CharField(max_length=50, unique=True)
    stock = models.IntegerField(default=0)
    price_override = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['size']

    def __str__(self):
        parts = [self.product.name, self.size]
        if self.color:
            parts.append(self.color)
        return ' / '.join(parts)

    @property
    def effective_price(self):
        return self.price_override if self.price_override is not None else self.product.base_price

    @property
    def in_stock(self):
        return self.stock > 0


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    SHIPPING_CHOICES = [
        ('PICKUP', 'Pickup at Training'),
        ('STANDARD', 'Standard Shipping ($10)'),
    ]

    order_number = models.CharField(max_length=30, unique=True)
    user = models.ForeignKey(
        'auth.User', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='orders',
    )
    email = models.EmailField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    stripe_session_id = models.CharField(max_length=200, blank=True)
    stripe_payment_intent = models.CharField(max_length=200, blank=True)

    shipping_name = models.CharField(max_length=200, blank=True)
    shipping_address = models.TextField(blank=True)
    shipping_method = models.CharField(max_length=20, choices=SHIPPING_CHOICES, default='PICKUP')
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))

    subtotal = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))

    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order_number} — {self.status}'

    @staticmethod
    def generate_order_number():
        now = timezone.now()
        date_part = now.strftime('%Y%m%d')
        # Count today's orders for sequential number
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        count = Order.objects.filter(created_at__gte=today_start).count() + 1
        return f'B3RC-{date_part}-{count:04d}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    product_name = models.CharField(max_length=200)
    variant_sku = models.CharField(max_length=50)
    size = models.CharField(max_length=10)
    color = models.CharField(max_length=50, blank=True)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    line_total = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f'{self.product_name} x{self.quantity}'
