# Generated by Django 5.1.7 on 2025-05-01 19:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', 'add_account_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='account_status',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='scheduled_deletion_date',
        ),
    ]
