# Generated by Django 3.0.6 on 2020-07-27 17:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0014_trainedpredictionmodel_cv_progress'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='price_current',
        ),
    ]
