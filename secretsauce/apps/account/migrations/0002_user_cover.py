# Generated by Django 3.0.6 on 2020-07-22 03:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='cover',
            field=models.ImageField(blank=True, null=True, upload_to='cover_images/'),
        ),
    ]
