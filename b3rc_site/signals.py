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
