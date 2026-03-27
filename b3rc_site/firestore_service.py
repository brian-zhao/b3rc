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
