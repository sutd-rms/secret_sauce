from django.db import models

from secretsauce.apps.account.models import User, Company
from secretsauce.utils import obfuscate_upload_link

import uuid

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
        blank=True,
    )
    cost_sheet = models.BooleanField(default=False)

    class Meta:
        unique_together = ('title', 'company')

    def __str__(self):
        return "%s: %s" % (self.company, self.title)

    def get_price_bounds(self):
        price_bounds = list()
        if len(self.items.all()) == 0:
            return price_bounds
        for item in self.items.all():
            entry = dict()
            entry['item_id'] = item.item_id
            entry['min'] = item.price_floor
            entry['max'] = item.price_cap
            price_bounds.append(entry)
        return price_bounds

class PredictionModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
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
    name = models.CharField(max_length=200)
    upload = models.FileField(upload_to=obfuscate_upload_link)

    class Meta:
        unique_together = ('project', 'name')

    def __str__(self):
        return "DataBlock: %s" % (self.name) 

class ConstraintBlock(models.Model):
    """A set of constraints"""
    EQUALITY_CODES = {
        'EQ': 0,
        'LT': 1,
        'GT': 2,
        'LEQ': 3,
        'GEQ': 4,
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='constraint_blocks',
    )
    name = models.CharField(max_length=200)

    class Meta:
        unique_together = ('project', 'name')

    def __str__(self):
        return "ConstraintBlock: %s" % (self.name)

    def get_list(self):
        constraint_list = list()
        if len(self.constraints.all()) == 0:
            return constraint_list
        for constraint in self.constraints.all():
            entry = dict()
            entry['products'] = list()
            entry['scales'] = list()
            for relationship in constraint.constraint_relationships.all():
                entry['products'].append(relationship.constraint_parameter.item_id)
                entry['scales'].append(relationship.coefficient)
            entry['penalty'] = constraint.penalty
            entry['equality'] = self.EQUALITY_CODES[constraint.in_equality]
            entry['shift'] = constraint.rhs_constant
            constraint_list.append(entry)
        return constraint_list

class ConstraintCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)

class Constraint(models.Model):
    """A single constraint"""

    RELATIONSHIP_CHOICES = [
        ("LT", "Strictly less than"), # 1
        ("GT", "Strictly greater than"), # 2
        ("LEQ", "Less than or equal to"), # 3
        ("GEQ", "Greater than or equal to"), # 4
        ("EQ", "Equal to"), # 0
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    constraint_block = models.ForeignKey(
        ConstraintBlock, 
        on_delete=models.CASCADE, 
        related_name='constraints',
    )
    name = models.CharField(max_length=500)
    in_equality = models.CharField(max_length=3, choices=RELATIONSHIP_CHOICES)
    rhs_constant = models.FloatField()
    penalty = models.FloatField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        ConstraintCategory,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        unique_together = ('constraint_block', 'name')

    @property
    def equation(self):
        if len(self.constraint_relationships.all()) == 0:
            return

        eq = ""
        for relation in self.constraint_relationships.all():
            item_id = relation.constraint_parameter.item_id
            coeff = relation.coefficient
            if len(eq) > 0 and coeff > 0:
                eq += "+"
            eq += str(coeff) + "*" + "[" + str(item_id) + "]"

        return eq + self.format_in_equality + str(self.rhs_constant)
    
    @property
    def equation_name(self):
        if len(self.constraint_relationships.all()) == 0:
            return

        eq = ""
        for relation in self.constraint_relationships.all():
            item_id = relation.constraint_parameter.item_id
            try:
                item_name = Item.objects.get(project=self.constraint_block.project, item_id=item_id).name
            except Item.DoesNotExist:
                return  

            coeff = relation.coefficient
            if len(eq) > 0 and coeff > 0:
                eq += "+"
            eq += str(coeff) + "*" + "[" + str(item_name) + "]"

        return eq + self.format_in_equality + str(self.rhs_constant)

    @property
    def format_in_equality(self):
        check = self.in_equality
        if check == "LT":
            return "<"
        elif check == "GT":
            return ">"
        elif check == "LEQ":
            return "<="
        elif check == "GEQ":
            return ">="
        elif check == "EQ":
            return "="

    def __str__(self):
        return "Constraint: %s" % (self.name)

class ConstraintParameter(models.Model):
    """A parameter in a constraint"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    constraint_block = models.ForeignKey(
        ConstraintBlock,
        on_delete=models.CASCADE,
        related_name='params',
    )
    item_id = models.IntegerField()

    @property
    def item_name(self):
        if self.constraint_block.project.cost_sheet:
            try:
                return self.constraint_block.project.items.all().get(item_id=self.item_id).name
            except Item.DoesNotExist:
                pass
        return None

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

    class Meta:
        unique_together = ('data_block', 'item_id')

    @property
    def item_name(self):
        if self.data_block.project.cost_sheet:
            try:
                return self.data_block.project.items.all().get(item_id=self.item_id).name
            except Item.DoesNotExist:
                return None
        return None

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
    price_current = models.FloatField()
    price_floor = models.FloatField()
    price_cap = models.FloatField()

    class Meta:
        unique_together = ('project', 'item_id')

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
    created = models.DateTimeField(auto_now_add=True)
    pct_complete = models.FloatField(default=0)
    