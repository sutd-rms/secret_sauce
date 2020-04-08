from django.db import models

# Create your models here.

class Project(models.Model):
    title = models.CharField("Project Title", max_length=200)
    organization = models.CharField("Organization", max_length=200)
    # TODO: Change organization into choices

    def __str__(self):
        return "%s: %s" % (self.organization, self.title)

class PredictionModel(models.Model):
    model_name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.model_name

class ModelTag(models.Model):
    tag_name = models.CharField(max_length=200)
    prediction_model = models.ManyToManyField(
        PredictionModel,
        related_name="tags"
    )
    # TODO: No repeated tags

    def __str__(self):
        return self.tag_name

class Hyperparameters(models.Model):
    """
    Required hyperparameters to train a defined PredictionModel
    """
    prediction_model = models.ForeignKey(PredictionModel, on_delete=models.CASCADE)
    hyperparameter_name = models.CharField(max_length=200)
    HYPERPARAM_TYPES = (
        ('INT', 'Integer'),
        ('FP', 'Floating point'),
        ('STR', 'String'),
        ('CAT', 'Category')
    )
    hyperparameter_type = models.CharField(max_length=3, choices=HYPERPARAM_TYPES)

    def __str__(self):
        return "%s: %s (%s)" %(self.prediction_model, self.hyperparameter_name, self.hyperparameter_type)

class DataBlock(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    data_block_name = models.CharField(max_length=200)
    upload = models.FileField(upload_to="uploads/")

    def __str__(self):
        return "DataBlock: %s" % (self.data_block_name) 

class Weights(models.Model):
    prediction_model = models.ForeignKey(PredictionModel, on_delete=models.CASCADE)
    data_block = models.ForeignKey(DataBlock, on_delete=models.CASCADE)
    upload = models.URLField(max_length = 200) 

    def __str__(self):
        return "It's a Weight!"

class ConstraintBlock(models.Model):
    data_block = models.ForeignKey(DataBlock, on_delete=models.CASCADE)
    constraint_block_name = models.CharField(max_length=200)

    def __str__(self):
        return "ConstraintBlock: %s" % (self.constraint_block_name)

class Constraint(models.Model):
    constraint_block = models.ForeignKey(ConstraintBlock, on_delete=models.CASCADE)
    constraint_name = models.CharField(max_length=200)

    def __str__(self):
        return "Constraint: %s" % (self.constraint_name)