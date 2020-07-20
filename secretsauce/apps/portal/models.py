from django.db import models
from secretsauce.apps.account.models import User, Company
import uuid

# Create your models here.

class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField("Project Title", max_length=200, unique=True)
    description = models.TextField("Project Description", blank=True)
    cover = models.ImageField(upload_to='cover_images/', blank=True)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
    )
    owners = models.ManyToManyField(
        User,
        blank=True,
    )
    cost_sheet = models.BooleanField(default=False)

    def __str__(self):
        return "%s: %s" % (self.company, self.title)

class PredictionModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField("Model Description", blank=True)

    def __str__(self):
        return self.name

class ModelTag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    models = models.ManyToManyField(
        PredictionModel,
        related_name='model_tags',
        blank=True,
    )

    def __str__(self):
        return self.name

class DataBlock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='data_blocks'
    )
    name = models.CharField(max_length=200, unique=True)
    upload = models.FileField(upload_to='uploads/')

    def __str__(self):
        return "DataBlock: %s" % (self.name) 

class ConstraintBlock(models.Model):
    """A set of constraints"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='constraint_blocks',
    )
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return "ConstraintBlock: %s" % (self.name)

    def get_formatted_json(self):
        # TODO: Retrieve JSON formatted for GA optimizer
        pass

class Constraint(models.Model):
    """A single constraint"""

    RELATIONSHIP_CHOICES = [
        ("LT", "Strictly less than"), # 1
        ("GT", "Strictly greater than"), # 2
        ("LEQ", "Less than or equal to"),
        ("GEQ", "Greater than or equal to"),
        ("EQ", "Equal to"), # 0
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    constraint_block = models.ForeignKey(
        ConstraintBlock, 
        on_delete=models.CASCADE, 
        related_name='constraints',
    )
    name = models.CharField(max_length=500, unique=True)
    in_equality = models.CharField(max_length=3, choices=RELATIONSHIP_CHOICES)
    rhs_constant = models.FloatField()
    penalty = models.FloatField(default=0)

    def __str__(self):
        return "Constraint: %s" % (self.name)

class ConstraintParameter(models.Model):
    """A parameter in a constraint"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    constraint_block = models.ForeignKey(
        ConstraintBlock,
        on_delete=models.CASCADE,
    )
    item_id = models.IntegerField()

class ConstraintParameterRelationship(models.Model):
    """Relationship connecting Constraint and ConstraintParameter"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    constraint = models.ForeignKey(
        Constraint,
        on_delete=models.CASCADE,
        related_name='constraint_relationships'
    )
    constraint_parameter = models.ForeignKey(
        ConstraintParameter,
        on_delete=models.CASCADE,
    )
    coefficient = models.FloatField()

class DataBlockHeader(models.Model):
    data_block = models.ForeignKey(
        DataBlock,
        on_delete=models.CASCADE,
        related_name='schema',
    )
    item_id = models.IntegerField()

class Item(models.Model):
    """Item obtained from Cost Sheet"""
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='items',
    )
    name = models.CharField(max_length=200)
    item_id = models.IntegerField()
    cost = models.FloatField(blank=True)

class TrainedPredictionModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prediction_model = models.ForeignKey(
        PredictionModel,
        on_delete=models.CASCADE,
        related_name=None,
    )
    data_block = models.ForeignKey(
        DataBlock,
        on_delete=models.CASCADE,
        related_name='trained_models',
    )
    name = models.CharField(max_length=200)
    available = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    