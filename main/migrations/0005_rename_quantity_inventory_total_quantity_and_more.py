# Generated by Django 4.2.7 on 2024-06-08 08:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_contract_inventory_created_at_inventory_product_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inventory',
            old_name='quantity',
            new_name='total_quantity',
        ),
        migrations.AddField(
            model_name='contract',
            name='store',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='store_contracts', to='main.store'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inventory',
            name='available_quantity',
            field=models.PositiveIntegerField(default=50),
            preserve_default=False,
        ),
    ]
