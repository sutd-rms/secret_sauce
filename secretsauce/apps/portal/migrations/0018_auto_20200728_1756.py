# Generated by Django 3.0.6 on 2020-07-28 09:56

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0017_auto_20200728_1548'),
    ]

    operations = [
        migrations.AddField(
            model_name='optimizer',
            name='estimated_revenue',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='optimizer',
            name='hard_violations',
            field=models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='optimizer',
            name='soft_violations',
            field=models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]