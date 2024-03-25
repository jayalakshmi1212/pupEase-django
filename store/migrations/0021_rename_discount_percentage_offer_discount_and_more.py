from django.db import migrations, models
from django.utils import timezone

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0020_offer_product_offer_offercategory'),
    ]

    operations = [
        migrations.RenameField(
            model_name='offer',
            old_name='discount_percentage',
            new_name='discount',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='start_date',
        ),
        migrations.RemoveField(
            model_name='product',
            name='discounted_price',
        ),
        migrations.RemoveField(
            model_name='product',
            name='offer',
        ),
        migrations.AddField(
            model_name='offer',
            name='expires_on',
            field=models.DateTimeField(default=timezone.datetime(2024, 12, 31)),  # Set a valid default value
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='ProductOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('additional_discount', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('offer', models.ForeignKey(on_delete=models.deletion.CASCADE, to='store.offer')),
                ('product', models.ForeignKey(on_delete=models.deletion.CASCADE, to='store.product')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='offers',
            field=models.ManyToManyField(through='store.ProductOffer', to='store.offer'),
        ),
        migrations.DeleteModel(
            name='OfferCategory',
        ),
    ]
