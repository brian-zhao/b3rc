"""
Management command: load persistent Firestore data into the ephemeral SQLite DB.

Run on every GAE instance startup, before gunicorn starts.
"""
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime

from b3rc_site import firestore_service, signals
from b3rc_site.models import SiteMedia, CarouselImage


class Command(BaseCommand):
    help = 'Sync data from Firestore into the local SQLite database'

    def handle(self, *args, **options):
        # Disable Firestore write-back signals during import
        signals._syncing = True
        try:
            self._sync_site_media()
            self._sync_carousel_images()
        finally:
            signals._syncing = False

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
