# Generated by Django 3.0.6 on 2020-07-25 16:29

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0009_auto_20200725_1628'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConstraintCategory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='constraint',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='portal.ConstraintCategory'),
        ),
    ]