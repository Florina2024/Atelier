# Generated by Django 5.2.1 on 2025-06-01 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0004_alter_e_product_gallery_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='h_order',
            name='session_key',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]
