# Generated by Django 4.2.7 on 2024-06-13 08:13

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_product_featured_until'),
    ]

    operations = [
        migrations.CreateModel(
            name='Return',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='returns', to='main.contract')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='returns', to='main.product')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='returns', to='main.store')),
            ],
        ),
    ]
