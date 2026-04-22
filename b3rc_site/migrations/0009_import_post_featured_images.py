"""
Data migration: create a BlogImage record for every Post that has a
featured_image, so existing images appear in the Blog Images admin.
"""

from django.db import migrations


def import_featured_images(apps, schema_editor):
    Post = apps.get_model('b3rc_site', 'Post')
    BlogImage = apps.get_model('b3rc_site', 'BlogImage')

    for post in Post.objects.exclude(featured_image=''):
        # Derive a caption from the post title
        caption = post.title[:200] if post.title else ''
        BlogImage.objects.get_or_create(
            image=post.featured_image.name,
            defaults={'caption': caption},
        )


def reverse_import(apps, schema_editor):
    pass  # non-destructive — leave BlogImage records in place on rollback


class Migration(migrations.Migration):

    dependencies = [
        ('b3rc_site', '0008_blogimage'),
    ]

    operations = [
        migrations.RunPython(import_featured_images, reverse_import),
    ]
