# Generated by Django 5.0.3 on 2024-04-09 15:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0032_alter_variation_variation_category'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grand_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date_applied', models.DateTimeField(auto_now_add=True)),
                ('coupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.coupon')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
