"""
Management command: load persistent Firestore data into the ephemeral SQLite DB.

Run on every GAE instance startup, before gunicorn starts.
"""
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime

from decimal import Decimal

from b3rc_site import firestore_service, signals
from b3rc_site.models import (
    Announcement,
    SiteMedia, CarouselImage,
    Post, PostComment, PostLike, BlogImage,
    Product, ProductImage, ProductVariant, Order, OrderItem,
)


class Command(BaseCommand):
    help = 'Sync data from Firestore into the local SQLite database'

    def handle(self, *args, **options):
        # Disable Firestore write-back signals during import
        signals._syncing = True
        try:
            self._sync_announcements()
            self._sync_blog_images()
            self._sync_posts()
            self._sync_post_comments()
            self._sync_post_likes()
            self._sync_site_media()
            self._sync_carousel_images()
            self._sync_products()
            self._sync_product_images()
            self._sync_product_variants()
            self._sync_orders()
            self._sync_order_items()
        finally:
            signals._syncing = False

    def _sync_announcements(self):
        from django.utils.dateparse import parse_datetime
        docs = firestore_service.list_announcements()
        count = 0
        for doc in docs:
            valid_from = doc.get('valid_from')
            if isinstance(valid_from, str):
                valid_from = parse_datetime(valid_from)
            valid_to = doc.get('valid_to')
            if isinstance(valid_to, str):
                valid_to = parse_datetime(valid_to)
            Announcement.objects.update_or_create(
                pk=doc['pk'],
                defaults={
                    'message':    doc.get('message', ''),
                    'link_url':   doc.get('link_url', ''),
                    'link_label': doc.get('link_label', 'Read more'),
                    'valid_from': valid_from,
                    'valid_to':   valid_to,
                    'is_active':  doc.get('is_active', True),
                    'bg_color':   doc.get('bg_color', '#0B3C56'),
                },
            )
            count += 1
        self.stdout.write(f'Synced {count} Announcement record(s) from Firestore')

    def _sync_site_media(self):
        docs = firestore_service.list_site_media()
        count = 0
        for doc in docs:
            updated_at = doc.get('updated_at')
            if isinstance(updated_at, str):
                updated_at = parse_datetime(updated_at)

            SiteMedia.objects.update_or_create(
                slot=doc['slot'],
                defaults={
                    'file': doc.get('file', ''),
                    'alt_text': doc.get('alt_text', ''),
                },
            )
            # Manually set updated_at since auto_now=True ignores defaults
            if updated_at:
                SiteMedia.objects.filter(slot=doc['slot']).update(
                    updated_at=updated_at
                )
            count += 1
        self.stdout.write(f'Synced {count} SiteMedia record(s) from Firestore')

    def _sync_carousel_images(self):
        docs = firestore_service.list_carousel_images()
        count = 0
        for doc in docs:
            CarouselImage.objects.update_or_create(
                pk=doc['pk'],
                defaults={
                    'image': doc.get('image', ''),
                    'alt_text': doc.get('alt_text', ''),
                    'order': doc.get('order', 0),
                },
            )
            count += 1
        self.stdout.write(
            f'Synced {count} CarouselImage record(s) from Firestore'
        )

    def _sync_products(self):
        docs = firestore_service.list_products()
        count = 0
        for doc in docs:
            Product.objects.update_or_create(
                slug=doc['slug'],
                defaults={
                    'name': doc.get('name', ''),
                    'short_description': doc.get('short_description', ''),
                    'description': doc.get('description', ''),
                    'category': doc.get('category', 'APPAREL'),
                    'base_price': Decimal(doc.get('base_price', '0')),
                    'is_active': doc.get('is_active', True),
                    'is_preorder': doc.get('is_preorder', False),
                    'preorder_eta': doc.get('preorder_eta', ''),
                    'sort_order': doc.get('sort_order', 0),
                },
            )
            count += 1
        self.stdout.write(f'Synced {count} Product record(s) from Firestore')

    def _sync_product_images(self):
        docs = firestore_service.list_product_images()
        count = 0
        for doc in docs:
            try:
                product = Product.objects.get(slug=doc['product_slug'])
            except Product.DoesNotExist:
                continue
            ProductImage.objects.update_or_create(
                pk=doc['pk'],
                defaults={
                    'product': product,
                    'image': doc.get('image', ''),
                    'alt_text': doc.get('alt_text', ''),
                    'order': doc.get('order', 0),
                },
            )
            count += 1
        self.stdout.write(f'Synced {count} ProductImage record(s) from Firestore')

    def _sync_product_variants(self):
        docs = firestore_service.list_product_variants()
        count = 0
        for doc in docs:
            try:
                product = Product.objects.get(slug=doc['product_slug'])
            except Product.DoesNotExist:
                continue
            price_override = doc.get('price_override')
            ProductVariant.objects.update_or_create(
                sku=doc['sku'],
                defaults={
                    'product': product,
                    'size': doc.get('size', ''),
                    'color': doc.get('color', ''),
                    'stock': doc.get('stock', 0),
                    'price_override': Decimal(price_override) if price_override is not None else None,
                },
            )
            count += 1
        self.stdout.write(f'Synced {count} ProductVariant record(s) from Firestore')

    def _sync_orders(self):
        from django.contrib.auth.models import User
        docs = firestore_service.list_orders()
        count = 0
        for doc in docs:
            user = None
            user_id = doc.get('user_id')
            if user_id:
                user = User.objects.filter(pk=user_id).first()
            paid_at = doc.get('paid_at')
            if isinstance(paid_at, str):
                paid_at = parse_datetime(paid_at)
            Order.objects.update_or_create(
                order_number=doc['order_number'],
                defaults={
                    'user': user,
                    'email': doc.get('email', ''),
                    'status': doc.get('status', 'PENDING'),
                    'stripe_session_id': doc.get('stripe_session_id', ''),
                    'stripe_payment_intent': doc.get('stripe_payment_intent', ''),
                    'shipping_name': doc.get('shipping_name', ''),
                    'shipping_address': doc.get('shipping_address', ''),
                    'shipping_method': doc.get('shipping_method', 'PICKUP'),
                    'shipping_cost': Decimal(doc.get('shipping_cost', '0')),
                    'subtotal': Decimal(doc.get('subtotal', '0')),
                    'total': Decimal(doc.get('total', '0')),
                    'paid_at': paid_at,
                },
            )
            count += 1
        self.stdout.write(f'Synced {count} Order record(s) from Firestore')

    def _sync_order_items(self):
        docs = firestore_service.list_order_items()
        count = 0
        for doc in docs:
            try:
                order = Order.objects.get(order_number=doc['order_number'])
            except Order.DoesNotExist:
                continue
            product = None
            product_id = doc.get('product_id')
            if product_id:
                product = Product.objects.filter(pk=product_id).first()
            OrderItem.objects.update_or_create(
                pk=doc['pk'],
                defaults={
                    'order': order,
                    'product': product,
                    'product_name': doc.get('product_name', ''),
                    'variant_sku': doc.get('variant_sku', ''),
                    'size': doc.get('size', ''),
                    'color': doc.get('color', ''),
                    'quantity': doc.get('quantity', 0),
                    'unit_price': Decimal(doc.get('unit_price', '0')),
                    'line_total': Decimal(doc.get('line_total', '0')),
                },
            )
            count += 1
        self.stdout.write(f'Synced {count} OrderItem record(s) from Firestore')

    def _sync_blog_images(self):
        docs = firestore_service.list_blog_images()
        count = 0
        for doc in docs:
            uploaded_at = doc.get('uploaded_at')
            if isinstance(uploaded_at, str):
                uploaded_at = parse_datetime(uploaded_at)
            BlogImage.objects.update_or_create(
                pk=doc['pk'],
                defaults={
                    'image': doc.get('image', ''),
                    'caption': doc.get('caption', ''),
                    'uploaded_at': uploaded_at,
                },
            )
            count += 1
        self.stdout.write(f'Synced {count} BlogImage record(s) from Firestore')

    def _sync_posts(self):
        from datetime import date
        from django.contrib.auth.models import User
        docs = firestore_service.list_posts()
        count = 0
        for doc in docs:
            author = None
            author_id = doc.get('author_id')
            if author_id:
                author = User.objects.filter(pk=author_id).first()
            published_at = doc.get('published_at')
            if isinstance(published_at, str):
                published_at = parse_datetime(published_at)
            created_at = doc.get('created_at')
            if isinstance(created_at, str):
                created_at = parse_datetime(created_at)
            updated_at = doc.get('updated_at')
            if isinstance(updated_at, str):
                updated_at = parse_datetime(updated_at)
            event_date = doc.get('event_date')
            if isinstance(event_date, str) and event_date:
                event_date = date.fromisoformat(event_date)
            Post.objects.update_or_create(
                slug=doc['slug'],
                defaults={
                    'title': doc.get('title', ''),
                    'category': doc.get('category', 'EVENT'),
                    'status': doc.get('status', 'DRAFT'),
                    'body': doc.get('body', ''),
                    'featured_image': doc.get('featured_image', ''),
                    'video_url': doc.get('video_url', ''),
                    'event_date': event_date,
                    'location': doc.get('location', ''),
                    'strava_url': doc.get('strava_url', ''),
                    'is_featured': doc.get('is_featured', False),
                    'author': author,
                    'published_at': published_at,
                },
            )
            count += 1
        self.stdout.write(f'Synced {count} Post record(s) from Firestore')

    def _sync_post_comments(self):
        from django.contrib.auth.models import User
        from django.utils.dateparse import parse_datetime
        docs = firestore_service.list_comments()
        count = 0
        for doc in docs:
            try:
                post = Post.objects.get(slug=doc['post_slug'])
            except Post.DoesNotExist:
                continue
            user = User.objects.filter(pk=doc.get('user_id')).first()
            if not user:
                continue
            created_at = doc.get('created_at')
            if isinstance(created_at, str):
                created_at = parse_datetime(created_at)
            PostComment.objects.update_or_create(
                pk=doc['pk'],
                defaults={'post': post, 'user': user, 'body': doc.get('body', '')},
            )
            if created_at:
                PostComment.objects.filter(pk=doc['pk']).update(created_at=created_at)
            count += 1
        self.stdout.write(f'Synced {count} PostComment record(s) from Firestore')

    def _sync_post_likes(self):
        from django.contrib.auth.models import User
        docs = firestore_service.list_likes()
        count = 0
        for doc in docs:
            try:
                post = Post.objects.get(slug=doc['post_slug'])
            except Post.DoesNotExist:
                continue
            user = User.objects.filter(pk=doc.get('user_id')).first()
            if not user:
                continue
            PostLike.objects.get_or_create(pk=doc['pk'], defaults={'post': post, 'user': user})
            count += 1
        self.stdout.write(f'Synced {count} PostLike record(s) from Firestore')
