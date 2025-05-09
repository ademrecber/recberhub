# Generated by Django 5.1.7 on 2025-04-23 20:46
from django.db import migrations
from main.utils.shortener import generate_short_code

def migrate_links(apps, schema_editor):
    Post = apps.get_model('main', 'Post')
    for post in Post.objects.all():
        if post.link and not post.link.startswith('rmp/'):
            # Uzun URL’yi original_link’e taşı
            long_url = post.link
            short_code = f"rmp/{generate_short_code()}"
            while Post.objects.filter(link=short_code).exists():
                short_code = f"rmp/{generate_short_code()}"
            post.original_link = long_url
            post.link = short_code
            post.save()

class Migration(migrations.Migration):
    dependencies = [
        ('main', '0013_post_original_link_alter_post_link'),
    ]

    operations = [
        migrations.RunPython(migrate_links),
    ]