"""
Management command: create a superuser and configure allauth social apps.

Used on GAE where SQLite is ephemeral and must be set up on every startup.
"""
import os

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand


# (env_prefix, provider_key, display_name)
SOCIAL_PROVIDERS = [
    ('STRAVA', 'strava', 'Strava'),
    ('GOOGLE', 'google', 'Google'),
    ('FACEBOOK', 'facebook', 'Facebook'),
]


class Command(BaseCommand):
    help = 'Create superuser and configure social auth apps from env vars'

    def handle(self, *args, **options):
        self._ensure_site()
        self._ensure_superuser()
        self._ensure_social_apps()

    def _ensure_site(self):
        domain = os.getenv('SITE_DOMAIN', 'b3rc-467810.ts.r.appspot.com')
        Site.objects.update_or_create(
            pk=1,
            defaults={'domain': domain, 'name': 'B3RC'},
        )
        self.stdout.write(f'Site configured: {domain}')

    def _ensure_superuser(self):
        User = get_user_model()
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write('Superuser already exists, skipping')
            return

        username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', '')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

        if not password:
            self.stderr.write(
                'DJANGO_SUPERUSER_PASSWORD not set, skipping superuser creation'
            )
            return

        User.objects.create_superuser(
            username=username, email=email, password=password
        )
        self.stdout.write(f'Created superuser "{username}"')

    def _ensure_social_apps(self):
        from allauth.socialaccount.models import SocialApp

        site = Site.objects.get(pk=1)

        for env_prefix, provider, name in SOCIAL_PROVIDERS:
            client_id = os.getenv(f'{env_prefix}_CLIENT_ID', '')
            client_secret = os.getenv(f'{env_prefix}_CLIENT_SECRET', '')

            if not client_id or 'PLACEHOLDER' in client_id:
                self.stdout.write(f'{name} credentials not configured, skipping')
                continue

            app, created = SocialApp.objects.update_or_create(
                provider=provider,
                defaults={
                    'name': name,
                    'client_id': client_id,
                    'secret': client_secret,
                },
            )
            app.sites.add(site)
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'{action} {name} social app')
