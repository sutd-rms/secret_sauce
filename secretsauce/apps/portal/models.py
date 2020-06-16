from django.db import models
from secretsauce.apps.account.models import User, Company
import uuid

# Create your models here.

class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField("Project Title", max_length=200)
    description = models.TextField("Project Description", blank=True)
    cover = models.ImageField(upload_to='cover_images/', blank=True)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
    )
    owners = models.ManyToManyField(
        User,
    )

    def __str__(self):
        return "%s: %s" % (self.company, self.title)

class PredictionModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name

class ModelTag(models.Model):
    name = models.CharField(max_length=200)
    prediction_model = models.ManyToManyField(
        PredictionModel,
        related_name="tags"
    )
    # TODO: No repeated tags

    def __str__(self):
        return self.name

class RequiredHyperparameter(models.Model):
    """
    Required hyperparameters to train a defined PredictionModel
    """
    prediction_model = models.OneToOneField(
        PredictionModel, 
        on_delete=models.CASCADE,
        related_name='required_hyperparameters'
    )
    name = models.CharField(max_length=200)
    HYPERPARAM_TYPES = (
        ('INT', "Integer"),
        ('FP', "Floating point"),
        ('STR', "String"),
        ('CAT', "Category")
    )
    hyperparameter_type = models.CharField(max_length=3, choices=HYPERPARAM_TYPES)

    def __str__(self):
        return "%s: %s (%s)" %(self.prediction_model, self.name, self.hyperparameter_type)

class DataBlock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name="projects"
    )
    name = models.CharField(max_length=200)
    upload = models.FileField(upload_to='uploads/')

    def __str__(self):
        return "DataBlock: %s" % (self.name) 

class Weights(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prediction_model = models.ForeignKey(
        PredictionModel, 
        on_delete=models.CASCADE, 
        related_name="weights"
    )
    data_block = models.ForeignKey(
        DataBlock, 
        on_delete=models.CASCADE,
        related_name="weights"
    )
    upload = models.URLField(max_length = 200) 

    def __str__(self):
        return "Weight for %s (%s)" % (self.prediction_model, self.data_block)

class ConstraintBlock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data_block = models.ForeignKey(
        DataBlock, 
        on_delete=models.CASCADE, 
        related_name="datablocks"
    )
    constraint_block_name = models.CharField(max_length=200)

    def __str__(self):
        return "ConstraintBlock: %s" % (self.name)

class Constraint(models.Model):
    constraint_block = models.ForeignKey(
        ConstraintBlock, 
        on_delete=models.CASCADE, 
        related_name="constraints"
    )
    name = models.CharField(max_length=200)

    def __str__(self):
        return "Constraint: %s" % (self.name)
