# Generated by Django 5.0.2 on 2024-03-07 07:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_address'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='user',
        ),
    ]
