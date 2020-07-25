# Generated by Django 3.0.6 on 2020-07-25 03:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0006_auto_20200722_1744'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='item_id',
            field=models.IntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name='datablockheader',
            unique_together={('data_block', 'item_id')},
        ),
        migrations.AlterUniqueTogether(
            name='item',
            unique_together={('project', 'item_id')},
        ),
    ]
