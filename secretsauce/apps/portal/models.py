from django.db import models

# Create your models here.

class Project(models.Model):
    title = models.CharField(max_length=200)

class PredictionModel(models.Model):
    model_type = models.CharField(max_length=200)
    model_name = models.CharField(max_length=200)

class Weights(models.Model):
    model_type = models.ForeignKey(PredictionModel, on_delete=models.CASCADE)

class DataBlock(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

class ConstraintBlock(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

class Constraint(models.Model):
    constraint_block = models.ForeignKey(ConstraintBlock, on_delete=models.CASCADE)