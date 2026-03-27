from django.db import models


class SiteMedia(models.Model):
    SLOT_CHOICES = [
        ('hero_bg', 'Home — Hero Background'),
        ('about_image', 'Home — About Section Image'),
        ('photo_strip_1', 'Home — Photo Strip 1 (left)'),
        ('photo_strip_2', 'Home — Photo Strip 2 (center)'),
        ('photo_strip_3', 'Home — Photo Strip 3 (right)'),
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
