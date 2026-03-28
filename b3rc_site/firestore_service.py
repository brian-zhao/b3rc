"""
Firestore client and CRUD helpers for SiteMedia and CarouselImage.

Firestore is the persistent source of truth. SQLite is an ephemeral cache
that gets populated from Firestore on each GAE instance startup.
"""
import os
from google.cloud import firestore


def get_client():
    """Return a Firestore client, respecting emulator env var."""
    project = os.getenv('FIRESTORE_PROJECT_ID', 'b3rc-467810')
    database = os.getenv('FIRESTORE_DATABASE_ID', 'b3rc')
    return firestore.Client(project=project, database=database)


# ── SiteMedia ──

def save_site_media(instance):
    """Upsert a SiteMedia document keyed by slot."""
    db = get_client()
    db.collection('site_media').document(instance.slot).set({
        'slot': instance.slot,
        'file': instance.file.name if instance.file else '',
        'alt_text': instance.alt_text,
        'updated_at': instance.updated_at,
    })


def delete_site_media(slot):
    """Delete a SiteMedia document by slot."""
    db = get_client()
    db.collection('site_media').document(slot).delete()


def list_site_media():
    """Return all SiteMedia documents as dicts."""
    db = get_client()
    return [doc.to_dict() for doc in db.collection('site_media').stream()]


# ── CarouselImage ──

def save_carousel_image(instance):
    """Upsert a CarouselImage document keyed by its PK."""
    db = get_client()
    db.collection('carousel_images').document(str(instance.pk)).set({
        'pk': instance.pk,
        'image': instance.image.name if instance.image else '',
        'alt_text': instance.alt_text,
        'order': instance.order,
    })


def delete_carousel_image(pk):
    """Delete a CarouselImage document by PK."""
    db = get_client()
    db.collection('carousel_images').document(str(pk)).delete()


def list_carousel_images():
    """Return all CarouselImage documents as dicts."""
    db = get_client()
    return [doc.to_dict() for doc in db.collection('carousel_images').stream()]


# ── Product ──

def save_product(instance):
    db = get_client()
    db.collection('products').document(instance.slug).set({
        'slug': instance.slug,
        'name': instance.name,
        'short_description': instance.short_description,
        'description': instance.description,
        'category': instance.category,
        'base_price': str(instance.base_price),
        'is_active': instance.is_active,
        'is_preorder': instance.is_preorder,
        'preorder_eta': instance.preorder_eta,
        'sort_order': instance.sort_order,
    })


def delete_product(slug):
    db = get_client()
    db.collection('products').document(slug).delete()


def list_products():
    db = get_client()
    return [doc.to_dict() for doc in db.collection('products').stream()]


# ── ProductImage ──

def save_product_image(instance):
    db = get_client()
    db.collection('product_images').document(str(instance.pk)).set({
        'pk': instance.pk,
        'product_slug': instance.product.slug,
        'image': instance.image.name if instance.image else '',
        'alt_text': instance.alt_text,
        'order': instance.order,
    })


def delete_product_image(pk):
    db = get_client()
    db.collection('product_images').document(str(pk)).delete()


def list_product_images():
    db = get_client()
    return [doc.to_dict() for doc in db.collection('product_images').stream()]


# ── ProductVariant ──

def save_product_variant(instance):
    db = get_client()
    db.collection('product_variants').document(instance.sku).set({
        'sku': instance.sku,
        'product_slug': instance.product.slug,
        'size': instance.size,
        'color': instance.color,
        'stock': instance.stock,
        'price_override': str(instance.price_override) if instance.price_override is not None else None,
    })


def delete_product_variant(sku):
    db = get_client()
    db.collection('product_variants').document(sku).delete()


def list_product_variants():
    db = get_client()
    return [doc.to_dict() for doc in db.collection('product_variants').stream()]


# ── Order ──

