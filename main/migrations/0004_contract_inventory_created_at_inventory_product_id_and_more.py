# Generated by Django 4.2.7 on 2024-05-27 13:49

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_inventory'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('product_quantity', models.PositiveIntegerField()),
                ('price_per_item', models.DecimalField(decimal_places=2, max_digits=10)),
                ('commission_percentage', models.DecimalField(decimal_places=2, max_digits=5)),
                ('duration', models.IntegerField(default=0)),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_date', models.DateTimeField(editable=False)),
                ('status', models.CharField(choices=[('Approved', 'Approved'), ('Pending', 'Pending'), ('Denied', 'Denied')], default='Pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.product')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seller_contracts', to='main.normaluser')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_contracts', to='main.normaluser')),
            ],
            options={
                'verbose_name': 'Contract',
                'verbose_name_plural': 'Contracts',
            },
        ),
        migrations.AddField(
            model_name='inventory',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inventory',
            name='product_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='main.product'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inventory',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inventory',
            name='store_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='main.store'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inventory',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('quantity', models.PositiveIntegerField()),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='main.contract')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='main.product')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='main.normaluser')),
            ],
            options={
                'verbose_name': 'Sale',
                'verbose_name_plural': 'Sales',
            },
        ),
        migrations.AddField(
            model_name='inventory',
            name='contract_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='main.contract'),
            preserve_default=False,
        ),
    ]
