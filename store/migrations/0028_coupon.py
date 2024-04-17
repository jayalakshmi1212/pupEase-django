# Generated by Django 5.0.3 on 2024-04-05 13:01

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0027_remove_offerproductassociation_offer_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coupon_code', models.CharField(max_length=100)),
                ('is_expired', models.BooleanField(default=False)),
                ('discount_percentage', models.IntegerField(default=10, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('minimum_amount', models.IntegerField(default=400)),
                ('max_uses', models.IntegerField(default=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('expire_date', models.DateField()),
                ('total_coupons', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
    ]
