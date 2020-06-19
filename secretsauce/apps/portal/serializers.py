from django.contrib.auth.models import User
from rest_framework import serializers

from secretsauce.apps.portal.models import *

class DataBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataBlock
        fields = '__all__'
    
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__' 

class ConstraintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Constraint
        fields = '__all__'

class ConstraintBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstraintBlock
        fields = '__all__'

class PredictionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionModel
        fields = '__all__'
