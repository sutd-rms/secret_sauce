# Generated by Django 3.0.6 on 2020-07-25 16:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0008_auto_20200725_2008'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='constraint',
            name='category',
        ),
        migrations.DeleteModel(
            name='ConstraintCategory',
        ),
    ]