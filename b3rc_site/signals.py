"""
Django signals that sync model saves/deletes to Firestore.

A _syncing flag prevents infinite loops when sync_from_firestore
bulk-creates records back into SQLite.
"""
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

logger = logging.getLogger(__name__)

# When True, signals skip Firestore writes (used during sync_from_firestore).
_syncing = False


@receiver(post_save, sender='b3rc_site.SiteMedia')
def site_media_saved(sender, instance, **kwargs):
    if _syncing:
        return
    try:
        from . import firestore_service
        firestore_service.save_site_media(instance)
    except Exception:
        logger.exception('Failed to sync SiteMedia to Firestore')


@receiver(post_delete, sender='b3rc_site.SiteMedia')
def site_media_deleted(sender, instance, **kwargs):
    if _syncing:
        return
    try:
        from . import firestore_service
        firestore_service.delete_site_media(instance.slot)
    except Exception:
        logger.exception('Failed to delete SiteMedia from Firestore')


@receiver(post_save, sender='b3rc_site.CarouselImage')
def carousel_image_saved(sender, instance, **kwargs):
    if _syncing:
        return
    try:
        from . import firestore_service
        firestore_service.save_carousel_image(instance)
    except Exception:
        logger.exception('Failed to sync CarouselImage to Firestore')


@receiver(post_delete, sender='b3rc_site.CarouselImage')
def carousel_image_deleted(sender, instance, **kwargs):
    if _syncing:
        return
    try:
        from . import firestore_service
        firestore_service.delete_carousel_image(instance.pk)
    except Exception:
        logger.exception('Failed to delete CarouselImage from Firestore')


# ── Shop signals ─────────────────────────────────────────────────────────────

@receiver(post_save, sender='b3rc_site.Product')
def product_saved(sender, instance, **kwargs):
    if _syncing:
        return
    try:
        from . import firestore_service
        firestore_service.save_product(instance)
    except Exception:
        logger.exception('Failed to sync Product to Firestore')


@receiver(post_delete, sender='b3rc_site.Product')
def product_deleted(sender, instance, **kwargs):
    if _syncing:
        return
    try:
        from . import firestore_service
        firestore_service.delete_product(instance.slug)
    except Exception:
        logger.exception('Failed to delete Product from Firestore')


@receiver(post_save, sender='b3rc_site.ProductImage')
def product_image_saved(sender, instance, **kwargs):
    if _syncing:
        return
    try:
        from . import firestore_service
        firestore_service.save_product_image(instance)
    except Exception:
        logger.exception('Failed to sync ProductImage to Firestore')


@receiver(post_delete, sender='b3rc_site.ProductImage')
def product_image_deleted(sender, instance, **kwargs):
    if _syncing:
        return
    try:
        from . import firestore_service
        firestore_service.delete_product_image(instance.pk)
    except Exception:
        logger.exception('Failed to delete ProductImage from Firestore')


@receiver(post_save, sender='b3rc_site.ProductVariant')
def product_variant_saved(sender, instance, **kwargs):
    if _syncing:
        return
    try:
        from . import firestore_service
        firestore_service.save_product_variant(instance)
    except Exception:
        logger.exception('Failed to sync ProductVariant to Firestore')


@receiver(post_delete, sender='b3rc_site.ProductVariant')
def product_variant_deleted(sender, instance, **kwargs):
    if _syncing:
        return
    try:
        from . import firestore_service
        firestore_service.delete_product_variant(instance.sku)
    except Exception:
        logger.exception('Failed to delete ProductVariant from Firestore')


@receiver(post_save, sender='b3rc_site.Order')
def order_saved(sender, instance, **kwargs):
    if _syncing:
        return
    try:
        from . import firestore_service
        firestore_service.save_order(instance)
    except Exception:
        logger.exception('Failed to sync Order to Firestore')


@receiver(post_delete, sender='b3rc_site.Order')
def order_deleted(sender, instance, **kwargs):
    if _syncing:
        return
    try:
        from . import firestore_service
        firestore_service.delete_order(instance.order_number)
    except Exception:
        logger.exception('Failed to delete Order from Firestore')


@receiver(post_save, sender='b3rc_site.OrderItem')
def order_item_saved(sender, instance, **kwargs):
    if _syncing:
        return
    try:
        from . import firestore_service
        firestore_service.save_order_item(instance)
    except Exception:
        logger.exception('Failed to sync OrderItem to Firestore')


@receiver(post_delete, sender='b3rc_site.OrderItem')
def order_item_deleted(sender, instance, **kwargs):
    if _syncing:
        return
    try:
        from . import firestore_service
        firestore_service.delete_order_item(instance.pk)
    except Exception:
        logger.exception('Failed to delete OrderItem from Firestore')
