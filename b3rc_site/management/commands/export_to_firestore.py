"""
One-time command: push existing SQLite/PostgreSQL data into Firestore.

Run this once before switching production to Firestore, while the app
still has access to Cloud SQL data:

    python manage.py export_to_firestore

After verifying data in Firestore, this command can be deleted.
"""
from django.core.management.base import BaseCommand

from b3rc_site import firestore_service
from b3rc_site.models import SiteMedia, CarouselImage


class Command(BaseCommand):
    help = 'Export current DB data to Firestore (one-time migration)'

    def handle(self, *args, **options):
        count = 0
        for sm in SiteMedia.objects.all():
            firestore_service.save_site_media(sm)
            count += 1
        self.stdout.write(f'Exported {count} SiteMedia record(s)')

        count = 0
        for ci in CarouselImage.objects.all():
            firestore_service.save_carousel_image(ci)
            count += 1
        self.stdout.write(f'Exported {count} CarouselImage record(s)')

        self.stdout.write(self.style.SUCCESS('Done! Verify data in Firestore console.'))

        from b3rc_site.models import Post
        count = 0
        for post in Post.objects.all():
            firestore_service.save_post(post)
            count += 1
        self.stdout.write(f'Exported {count} Post record(s)')
