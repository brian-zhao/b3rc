from django.apps import AppConfig


class B3RcSiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'b3rc_site'

    def ready(self):
        import b3rc_site.signals  # noqa: F401 — connect signal handlers