def save_order(instance):
    db = get_client()
    db.collection('orders').document(instance.order_number).set({
        'order_number': instance.order_number,
        'user_id': instance.user_id,
        'email': instance.email,
        'status': instance.status,
        'stripe_session_id': instance.stripe_session_id,
        'stripe_payment_intent': instance.stripe_payment_intent,
        'shipping_name': instance.shipping_name,
        'shipping_address': instance.shipping_address,
        'shipping_method': instance.shipping_method,
        'shipping_cost': str(instance.shipping_cost),
        'subtotal': str(instance.subtotal),
        'total': str(instance.total),
        'created_at': instance.created_at,
        'paid_at': instance.paid_at,
    })


def delete_order(order_number):
    db = get_client()
    db.collection('orders').document(order_number).delete()


def list_orders():
    db = get_client()
    return [doc.to_dict() for doc in db.collection('orders').stream()]


# ── OrderItem ──

def save_order_item(instance):
    db = get_client()
    db.collection('order_items').document(str(instance.pk)).set({
        'pk': instance.pk,
        'order_number': instance.order.order_number,
        'product_id': instance.product_id,
        'product_name': instance.product_name,
        'variant_sku': instance.variant_sku,
        'size': instance.size,
        'color': instance.color,
        'quantity': instance.quantity,
        'unit_price': str(instance.unit_price),
        'line_total': str(instance.line_total),
    })


def delete_order_item(pk):
    db = get_client()
    db.collection('order_items').document(str(pk)).delete()


def list_order_items():
    db = get_client()
    return [doc.to_dict() for doc in db.collection('order_items').stream()]


# ── Post ──

def save_post(instance):
    db = get_client()
    db.collection('posts').document(instance.slug).set({
        'slug': instance.slug,
        'title': instance.title,
        'category': instance.category,
        'status': instance.status,
        'body': instance.body,
        'featured_image': instance.featured_image.name if instance.featured_image else '',
        'video_url': instance.video_url,
        'event_date': instance.event_date.isoformat() if instance.event_date and hasattr(instance.event_date, 'isoformat') else (instance.event_date if instance.event_date else None),
        'location': instance.location,
        'strava_url': instance.strava_url,
        'is_featured': instance.is_featured,
        'author_id': instance.author_id,
        'published_at': instance.published_at,
        'created_at': instance.created_at,
        'updated_at': instance.updated_at,
    })


def delete_post(slug):
    db = get_client()
    db.collection('posts').document(slug).delete()


def list_posts():
    db = get_client()
    return [doc.to_dict() for doc in db.collection('posts').stream()]


# ── PostComment ──

def save_comment(instance):
    db = get_client()
    db.collection('post_comments').document(str(instance.pk)).set({
        'pk': instance.pk,
        'post_slug': instance.post.slug,
        'user_id': instance.user_id,
        'body': instance.body,
        'created_at': instance.created_at,
    })


def delete_comment(pk):
    db = get_client()
    db.collection('post_comments').document(str(pk)).delete()


def list_comments():
    db = get_client()
    return [doc.to_dict() for doc in db.collection('post_comments').stream()]


# ── PostLike ──

def save_like(instance):
    db = get_client()
    db.collection('post_likes').document(str(instance.pk)).set({
        'pk': instance.pk,
        'post_slug': instance.post.slug,
        'user_id': instance.user_id,
        'created_at': instance.created_at,
    })


def delete_like(pk):
    db = get_client()
    db.collection('post_likes').document(str(pk)).delete()


def list_likes():
    db = get_client()
    return [doc.to_dict() for doc in db.collection('post_likes').stream()]


# ── Announcement ──

def save_announcement(instance):
    db = get_client()
    db.collection('announcements').document(str(instance.pk)).set({
        'pk':         instance.pk,
        'message':    instance.message,
        'link_url':   instance.link_url,
        'link_label': instance.link_label,
        'valid_from': instance.valid_from,
        'valid_to':   instance.valid_to,
        'is_active':  instance.is_active,
        'bg_color':   instance.bg_color,
        'created_at': instance.created_at,
    })


def delete_announcement(pk):
    db = get_client()
    db.collection('announcements').document(str(pk)).delete()


def list_announcements():
    db = get_client()
    return [doc.to_dict() for doc in db.collection('announcements').stream()]
