# Generated by Django 3.0.6 on 2020-07-22 07:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0003_auto_20200721_1046'),
    ]

    operations = [
        migrations.AddField(
            model_name='constraint',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='item',
            name='price_cap',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='item',
            name='price_current',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='item',
            name='price_floor',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
