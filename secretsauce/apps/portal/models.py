from django.db import models

# Create your models here.

class Project(models.Model):
    title = models.CharField(max_length=200)
    organization = models.CharField(max_length=200)

class PredictionModel(models.Model):
    model_type = models.CharField(max_length=200)
    model_name = models.CharField(max_length=200)

class Hyperparameters(models.Model):
    prediction_model = models.ForeignKey(PredictionModel, on_delete=models.CASCADE)

class Weights(models.Model):
    model_type = models.ForeignKey(PredictionModel, on_delete=models.CASCADE)
    url = models.URLField(max_length = 200) 

class DataBlock(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

class ConstraintBlock(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

class Constraint(models.Model):
    constraint_block = models.ForeignKey(ConstraintBlock, on_delete=models.CASCADE)