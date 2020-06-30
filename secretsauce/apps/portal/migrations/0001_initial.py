# Generated by Django 3.0.6 on 2020-06-30 16:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Constraint',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('in_equality', models.CharField(choices=[('LEQ', 'Less than or equal to'), ('GEQ', 'Greater than or equal to'), ('EQ', 'Equal to')], max_length=3)),
                ('rhs_constant', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='ConstraintBlock',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='ConstraintParameter',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('constraint_block', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portal.ConstraintBlock')),
            ],
        ),
        migrations.CreateModel(
            name='PredictionModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200, verbose_name='Project Title')),
                ('description', models.TextField(blank=True, verbose_name='Project Description')),
                ('cover', models.ImageField(blank=True, upload_to='cover_images/')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.Company')),
                ('owners', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ModelTag',
            fields=[
                ('name', models.CharField(max_length=200, primary_key=True, serialize=False, unique=True)),
                ('prediction_model', models.ManyToManyField(related_name='model_tags', to='portal.PredictionModel')),
            ],
        ),
        migrations.CreateModel(
            name='DataBlock',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('upload', models.FileField(upload_to='uploads/')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data_blocks', to='portal.Project')),
            ],
        ),
        migrations.CreateModel(
            name='ConstraintParameterRelationship',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('coefficient', models.FloatField()),
                ('constraint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='constraint_relationships', to='portal.Constraint')),
                ('constraint_parameter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portal.ConstraintParameter')),
            ],
        ),
        migrations.AddField(
            model_name='constraintblock',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='constraint_blocks', to='portal.Project'),
        ),
        migrations.AddField(
            model_name='constraint',
            name='constraint_block',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='constraints', to='portal.ConstraintBlock'),
        ),
    ]
