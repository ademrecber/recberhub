# Generated by Django 5.1.7 on 2025-03-26 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='instagram_username',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='twitter_username',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
